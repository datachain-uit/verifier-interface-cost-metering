#!/bin/bash
# V2-MPI-FULL-01 post-collection: deviation records, freeze (records concatenation per run root, root SHA256SUMS),
# validation on a writable copy. Run only after RUNNER-STATUS = ALL-DONE and the janitor has exited.
set -eu
E=$HOME/full/V2-MPI-FULL-01; cd $E
[ "$(cat RUNNER-STATUS)" = ALL-DONE ] || { echo "runner not done"; exit 1; }
pgrep -f '[j]anitor.sh' >/dev/null && { echo "janitor still running"; exit 1; }
[ -f full/COLLECTION-COMPLETE ] && [ -f bridge/COLLECTION-COMPLETE ] || { echo "collection-complete markers missing"; exit 1; }
for R in full bridge; do
  n_att=$(find $R/raw -maxdepth 2 -name 'attempt-*' | wc -l); n_cells=$(ls $R/cells/*.jsonl | wc -l); n_err=$(find $R/raw -name CELL-ERROR.txt | wc -l)
  mm=$(awk -F'\t' '$3!="equals_decompressed_pin"' $R/raw/l1-state-inputs-removed.tsv 2>/dev/null | wc -l); nl=$(wc -l < $R/raw/l1-state-inputs-removed.tsv 2>/dev/null || echo 0)
  echo "$R cells=$n_cells attempts=$n_att cell_errors=$n_err l1_state_removed=$nl mismatches=$mm"
done
mkdir -p deviations
FA=$(find full/raw -maxdepth 2 -name 'attempt-*' | wc -l); FC=$(ls full/cells/*.jsonl | wc -l); BA=$(find bridge/raw -maxdepth 2 -name 'attempt-*' | wc -l); BC=$(ls bridge/cells/*.jsonl | wc -l)
FE=$(find full/raw bridge/raw -name CELL-ERROR.txt | wc -l)
FL=$(wc -l < full/raw/l1-state-inputs-removed.tsv); BL=$(wc -l < bridge/raw/l1-state-inputs-removed.tsv)
FM=$(awk -F'\t' '$3!="equals_decompressed_pin"' full/raw/l1-state-inputs-removed.tsv bridge/raw/l1-state-inputs-removed.tsv | wc -l)
cat > deviations/DEVIATIONS-FULL.md <<MD
# Deviation records — V2-MPI-FULL-01 (FULL run and BRIDGE run)

**Recorded deviations: $FE.** FULL: $FC / 90 scheduled cells completed, $FA attempt directories. BRIDGE: $BC / 12 cells
completed, $BA attempt directories. The harness stops on any node crash, deploy failure, unexpected rejection or
acceptance, missing trace / meter field, version or hash mismatch, interruption or duplicate (\`harness/run_campaign.py\`);
cell-error files found: $FE (\`orchestrator.log\` of each run).

Not run (not deviations): the 12 FFLONK cells (\`FULL-IF-FFLONK-GATE-PASSES\`) — FFLONK gate G1 not passed (published
power-19 ptau not obtainable, HTTP 403; V2-A18); the 6 SUPPORTING cells (\`NOT-SCHEDULED\` in C1).

Note (not a deviation): per-cell ZKsync OS L1 start states (fresh decompressions of the pinned
\`local-chains/v32.0/l1-state.json.gz\`) were removed from \`raw/\` after hashing, as in the pilot:
FULL $FL files, BRIDGE $BL files; copies not equal to the decompressed pin: $FM
(\`full/raw/l1-state-inputs-removed.tsv\`, \`bridge/raw/l1-state-inputs-removed.tsv\`).

Freeze procedure: the per-run records files \`full/V2-MPI-FULL-01-records.jsonl\` and
\`bridge/V2-MPI-FULL-01-BRIDGE-records.jsonl\` are the concatenation of \`cells/*.jsonl\` in file order (the command of
\`harness/freeze_evidence.sh\`), and one \`SHA256SUMS\` covers every file under the campaign root.
MD
cat deviations/DEVIATIONS-FULL.md
cat $(ls full/cells/*.jsonl | sort) > full/V2-MPI-FULL-01-records.jsonl
cat $(ls bridge/cells/*.jsonl | sort) > bridge/V2-MPI-FULL-01-BRIDGE-records.jsonl
find . -type f ! -name SHA256SUMS | sort | xargs sha256sum > SHA256SUMS
chmod -R a-w . 2>/dev/null || true
sha256sum SHA256SUMS; wc -l < SHA256SUMS
