#!/usr/bin/env bash
# Run independently for LALIGA HYPERMOTION after matchday games have finished.
# This is a refresh script only; it does not schedule itself or publish automatically.
set -euo pipefail
cd "$(dirname "$0")"
python3 fetch_official_laliga2.py
python3 capture_official_standings.py
python3 capture_espn_crosscheck.py
python3 validate_laliga2.py
python3 build_laliga2_dashboard.py
printf '\nValidation passed; review the cutoff/live-fixture reconciliation in laliga2_2026_27_validation.txt before publishing.\n'
