# Text-to-SQL Evaluation on Real Analytics Questions

[![CI](https://github.com/prhoguns/text-to-sql-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/prhoguns/text-to-sql-eval/actions/workflows/ci.yml)

How well can a small open model that runs on a laptop turn a business question into correct SQL? This
measures it on **92 questions I had already answered by hand** across five of my analytics projects:

- Toronto police crime
- Network intrusion flows
- Industrial-control sensor data
- Bank account fraud
- Windows logons

Every question has a gold query and a real database behind it, so a generated query is graded by
**what it returns**, not by how it looks.

**Stack:** Python 3.14 · DuckDB · Ollama (Qwen2.5-Coder 3B and 7B, run locally) · pytest.

## Method

- **Questions:** the first comment line of each source query; the query is the gold answer. Notes about
  technique are kept out of the question ([`questions.py`](evalsql/questions.py)).
- **Grading:** execution accuracy ([`compare.py`](evalsql/compare.py)). The generated and gold queries run
  on the same database, and the results must hold the same rows. Row and column order and column names
  are ignored, and numbers are compared at one decimal. *Relaxed* also accepts extra columns.
- **Conditions:**
  - `schema`: tables and columns only
  - `schema+rows`: plus three example rows per table
  - `+repair`: one retry that shows the model its own DuckDB error
- **Safety:** generated SQL runs on a read-only connection with a 60-second limit, so a bad query can
  neither change the data it is graded against nor hang the run.
- **Gold answers checked first** ([`check_gold.py`](evalsql/check_gold.py)). Each gold query runs on one
  thread and again on eight, and must return identical results. This found **eight queries in the source
  repositories whose results changed from run to run**: ties under `ORDER BY ... LIMIT`, and one `NTILE`
  over tied scores. They were fixed at the source, and the corrected results committed there, before any
  model was graded.

## Results

The run is in progress on local hardware. Results will appear here and in
[`results/SUMMARY.md`](results/SUMMARY.md) once every model and condition has finished.

## Reproduce

```bash
pip install -r requirements.txt
ollama pull qwen2.5-coder:3b && ollama pull qwen2.5-coder:7b
# build the five source databases with each repository's own scripts (see datasets.toml for paths)
python -m evalsql.questions && python -m evalsql.check_gold
scripts/run_all.sh          # resumable; writes results/*.jsonl and results/SUMMARY.md
```

`pytest` covers the grading rules, SQL extraction from model replies, the read-only connection and the
query timeout. It needs no model or data.
