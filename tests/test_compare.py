import datetime as dt
import decimal

from evalsql.compare import compare


def test_identical():
    rows = [("a", 1, 2.5), ("b", 2, 3.5)]
    assert compare(rows, rows).strict


def test_row_and_column_order_do_not_matter():
    gold = [("a", 1), ("b", 2)]
    pred = [(2, "b"), (1, "a")]
    assert compare(gold, pred).strict


def test_rounding_to_one_decimal():
    assert compare([(37.21,)], [(37.2134,)]).strict
    assert compare([(10,)], [(10.0,)]).strict
    assert compare([(decimal.Decimal("1.50"),)], [(1.5,)]).strict


def test_percentage_is_not_a_fraction():
    assert not compare([(37.2,)], [(0.372,)]).relaxed


def test_extra_columns_only_pass_relaxed():
    m = compare([("a", 1)], [("a", 1, "extra")])
    assert m.relaxed and not m.strict


def test_missing_column_fails():
    assert not compare([("a", 1)], [("a",)]).relaxed


def test_row_count_must_match():
    assert not compare([("a",), ("b",)], [("a",)]).relaxed


def test_columns_must_pair_up_row_by_row():
    # Each column's values match as a multiset, but the rows are paired differently.
    gold = [("a", 1), ("b", 2)]
    pred = [("a", 2), ("b", 1)]
    assert not compare(gold, pred).relaxed


def test_duplicate_valued_columns_are_resolved_by_search():
    gold = [(1, 1, "x"), (2, 2, "y")]
    pred = [("x", 1, 1), ("y", 2, 2)]
    assert compare(gold, pred).strict


def test_dates_and_nulls():
    gold = [(dt.date(2024, 1, 1), None)]
    assert compare(gold, [(dt.date(2024, 1, 1), None)]).strict
    assert not compare(gold, [(dt.date(2024, 1, 2), None)]).relaxed


def test_empty_results_match():
    assert compare([], []).strict
