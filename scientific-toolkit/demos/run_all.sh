#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p demos/out
for d in audit revue doublons catalogue recherche; do
  echo
  echo "▶ demos/demo_$d.py"
  python3 "demos/demo_$d.py" || echo "  (échec de la démo $d)"
done
echo
echo "▶ tests"
python3 -m unittest discover -s tests 2>&1 | tail -3
