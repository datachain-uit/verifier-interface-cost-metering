# 04 — Prediction procedure (pre-registered two-stage procedure)

The concrete d = 11 FFLONK verifier is needed for two structural inputs that cannot be known without it (bytecode length;
opcode, memory and precompile structure of its execution). C2 therefore uses two stages. **No FFLONK cost is read, computed
or printed before the stage-2 numeric predictions are frozen.**

## Stage 1 — now (this package, frozen)

Model form and all source constants (`02`), C_env (`03`), the structural tool, the prediction and scoring code (`code/`),
target cells (`05`), tolerance, criteria and falsifiers (`06`), relation to H8 (`07`), deviations policy (`08`).
Stage-1 structural expectations from the snarkjs 0.7.5 template and the C1 template table (checked, not scored, at stage 2):
5 ecMul + 7 ecAdd + 1 pairing call with 2 pairs (13 precompile calls); calldata 772 + 32k bytes; no EXP; one
CALLDATACOPY.

## Stage 2 — after the C1 doc-21 gates, before any FFLONK measurement

S2.1 **Artifact production** (C1 doc 21 / AMD-FF-1, unchanged): local power-19 research ptau; FFLONK setup for
c1_ff_k01, c1_ff_k04, c1_ff_k16, c1_ff_k32 from the frozen R1CS; vkey and verifier export; compilation by the registered
compile pipeline (solc 0.8.20; zksolc for EraVM); 8 proofs per circuit from the frozen corpus inputs; off-chain verification
(G3). Setup and proving durations are never evidence.
S2.2 **Structural derivation**: `code/c2_structural.js` on the 32 FFLONK proofs (manifest: proof_id
`c1_ff_kNN/fflonk/jJ`, the registered compiled artifact, the corpus proof file), EDR osaka with the registered network
configuration. It writes only the structural record (no gas, gasUsed or gasCost). Run once; a rerun only after a crash,
recorded.
S2.3 **Gates** (`code/c2_predict.py`): exactly 4 k × 8 proofs; status 1 and verifyProof true for every record; no
unknown term (`02`, gate rule). A failed gate is recorded before measurement; the model is not changed.
S2.4 **Numeric predictions** (`code/c2_predict.py`): per proof N̂ and [N̂(1 − τ), N̂(1 + τ)]; per k the mean N̂; ranking
predictions against the registered Groth16 and PLONK ZKsync OS cell means at the same k (determinate only if
|N̂_F mean − N_X mean| > τ · N̂_F mean + half-range of the registered X cell; otherwise INDETERMINATE, not scored);
crossover prediction = the sign sequence over k ∈ {1, 4, 16, 32} (a sign change between consecutive determinate k
defines the predicted interval, else "none within the grid").
S2.5 **Freeze**: the stage-2 directory (`research/csi/protocols/v2/V2-C2-stage2/`: manifest, structural records,
`C2-STAGE2-PREDICTIONS.json/.csv`, tool versions, artifact hashes) gets `SHA256SUMS` and a UTC freeze record, is copied to
the Mac and recorded in the decision log **before** any registered FFLONK cell runs.

## Stage 3 — measurement

The 12 registered FFLONK cells run with the registered C1 harness (unchanged). C2 adds nothing to the measurement.

## Stage 4 — scoring

C1 / H8 with the frozen C1 scorer (unchanged). C2 with `code/c2_score.py`: stage-2 `SHA256SUMS` re-verified; consistency
gate (registered EVM-Osaka trace of every FFLONK proof = its stage-2 structural record); scores per `06`. The two are
reported separately.

## Allowed and forbidden inputs

Allowed for stage-2 predictions: the stage-1 package; the FFLONK artifacts and proofs; the stage-2 structural records;
the registered Groth16 / PLONK ZKsync OS natives (ranking comparators only). Forbidden: any FFLONK EVM gas, EraVM or ZKsync
OS value (d = 11 or P0 / self-test depth 0); any change of a term, constant, τ or rule after the stage-1 freeze.
Transparency note: EVM gas is a deterministic function of the structural record; C2 neither computes it nor makes an EVM
claim, and the C1 FFLONK EVM predictions were frozen in C1 on 2026-10-04.
