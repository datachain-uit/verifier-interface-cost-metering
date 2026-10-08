# 03 — Calibration of C_env (registered Groth16 / PLONK only; no FFLONK input)

**Data.** The registered ZKsync OS v32.0 @ npg 100 (no priority fee) `computational_native` of the direct `verifyProof`
measurement of proof `j0` of c1_k01 and c1_ctx_k02, k04, k08, k12, k16, k24, k32, k64, Groth16 and PLONK (18 proofs; the
V2-M7B-A set). Records: V2-MPI-PILOT-01 (`08cc9f3a…`) and V2-MPI-FULL-01 (`c267ebe2…`); where a proof appears in both
(bridge), the values are identical. Structural records: `calibration/calibration-structural.jsonl` from
`code/c2_structural.js` (manifest `calibration/calibration-manifest.json`; frozen C1 corpus; campaign-compiled verifiers).

**Rule (fixed before the computation).** C_env(proof) = N_registered − (terms 1–9). C_env is the value common to every
calibration proof; if the 18 values were not identical, the package could not be frozen (no averaging, no fitting).

**Result** (`calibration/C2-CALIBRATION.json`): all 18 values = **1,669,012**; calibration residual 0 for every proof.
Cross-checks, all PASS for all 18 proofs: structural record = registered EVM-Osaka trace of the same proof (opcode
counts, precompile counts, keccak sizes, copies); terms 1–4 = frozen C1 trace-model components; terms 5, 6, 7, 9 = V2-M7A;
heap events = V2-M7B-A.

**Internal check (not calibration, not a C2 test)** (`calibration/C2-INTERNAL-CHECK.json`): the frozen model with
C_env = 1,669,012 applied to the other 190 registered Groth16 / PLONK proofs (j1 … j7 of the nine context-tag cells and
all 8 proofs of c1_ctx_k06, c1_a4, c1_a8, c1_disc_k04): residual **0** for every proof; directly counted heap events
per cell: Groth16 7 everywhere; PLONK 29 (k = 1, 2), 31 (k = 4 … 8 and the k = 4 / 8 anchors), 35, 39, 47, 55, 87
(k = 12, 16, 24, 32, 64).

**What the calibration establishes.** For the two calibration templates, terms 1–9 plus one constant reproduce every
registered ZKsync OS direct-call native exactly. It does not establish that C_env is template-independent beyond
Groth16 and PLONK; that is the C2 test.
