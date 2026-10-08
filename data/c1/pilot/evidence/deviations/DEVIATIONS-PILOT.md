# Deviation records — V2-MPI-PILOT-01

**Recorded deviations: 0.** All 36 scheduled cells completed on their first attempt (no node crash, deploy failure,
unexpected rejection or acceptance, missing trace / meter field, version or hash mismatch, interruption or duplicate).
The harness stops on any such event (`harness/run_campaign.py`); none occurred (`orchestrator.log`).

Note (not a deviation): the per-cell ZKsync OS L1 start states (fresh decompressions of the pinned
`local-chains/v32.0/l1-state.json.gz`) were removed from `raw/` after hashing; every copy equalled the decompressed pin
(`raw/l1-state-inputs-removed.json`).
