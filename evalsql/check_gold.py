"""Before grading anything: every gold query must run and give the same answer every time.

Each query runs single-threaded and again on eight threads, which reorders tied rows the way a
different machine would. A gold query whose answer changes (ties under ORDER BY ... LIMIT) would
mark correct model answers wrong at random, so it is reported for fixing in its source repo.
"""

from __future__ import annotations

import json

from evalsql import db
from evalsql.questions import load
from evalsql.run import connection, schema_text

OUT = db.ROOT / "questions" / "gold_check.json"


def main() -> None:
    unstable, sizes = [], {}
    for q in load():
        con = connection(q["dataset"])
        con.execute("SET threads = 1")
        a = db.run(con, q["gold_sql"], 300)
        con.execute("SET threads = 8")
        b = db.run(con, q["gold_sql"], 300)
        con.execute("SET threads = 4")
        if a != b:  # exact, ordered comparison: the committed results/ files are ordered too
            unstable.append(q["id"])
        print(f"{q['id']:<50} {len(a):>6} rows{'  UNSTABLE' if q['id'] in unstable else ''}")
    for name in {q["dataset"] for q in load()}:
        sizes[name] = {"schema_chars": len(schema_text(name, False)), "schema_rows_chars": len(schema_text(name, True))}
    OUT.write_text(json.dumps({"unstable": unstable, "prompt_sizes": sizes}, indent=2) + "\n")
    print(f"{len(unstable)} unstable gold queries; written to {OUT.relative_to(db.ROOT)}")


if __name__ == "__main__":
    main()
