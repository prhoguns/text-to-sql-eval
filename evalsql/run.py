"""Run one model under one condition over the question set and grade every answer.

    python -m evalsql.run --model qwen2.5-coder:3b --condition schema
    python -m evalsql.run --model qwen2.5-coder:3b --condition schema+rows+repair --dataset fraud

Conditions: `schema` (tables and columns only), `schema+rows` (plus three example rows per table),
and `+repair` on either (one retry that shows the model its own DuckDB error).
Results append to results/<model>__<condition>.jsonl, so an interrupted run resumes where it stopped.
"""

from __future__ import annotations

import argparse
import json
from functools import cache

import requests

from evalsql import db, llm
from evalsql.compare import compare
from evalsql.questions import load

CONDITIONS = ["schema", "schema+repair", "schema+rows", "schema+rows+repair"]


def results_path(model: str, condition: str):
    return db.ROOT / "results" / f"{model.replace(':', '_').replace('/', '_')}__{condition}.jsonl"


@cache
def connection(name: str):
    return db.connect(db.load_datasets()[name].db)


@cache
def schema_text(name: str, rows: bool) -> str:
    return db.describe(connection(name), sample_rows=3 if rows else 0)


def execute(name: str, sql: str):
    try:
        return db.run(connection(name), sql), None
    except Exception as e:  # any failure is a graded outcome, not a crash
        return None, f"{type(e).__name__}: {str(e).splitlines()[0][:300]}"


@cache
def first_attempts(model: str, condition: str) -> dict[str, dict]:
    """Decoding is deterministic, so a +repair run's first attempt equals the plain run's answer."""
    path = results_path(model, condition)
    return {r["id"]: r for r in map(json.loads, path.read_text().splitlines())} if path.exists() else {}


def grade(q: dict, model: str, condition: str) -> dict:
    gold, gold_err = execute(q["dataset"], q["gold_sql"])
    if gold_err:
        raise RuntimeError(f"{q['id']}: gold query failed: {gold_err}")
    messages = [
        {"role": "system", "content": llm.SYSTEM},
        {"role": "user", "content": llm.user_prompt(schema_text(q["dataset"], "rows" in condition), q["question"])},
    ]
    base = None
    if condition.endswith("repair"):
        base = first_attempts(model, condition.removesuffix("+repair")).get(q["id"])
    if base and "reply" in base:
        reply = llm.Reply(base["reply"], base["seconds"], base["prompt_tokens"], base["output_tokens"])
    else:
        try:
            reply = llm.chat(model, messages)
        except requests.RequestException as e:  # a hung model is a failed answer, not a crashed run
            reply = llm.Reply(f"-- model error: {type(e).__name__}", 900.0, 0, 0)
    sql = llm.extract_sql(reply.text)
    rows, err = execute(q["dataset"], sql)
    seconds, tokens, repaired = reply.seconds, reply.output_tokens, False
    if err and condition.endswith("repair"):
        messages += [
            {"role": "assistant", "content": reply.text},
            {"role": "user", "content": llm.repair_prompt(sql, err)},
        ]
        try:
            second = llm.chat(model, messages)
        except requests.RequestException as e:
            second = llm.Reply(f"-- model error: {type(e).__name__}", 900.0, 0, 0)
        sql, repaired = llm.extract_sql(second.text), True
        rows, err = execute(q["dataset"], sql)
        seconds, tokens = seconds + second.seconds, tokens + second.output_tokens
    match = compare(gold, rows) if rows is not None else None
    return {
        "id": q["id"],
        "dataset": q["dataset"],
        "model": model,
        "condition": condition,
        "sql": sql,
        "reply": reply.text if not repaired else None,
        "error": err,
        "repaired": repaired,
        "strict": bool(match and match.strict),
        "relaxed": bool(match and match.relaxed),
        "gold_rows": len(gold),
        "pred_rows": None if rows is None else len(rows),
        "seconds": round(seconds, 2),
        "prompt_tokens": reply.prompt_tokens,
        "output_tokens": tokens,
    }


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--condition", choices=CONDITIONS, default="schema")
    p.add_argument("--dataset", action="append", help="limit to one or more datasets")
    args = p.parse_args(argv)

    out = results_path(args.model, args.condition)
    done = {json.loads(line)["id"] for line in out.read_text().splitlines()} if out.exists() else set()
    todo = [q for q in load() if q["id"] not in done and (not args.dataset or q["dataset"] in args.dataset)]
    print(f"{args.model} / {args.condition}: {len(done)} done, {len(todo)} to go -> {out.name}")
    with out.open("a") as f:
        for q in todo:
            r = grade(q, args.model, args.condition)
            f.write(json.dumps(r) + "\n")
            f.flush()
            mark = "PASS" if r["strict"] else ("pass*" if r["relaxed"] else ("ERR " if r["error"] else "fail"))
            print(f"  {mark}  {r['id']:<45} {r['seconds']:>6.1f}s")


if __name__ == "__main__":
    main()
