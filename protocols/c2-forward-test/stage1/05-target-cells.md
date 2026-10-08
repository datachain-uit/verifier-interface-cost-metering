# 05 — Target cells (exactly the registered FFLONK validation cells; none added)

| Environment | Cells (k) | Proofs | C2 role |
|---|---|---|---|
| ZKsync OS v32.0 @ npg 100 | c1_ff_k01, c1_ff_k04, c1_ff_k16, c1_ff_k32 | j0 … j7 each (32 direct `verifyProof` measurements) | **C2 claim**: per-proof native (C2-PRIMARY, C2-EXACT); ranking and crossover against the registered Groth16 / PLONK cells at the same k (C2-RANK, C2-XOVER) |
| EVM Osaka | same 4 | same | C1 role only. Used by C2 only as the consistency gate (registered trace = stage-2 structural record); no C2 prediction |
| EraVM v29 | same 4 | same | C1 role only; no C2 prediction |

Scope details: direct `verifyProof` measurement records only (role `measurement`, op `verify_proof_direct`), npg 100, no
priority fee. Application-path records, controls and replays are outside C2. If the FFLONK cells are never run (C1 doc 21
gate failure or DROP), C2 is reported as NOT RUN.
