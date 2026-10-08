# Deviation records — V2-MPI-FULL-01 (FULL run and BRIDGE run)

**Recorded deviations: 0.** FULL: 90 / 90 scheduled cells completed, 90 attempt directories. BRIDGE: 12 / 12 cells
completed, 12 attempt directories. The harness stops on any node crash, deploy failure, unexpected rejection or
acceptance, missing trace / meter field, version or hash mismatch, interruption or duplicate (`harness/run_campaign.py`);
cell-error files found: 0 (`orchestrator.log` of each run).

Not run (not deviations): the 12 FFLONK cells (`FULL-IF-FFLONK-GATE-PASSES`) — FFLONK gate G1 not passed (published
power-19 ptau not obtainable, HTTP 403; V2-A18); the 6 SUPPORTING cells (`NOT-SCHEDULED` in C1).

Note (not a deviation): per-cell ZKsync OS L1 start states (fresh decompressions of the pinned
`local-chains/v32.0/l1-state.json.gz`) were removed from `raw/` after hashing, as in the pilot:
FULL 44 files, BRIDGE 4 files; copies not equal to the decompressed pin: 0
(`full/raw/l1-state-inputs-removed.tsv`, `bridge/raw/l1-state-inputs-removed.tsv`).

Freeze procedure: the per-run records files `full/V2-MPI-FULL-01-records.jsonl` and
`bridge/V2-MPI-FULL-01-BRIDGE-records.jsonl` are the concatenation of `cells/*.jsonl` in file order (the command of
`harness/freeze_evidence.sh`), and one `SHA256SUMS` covers every file under the campaign root.
