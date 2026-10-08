# Deviations — V2-MPI-FULL-01-FFLONK (registered FFLONK cells, campaign FULL-IF-FFLONK-GATE-PASSES)

Measurement deviations (C1 `20-deviations-policy.md`): **none**. 12 / 12 cells completed at attempt 1; no CELL-ERROR;
no retry; harness unchanged (`HARNESS-SHA256SUMS` 02cee61b…3d36).

Procedural notes recorded before the run (not measurement deviations):
- **DEV-FF-2** (AMD-FF-1): the frozen `make_manifest.py` checks verifier sources against C1 `CIRCUITS.csv`, which has no
  FFLONK rows. The FFLONK compiled artifacts are therefore passed with `--compiled compiled-fflonk/` (outside the
  manifest's `compiled/` glob; `RUN-MANIFEST-FULL-IF-FFLONK-GATE-PASSES.json` lists `compiled = {}`); their expected
  hashes are those of AMD-FF-1 and were checked before the run (`PRE-RUN-FFLONK-INPUTS.sha256`).
- FFLONK proofs come from AMD-FF-1 (`--proofs proofs-fflonk/`, copies of the transferred corpus proofs; 32 / 32 equal
  `TRANSFER-SHA256SUMS` `67e46cc3…3953`). The registered harness reads `<proofs>/<circuit>/fflonk-jJ.json` exactly as for
  the frozen Groth16 / PLONK corpus.
- Order: C2 stage 2 frozen 2026-10-05T05:21:34Z and recorded (V2-D-47) before the first cell (05:24:02Z).
