#!/bin/bash
# Removes per-cell copies of the pinned ZKsync OS L1 start state once the cell is complete (records the hash first).
C=$1; REF=$(gzip -dc $HOME/p0/zkos/src/local-chains/v32.0/l1-state.json.gz | sha256sum | cut -c1-64)
while true; do
  for f in $(find $C -path '*/raw/*/attempt-*/node/l1-state.json' 2>/dev/null); do
    run=$(echo $f | sed "s#$C/##; s#/raw/.*##"); slug=$(echo $f | sed "s#.*/raw/##; s#/attempt.*##")
    if [ -f $C/$run/cells/$slug.jsonl ] || [ -f $(dirname $(dirname $f))/CELL-ERROR.txt ]; then
      h=$(sha256sum $f | cut -c1-64); st=MISMATCH; [ "$h" = "$REF" ] && st=equals_decompressed_pin
      printf '%s\t%s\t%s\t%s\n' "${f#$C/$run/}" "$h" "$st" "$(stat -c %s $f)" >> $C/$run/raw/l1-state-inputs-removed.tsv; rm -f $f
    fi
  done
  [ -f $C/RUNNER-STATUS ] && [ -z "$(find $C -name l1-state.json 2>/dev/null)" ] && break
  sleep 60
done
