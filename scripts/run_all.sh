#!/usr/bin/env bash
# Every model under every condition. Plain conditions run first so the +repair runs can reuse
# their first attempts. Resumable: rerun after an interruption and it continues.
set -euo pipefail
cd "$(dirname "$0")/.."
MODELS=${MODELS:-"qwen2.5-coder:3b qwen2.5-coder:7b"}
for model in $MODELS; do
  for condition in schema schema+rows schema+repair schema+rows+repair; do
    python -m evalsql.run --model "$model" --condition "$condition"
  done
done
python -m evalsql.report
