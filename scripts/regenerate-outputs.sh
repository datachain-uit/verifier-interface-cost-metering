#!/usr/bin/env bash
# Level 2 (deterministic regeneration) of the reported values, data tables, Tables 1-3, Tables S1-S25 and Figs. 2-5
# from the frozen packages of this artifact.
#   --check (default)  regenerate and require byte-identical outputs; values and tables are compared in memory, figures
#                      are rebuilt in place and compared with figures/FIGURES-MANIFEST.json
#   --write            regenerate and overwrite generated/, tables/ and figures/ (Figs. 2-5 and the figure manifest)
# Environment: see environment/README.md (Python 3.10, reference 3.10.12; matplotlib 3.10.9; Liberation Sans 2.1.5; poppler-utils).
# The values derivation also re-hashes every file of every frozen package it uses (--deep).
set -euo pipefail
cd "$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
case "${1:---check}" in
  --check) c=--check ;;
  --write) c= ;;
  *) echo "usage: $0 [--check|--write]" >&2; exit 2 ;;
esac
mkdir -p generated tables/supplement figures
python3 analysis/derive_values.py --deep $c
python3 analysis/tables/src/make_tables.py $c
python3 analysis/supplement/src/make_supplement_tables.py $c
python3 analysis/figures/src/build_figures.py $c
echo "LEVEL 2 (${1:---check}): done"
