# V2-C2 engineering tests (stage 1; no FFLONK data; cloud workspace, 2026-10-05)

| # | Test | Result |
|---|---|---|
| ET1 | `c2_structural.js` on the 18 calibration proofs: records equal the registered EVM-Osaka traces (opcode counts, precompile counts, keccak sizes, copies); heap events equal V2-M7B-A | PASS 18 / 18 (`../calibration/C2-CALIBRATION.json`, cross-checks) |
| ET2 | `c2_model.py` terms 1–4 = frozen C1 trace-model components; terms 5, 6, 7, 9 = V2-M7A | PASS 18 / 18 |
| ET3 | calibration rule: one common C_env | 1,669,012 for all 18; residual 0 |
| ET4 | internal check on 190 non-calibration Groth16 / PLONK proofs | residual 0 for all 190 (`../calibration/C2-INTERNAL-CHECK.json`) |
| ET5 | `c2_predict.py` with C2_ENGINEERING_TEST=1 on a pseudo-target of identical shape (PLONK c1_k01 / k04 / k16 / k32, j0 … j7) | gates pass; predictions written (`stage2-pseudo-target/`); ranking vs Groth16 predicts the known crossover between k = 1 and 4 |
| ET6 | `c2_score.py` on ET5 (freeze by SHA256SUMS, then score) | C2-PRIMARY PASS, C2-EXACT PASS, ranking 4 / 4 MATCH, crossover MATCH (`score-pass/`) |
| ET7 | negative control: one registered native perturbed by +5,400 (0.0140 %) | C2-PRIMARY FAIL, C2-EXACT FAIL (`score-negative/`) — the falsifier can fire |
| ET8 | tamper control: stage-2 prediction file edited after its SHA256SUMS | scoring refused ("stage-2 file changed after freeze") |

ET5–ET8 use non-FFLONK data and are labelled ENGINEERING TEST in every output; they are not C2 results.
