import duckdb
import pytest

from evalsql import db, llm
from evalsql.questions import parse


@pytest.fixture
def small_db(tmp_path):
    path = tmp_path / "t.duckdb"
    con = duckdb.connect(str(path))
    con.execute("CREATE TABLE t AS SELECT range AS id, range % 3 AS grp FROM range(100)")
    con.execute("CREATE VIEW v AS SELECT grp, count(*) AS n FROM t GROUP BY grp")
    con.close()
    return path


def test_connection_is_read_only(small_db):
    con = db.connect(small_db)
    with pytest.raises(duckdb.Error):
        db.run(con, "DROP TABLE t")
    assert db.run(con, "SELECT count(*) FROM t") == [(100,)]


def test_runaway_query_is_stopped(small_db):
    con = db.connect(small_db)
    with pytest.raises(db.QueryTimeout):
        db.run(con, "SELECT count(*) FROM range(1000000000) a, range(1000000000) b", timeout_s=1)


def test_describe_lists_tables_views_and_samples(small_db):
    text = db.describe(db.connect(small_db), sample_rows=2)
    assert "CREATE TABLE t (\n  id BIGINT,\n  grp BIGINT\n);" in text
    assert "CREATE VIEW v" in text
    assert "2 example rows from t" in text


@pytest.mark.parametrize(
    "reply, sql",
    [
        ("```sql\nSELECT 1;\n```", "SELECT 1"),
        ("Here you go:\n```SQL\nSELECT 2\n```\nThis counts rows.", "SELECT 2"),
        ("```sql\nSELECT 1\n```\nFixed:\n```sql\nSELECT 3\n```", "SELECT 3"),
        ("SELECT 4;", "SELECT 4"),
    ],
)
def test_extract_sql(reply, sql):
    assert llm.extract_sql(reply) == sql


def test_parse_keeps_technique_notes_out_of_the_question(tmp_path):
    f = tmp_path / "07_x.sql"
    f.write_text("-- Q7. Which areas have the highest rate?\n-- Technique: UNION ALL of two LIMITs.\nselect 1;\n")
    question, gold = parse(f)
    assert question == "Which areas have the highest rate?"
    assert gold == "select 1;"
