#!/usr/bin/env bash
# Regenerate the PLONK proving keys classified REGENERABLE (provenance/REGENERABLE.tsv) with the pinned snarkjs 0.7.5
# and validate each against its frozen SHA-256. Keys are written to a work directory outside the artifact; add
# --place to copy validated keys to their published paths. See scripts/regenerate_keys.py --help.
set -euo pipefail
exec python3 "$(cd "$(dirname "$0")" && pwd)/regenerate_keys.py" "$@"
