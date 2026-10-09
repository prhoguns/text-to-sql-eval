"""Prompting a local model through Ollama's chat API and pulling the SQL out of its reply."""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass

import requests

OLLAMA = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

SYSTEM = (
    "You translate questions into DuckDB SQL for the database described below. "
    "Reply with exactly one read-only SELECT (CTEs allowed) inside a ```sql code block and nothing else. "
    "Use only the tables, views and columns listed."
)


def user_prompt(schema: str, question: str) -> str:
    return f"Database:\n\n{schema}\n\nQuestion: {question}"


def repair_prompt(sql: str, error: str) -> str:
    return (
        f"That query failed in DuckDB:\n\n{error}\n\n"
        f"Return a corrected query in a ```sql block.\n\nFailed query:\n{sql}"
    )


_FENCE = re.compile(r"```(?:sql|duckdb)?\s*\n(.*?)```", re.S | re.I)


def extract_sql(reply: str) -> str:
    """The last fenced block if there is one, else the reply itself; trailing semicolons removed."""
    blocks = _FENCE.findall(reply)
    sql = blocks[-1] if blocks else reply
    return sql.strip().rstrip(";").strip()


@dataclass
class Reply:
    text: str
    seconds: float
    prompt_tokens: int
    output_tokens: int


def chat(model: str, messages: list[dict], num_ctx: int = 4096) -> Reply:
    t = time.perf_counter()
    r = requests.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
            # Deterministic decoding, so a rerun reproduces the same queries.
            "options": {"temperature": 0, "seed": 7, "num_ctx": num_ctx},
        },
        timeout=900,
    )
    r.raise_for_status()
    body = r.json()
    return Reply(
        text=body["message"]["content"],
        seconds=time.perf_counter() - t,
        prompt_tokens=body.get("prompt_eval_count", 0),
        output_tokens=body.get("eval_count", 0),
    )
