#!/bin/bash
# V2-C1 registered harness — freeze an evidence tree: combined records file (cell order) + SHA256SUMS over every file.
set -eu; R=$1; CID=$2; cd $R
cat $(ls cells/*.jsonl | sort) > $CID-records.jsonl
find . -type f ! -name SHA256SUMS | sort | xargs sha256sum > SHA256SUMS
chmod -R a-w . 2>/dev/null || true
sha256sum SHA256SUMS
