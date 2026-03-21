#!/usr/bin/env bash
# safe-gog test harness runner
# Usage:
#   ./run.sh                    — run all available test cases
#   ./run.sh --risk 1E          — run one risk type only
#   ./run.sh --tc TC-3A-001     — run a single case
#   ./run.sh -v                 — verbose (all results)
#   ./run.sh -f                 — failures only
set -e
cd "$(dirname "$0")"
python3 runner.py "$@"
