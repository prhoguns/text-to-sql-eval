"""Read-only access to the five analytics databases, with a time limit per query."""

from __future__ import annotations

import os
import threading
import tomllib
from dataclasses import dataclass
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Dataset:
    name: str
    title: str
    db: Path
    sql_dir: Path


def load_datasets(config: Path = ROOT / "datasets.toml") -> dict[str, Dataset]:
    """Paths come from datasets.toml (sibling checkouts); EVALSQL_DB_<NAME> / EVALSQL_SQL_<NAME> override them."""
    raw = tomllib.loads(config.read_text())
    out = {}
    for name, d in raw.items():
        db = os.getenv(f"EVALSQL_DB_{name.upper()}", d["db"])
        sql = os.getenv(f"EVALSQL_SQL_{name.upper()}", d["sql_dir"])
        out[name] = Dataset(name, d["title"], (ROOT / db).resolve(), (ROOT / sql).resolve())
    return out


def connect(path: Path) -> duckdb.DuckDBPyConnection:
    # read_only: a generated query can never change the data it is graded against.
    con = duckdb.connect(str(path), read_only=True)
    con.execute("SET threads = 4")
    return con


class QueryTimeout(Exception):
    pass


def run(con: duckdb.DuckDBPyConnection, sql: str, timeout_s: float = 60.0) -> list[tuple]:
    timer = threading.Timer(timeout_s, con.interrupt)
    timer.start()
    try:
        return con.execute(sql).fetchall()
    except duckdb.InterruptException as e:
        raise QueryTimeout(f"query exceeded {timeout_s:.0f}s") from e
    finally:
        timer.cancel()


def describe(con: duckdb.DuckDBPyConnection, sample_rows: int = 0) -> str:
    """Schema as CREATE-style text, the form models see most in training; optionally a few rows each."""
    objects = con.execute(
        "SELECT table_name, table_type FROM information_schema.tables "
        "WHERE table_schema = 'main' ORDER BY table_type, table_name"
    ).fetchall()
    parts = []
    for name, kind in objects:
        cols = con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = 'main' AND table_name = ? ORDER BY ordinal_position",
            [name],
        ).fetchall()
        noun = "VIEW" if kind == "VIEW" else "TABLE"
        body = ",\n".join(f"  {c} {t}" for c, t in cols)
        part = f"CREATE {noun} {name} (\n{body}\n);"
        if sample_rows:
            rows = con.execute(f'SELECT * FROM "{name}" USING SAMPLE {sample_rows} ROWS (reservoir, 7)').fetchall()
            header = " | ".join(c for c, _ in cols)
            lines = "\n".join(" | ".join("NULL" if v is None else str(v) for v in r) for r in rows)
            part += f"\n/* {sample_rows} example rows from {name}:\n{header}\n{lines}\n*/"
        parts.append(part)
    return "\n\n".join(parts)
