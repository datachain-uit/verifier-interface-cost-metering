# 06 — Residual, tolerance, criteria and falsifiers (frozen)

**Residual.** r = N_measured − N̂ (native units); e = r / N̂.

**Tolerance τ_C2 = 0.000138 (relative), per proof.** Reused, not chosen here: it is C1's τ_cond for ZKsync OS Groth16
(`13-tolerances.csv`, key `zkos-v32|groth16|native`), fixed on 2026-10-04 from P0 data, before F4, the M7 audits and any
FFLONK artifact. Why this one:
1. it is the precision at which the frozen C1 model failed (F4); C2 asks whether the extended accounting closes that gap
   on a backend it has never seen;
2. it is the tightest independently justified ZKsync OS tolerance. FFLONK's template precompile natives alone are
   2.45 × 10⁷ (5 ecMul, 7 ecAdd, one 2-pair pairing; source constants), so τ_C2 · N̂ ≳ 3.4 × 10³ native. Every term class
   that M7A found missing in the frozen model is far larger than that at FFLONK's size (calldata 60 × (772 + 32k) ≥ 48,240;
   decommitment of a verifier of several kB ≥ 10⁴; 13 call overheads ≈ 5.5 × 10⁴), and so is the frozen model's call-constant
   bias (1,658.8 per call); omitting or mis-pricing any of them fails C2-PRIMARY. Errors smaller than ≈ 3.4 × 10³ native
   (e.g. fewer than ≈ 100 heap events) can pass C2-PRIMARY and are caught only by C2-EXACT;
3. C1's FFLONK tolerance τ_cond(F) = 0.569 % (H8) is ≈ 40 × wider and is not used: it would not discriminate the extended
   model from the frozen one;
4. the calibration residuals are exactly 0, so no noise-based tolerance can be derived from them; a zero tolerance is
   kept as the separate exactness criterion below rather than as the pass / fail bar.

## Criteria

| ID | Criterion | PASS | FAIL (falsifier) | NOT EVALUABLE |
|---|---|---|---|---|
| **C2-PRIMARY** | every one of the 32 FFLONK ZKsync OS direct-call proofs has |e| ≤ τ_C2 | all 32 inside | **F-C2-1**: any comparable proof outside τ_C2 (regardless of missing proofs) | a proof missing, failed stage-2 gate, or structural mismatch between its registered EVM trace and its stage-2 record, with no comparable proof outside τ |
| **C2-EXACT** | r = 0 for every proof (the sharp form of the accounting claim) | all 32 exactly 0 | **F-C2-2**: any comparable proof with r ≠ 0 | as above |
| **C2-RANK** | for each k and comparator X ∈ {Groth16, PLONK} with a determinate stage-2 ranking prediction, the measured sign of mean(N_F) − mean(N_X) equals the predicted sign | all determinate comparisons match | **F-C2-3**: any determinate comparison with the opposite measured sign | no determinate prediction / missing cells |
| **C2-XOVER** | for each X, the measured sign sequence over k ∈ {1, 4, 16, 32} equals the predicted one on the determinate k (hence the same crossover interval or "none within the grid") | match | **F-C2-4**: any determinate mismatch | as above |

The C2 claim of `01` §4 requires C2-PRIMARY = PASS. C2-EXACT, C2-RANK and C2-XOVER are reported separately and are not
aggregated into one score. A FAIL is reported as such: no term, constant, τ or rule is changed afterwards; any new model
needs a new registration and new held-out data.

**Expected direction of a failure (stated now).** If C_env is not template-independent, all FFLONK residuals share one
offset (same sign, nearly constant in k); if a per-input or per-call charge is still missing, residuals change with k or
with the number of calls. The score file reports the residual pattern; it is descriptive and changes no verdict.
