#!/usr/bin/env bash
# Run the A-Mem baseline on LoCoMo. Any extra arguments are passed through.
#   bash scripts/run_baseline.sh                                  # all 10 conversations, qwen2.5:3b
#   bash scripts/run_baseline.sh --set max_samples=1              # quick test on 1 conversation
#   bash scripts/run_baseline.sh --config configs/amem_llama3.2-3b.json
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ " $* " != *" --config "* ]]; then
  set -- --config configs/amem_qwen2.5-3b.json "$@"
fi
python -m harness.run_locomo "$@"
