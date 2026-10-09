"""Summarise every results/*.jsonl into results/SUMMARY.md and results/accuracy.png."""

from __future__ import annotations

import json
import re
import statistics
from collections import Counter, defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from evalsql.db import ROOT  # noqa: E402
from evalsql.questions import load  # noqa: E402

RESULTS = ROOT / "results"
ORDER = ["schema", "schema+repair", "schema+rows", "schema+rows+repair"]


def failure_kind(r: dict) -> str | None:
    if r["strict"]:
        return None
    if r["relaxed"]:
        return "right rows, extra columns"
    err = r["error"] or ""
    if err.startswith("QueryTimeout"):
        return "timed out"
    if "Parser Error" in err:
        return "SQL syntax"
    if "Binder Error" in err or "Catalog Error" in err:
        return "unknown table/column"
    if err:
        return "other runtime error"
    if r["pred_rows"] != r["gold_rows"]:
        return "wrong number of rows"
    return "wrong values"


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "–"


def main() -> None:
    runs = defaultdict(list)
    for path in sorted(RESULTS.glob("*.jsonl")):
        for r in map(json.loads, path.read_text().splitlines()):
            runs[(r["model"], r["condition"])].append(r)
    if not runs:
        raise SystemExit("no results yet")
    questions = {q["id"]: q for q in load()}
    datasets = sorted({q["dataset"] for q in questions.values()})
    keys = sorted(runs, key=lambda k: (k[0], ORDER.index(k[1])))

    out = [
        "# Results",
        "",
        f"{len(questions)} questions across {len(datasets)} databases. "
        "Execution accuracy: the generated query returns the same rows as the gold query "
        "(row and column order ignored, numbers compared at one decimal). Relaxed also accepts extra columns.",
        "",
    ]
    out += [
        "| model | condition | answered | strict | relaxed | ran without error | median s/question |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for k in keys:
        rs = runs[k]
        n = len(rs)
        out.append(
            f"| {k[0]} | {k[1]} | {n} | **{pct(sum(r['strict'] for r in rs), n)}** | "
            f"{pct(sum(r['relaxed'] for r in rs), n)} | {pct(sum(not r['error'] for r in rs), n)} | "
            f"{statistics.median(r['seconds'] for r in rs):.1f} |"
        )

    out += [
        "",
        "## By database (strict)",
        "",
        "| model | condition | " + " | ".join(datasets) + " |",
        "|---|---|" + "---:|" * len(datasets),
    ]
    for k in keys:
        cells = []
        for d in datasets:
            rs = [r for r in runs[k] if r["dataset"] == d]
            cells.append(pct(sum(r["strict"] for r in rs), len(rs)))
        out.append(f"| {k[0]} | {k[1]} | " + " | ".join(cells) + " |")

    out += [
        "",
        "## Why answers failed",
        "",
        "| model | condition | "
        + " | ".join(
            kinds := [
                "unknown table/column",
                "SQL syntax",
                "other runtime error",
                "timed out",
                "wrong number of rows",
                "wrong values",
                "right rows, extra columns",
            ]
        )
        + " |",
        "|---|---|" + "---:|" * len(kinds),
    ]
    for k in keys:
        c = Counter(failure_kind(r) for r in runs[k])
        out.append(f"| {k[0]} | {k[1]} | " + " | ".join(str(c[x]) for x in kinds) + " |")

    solved = defaultdict(int)
    for rs in runs.values():
        for r in rs:
            solved[r["id"]] += r["strict"]
    attempted_everywhere = {i for i in questions if all(any(r["id"] == i for r in rs) for rs in runs.values())}
    never = [i for i in questions if i in attempted_everywhere and solved.get(i, 0) == 0]
    out += ["", f"## Questions no configuration answered ({len(never)})", ""]
    out += [f"- `{i}`: {questions[i]['question']}" for i in never]
    (RESULTS / "SUMMARY.md").write_text("\n".join(out) + "\n")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    models = sorted({k[0] for k in keys})
    width = 0.8 / len(models)
    for i, m in enumerate(models):
        vals = [
            100 * sum(r["strict"] for r in runs[(m, c)]) / len(runs[(m, c)]) if (m, c) in runs else 0 for c in ORDER
        ]
        ax.bar([x + i * width for x in range(len(ORDER))], vals, width, label=m)
    ax.set_xticks([x + width * (len(models) - 1) / 2 for x in range(len(ORDER))], ORDER)
    ax.set(ylabel="Execution accuracy (%)", ylim=(0, 100), title="Text-to-SQL on 92 real analytics questions")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "accuracy.png", dpi=150)
    print(re.sub(r"\*\*", "", "\n".join(out[: 4 + len(keys) + 2])))


if __name__ == "__main__":
    main()
