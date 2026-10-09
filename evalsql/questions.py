"""Build questions/questions.jsonl from the source repositories' SQL files.

Each source query starts with a comment holding the plain-English question; the query itself is
the gold answer. Any further comment lines (such as "-- Technique: ...") describe how the query
was written, so they are kept out of the question the model sees.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from evalsql.db import ROOT, load_datasets

OUT = ROOT / "questions" / "questions.jsonl"


def parse(path: Path) -> tuple[str, str]:
    lines = path.read_text().strip().splitlines()
    question = re.sub(r"^--\s*(Q\d+\.\s*)?", "", lines[0]).strip()
    gold = "\n".join(line for line in lines[1:] if not line.lstrip().startswith("--")).strip()
    return question, gold


def main() -> None:
    rows = []
    for ds in load_datasets().values():
        files = sorted(ds.sql_dir.glob("*.sql"))
        if not files:
            sys.exit(f"{ds.name}: no SQL files in {ds.sql_dir}")
        for f in files:
            question, gold = parse(f)
            rows.append({"id": f"{ds.name}/{f.stem}", "dataset": ds.name, "question": question, "gold_sql": gold})
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"{len(rows)} questions -> {OUT.relative_to(ROOT)}")


def load() -> list[dict]:
    return [json.loads(line) for line in OUT.read_text().splitlines()]


if __name__ == "__main__":
    main()
