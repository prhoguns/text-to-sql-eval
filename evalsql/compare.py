"""Execution accuracy: does the model's query return the same answer as the gold query?

Two queries match when their result sets hold the same rows, ignoring row order, column order and
column names. Numbers are compared after rounding to one decimal, so 37.21 and 37.2134 agree but
37.2 and 0.372 (a percentage against a fraction) do not. `relaxed` also accepts extra columns.
"""

from __future__ import annotations

import datetime as dt
import decimal
from collections import Counter
from dataclasses import dataclass

Rows = list[tuple]


def canon(v):
    """One comparable form per value."""
    if v is None:
        return None
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, decimal.Decimal):
        v = float(v)
    if isinstance(v, float):
        if v != v:  # NaN
            return "nan"
        r = round(v, 1)
        return int(r) if r.is_integer() else r
    if isinstance(v, int):
        return v
    if isinstance(v, dt.datetime):
        return v.isoformat(sep=" ")
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, dt.timedelta):
        return v.total_seconds()
    return str(v).strip()


def _columns(rows: Rows, width: int) -> list[Counter]:
    return [Counter(canon(r[i]) for r in rows) for i in range(width)]


def _project(rows: Rows, cols: tuple[int, ...]) -> Counter:
    return Counter(tuple(canon(r[i]) for i in cols) for r in rows)


@dataclass(frozen=True)
class Match:
    strict: bool  # same rows, same number of columns
    relaxed: bool  # same rows; the prediction may carry extra columns


def compare(gold: Rows, pred: Rows) -> Match:
    if len(gold) != len(pred):
        return Match(False, False)
    if not gold:
        return Match(True, True)
    gw, pw = len(gold[0]), len(pred[0])
    if pw < gw:
        return Match(False, False)
    gcols, pcols = _columns(gold, gw), _columns(pred, pw)
    # A gold column can only map to a predicted column holding the same multiset of values.
    candidates = [[j for j in range(pw) if pcols[j] == gcols[i]] for i in range(gw)]
    if any(not c for c in candidates):
        return Match(False, False)
    target = _project(gold, tuple(range(gw)))

    def search(i: int, used: tuple[int, ...]) -> bool:
        if i == gw:
            return _project(pred, used) == target
        return any(search(i + 1, (*used, j)) for j in candidates[i] if j not in used)

    found = search(0, ())
    return Match(strict=found and pw == gw, relaxed=found)
