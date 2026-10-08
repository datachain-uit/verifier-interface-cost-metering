#!/usr/bin/env bash
# Level 1 (integrity): classify every object of the artifact and check every frozen package manifest.
# Outcomes per object: PRESENT HASH-MATCH, WITHHELD, REGENERABLE, EXTERNAL-PIN, GIT-LFS-PENDING, ERROR.
# Exit code 0 = no ERROR. Options: --quiet, --report FILE (JSON). Requires python3 (standard library only).
set -euo pipefail
exec python3 "$(cd "$(dirname "$0")" && pwd)/verify_artifact.py" "$@"
