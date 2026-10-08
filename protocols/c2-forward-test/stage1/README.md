# V2-C2 — prospective held-out FFLONK forward test (stage 1, FROZEN before any d = 11 FFLONK artifact or evidence)

Status: **STAGE 1 FROZEN** (UTC in `FROZEN-UTC.txt`; integrity `SHA256SUMS`). Authorization: owner adjudication of
V2-M7 phase 1 ("AUTHORIZE A SMALL M7B", part B; V2-D-43); stage-1 freeze recorded as V2-D-45. C2 is a **separate, post-F4 prospective test**. It does
not replace, amend or re-score C1: C1 (`V2-C1-preregistration/`, `SHA256SUMS` `7dac8482…bfc8f`) stays immutable and
C1 / H8 remains the original registered FFLONK validation. C2 was created **after** the Groth16 / PLONK campaigns, after
F4, after the V2-M7A mechanism audit and after the V2-M7B-A re-trace; it is registered **before any d = 11 FFLONK
evidence exists** (no power-19 ptau, setup, verifier, proof, compiled artifact or measurement).

Model: **source-augmented ZKsync OS native-cost model (extended transaction-level accounting), "C2-SA"** — not
"source-complete": one environment-level constant (C_env) is calibrated, not derived from source.

| File | Content |
|---|---|
| `01-purpose-chronology-and-claim-boundary.md` | why C2 exists, exact chronology, inventory of existing FFLONK-related material, model name and claim boundary |
| `02-model-ledger.md`, `02-model-ledger.csv` | every term: formula, source, source-defined / structural input / calibrated, calibration data, backend and k dependence |
| `03-calibration.md` | C_env from registered Groth16 / PLONK only (18 re-traced proofs; 190 further proofs as internal check) |
| `04-prediction-procedure.md` | the pre-registered two-stage procedure (stage 2 = artifacts → structural derivation → numeric predictions frozen → only then measurement) |
| `05-target-cells.md` | exactly the 12 registered FFLONK validation cells; C2's claim is the 4 ZKsync OS cells (32 proofs) |
| `06-criteria-and-falsifiers.md` | residual, tolerance (with justification), PASS / FAIL / NOT EVALUABLE, exactness, ranking, crossover |
| `07-relation-to-C1-H8.md` | two separate evaluations; never merged; wording |
| `08-deviations-and-amendments.md` | what may change, when, and how it is recorded |
| `code/` | `c2_model.py`, `c2_structural.js` (+ `hardhat.config.js`), `c2_calibrate.py`, `c2_internal_check.py`, `c2_predict.py`, `c2_score.py` |
| `calibration/` | calibration manifests, structural records, `C2-CALIBRATION.json`, `C2-INTERNAL-CHECK.json` |
| `engineering-tests/` | pipeline tests on non-FFLONK data (PLONK as pseudo-target; positive and negative scoring tests) |
| `INPUT-HASHES.txt` | every input of this package |

Calibration result (no FFLONK input): C_env = **1,669,012** native, identical for all 18 calibration proofs; the frozen
model with this constant reproduces all 190 non-calibration registered Groth16 / PLONK ZKsync OS proofs to the native
unit (residual 0). Tolerance: τ_C2 = **0.000138** (relative), reused from C1. Engineering tests: pipeline PASS on a
PLONK pseudo-target; a 5,400-native perturbation is FAILED as required.
