# Hand review of failed answers

Execution accuracy is strict: an answer counts only if it returns the same rows as the gold query. To see
how much that strictness costs, I classified a random sample (seed 11) of 25 failed answers from
**qwen2.5-coder:3b, schema+rows** by reading the question, the gold query and result, and the model's
query and result.

| Class | Count | What it means |
|---|---:|---|
| Defensible answer, rejected by strict grading | 4 | The answer is right for a reasonable reading of the question, but the shape differs from the gold: a fraction where the gold has a percentage, an overall figure where the gold breaks it down, the top hour where the gold lists twenty |
| Invented data values | 6 | Filters on values that do not exist, such as `status = 'Failed'` (failures are event ID 4625), or assumes benign flows have a NULL label (they are labelled `Benign`). The query runs and returns nothing, or the wrong thing |
| SQL error | 4 | Columns not in the GROUP BY, a column that is not in scope, a two-argument COUNT |
| Wrong logic | 11 | Share of fraud instead of fraud rate, no bucketing for a "gradient", the wrong column, unpivoted rows counted as readings |

## The four defensible answers

| Question | Model's answer | Why strict grading rejected it |
|---|---|---|
| `identity/05` What share of logons is remote? | 0.828 (exactly right) | Gold also reports failure rates for remote and local, which the question does not ask for |
| `identity/18` How complete are the user, source, destination and logon fields? | 0 missing in every field (right) | Gold reports per day |
| `network/04` Which hours carry the highest attack volume? | 2018-02-14 02:00, 120,348 attacks (the gold's top row) | Gold lists the top 20 hours with shares |
| `fraud/16` How does fraud rate drift by application source? | The right 16 rows, as fractions | Gold uses percentages and adds counts |

## What it means for the scores

About one failure in six was a defensible answer. Applied to this run, strict execution accuracy
undercounts by roughly 15 questions out of 92. That is a sample estimate, not a re-grade. The larger
lesson is the second row: small models write plausible SQL against values they have never seen. Three
example rows per table are not enough to show that failures are an event ID rather than a status
string.

In a reporting tool this is what matters most: an invented filter returns an empty or partial result
that looks like an answer.
