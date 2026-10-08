# 13 — Accuracy and indeterminacy criteria (V2-C1, frozen)

All thresholds below are **derived from P0 noise and P0 residuals** by `model/c1_predict.py`; none is a round number
chosen by hand. Values: `13-tolerances.csv` (generated) and `09-numeric-predictions/fitted_parameters_and_tolerances.json`.
Error convention everywhere: e = (measured − predicted) / predicted.

## 1. Three kinds of success, scored separately

| Kind | What passes | Criterion | Can it support a predictive claim? |
|---|---|---|---|
| **Accounting** (Level 1) | the numbers add up | exact identities L1-EVM, L1-EraVM, L1-STRUCT (counts and transcript rounds); L1-ZK within ±1 gas; all controls as expected (`17-…`) | no |
| **Explanatory fit** (Level 2/3) | the crossover sits where the regime's prices of the template's operations put it | §4 crossover criterion on the component-model crossover; signs §3; per-input decomposition reported with component shares (no threshold) | no |
| **Predictive success** (Level 4, and held-out k at Level 2) | values not used in calibration are predicted | §2 cost-error criterion on held-out cells; §5 conditional criterion for ZKsync OS | yes, within the stated scope only |

## 2. Cost-error criterion (cells)

PASS iff the measured cell mean (8 proofs) lies in [lo, hi] of `09-numeric-predictions/predictions_cells.csv` (prediction set P), and,
for procedure R, iff |e| ≤ τ_E,b,m.

τ_E,b,m = τ_noise + τ_struct, where
- τ_noise = the largest P0 within-cell half-range (max − min)/(2 · mean) of that regime and template over the P0
  context-tag / V1 cells with k ≤ 32 (for EVM computed on calldata-normalised gas, because calldata gas is predicted
  exactly from the frozen corpus);
- τ_struct = the largest |e| of the k ∈ {1, 4}-calibrated model at the P0 seen-but-not-fitted k ∈ {2, 16, 32}
  (EraVM v27: at k ∈ {4, 16} of the transfer model; ZKsync OS: k-model interpolation residual on v0.4.0 trace-model
  natives + the v31 conditional-model residual).

Consequence of this construction: P0 residuals at k ∈ {2, 16, 32} define τ, so those k are **seen-in-P0** held-out
cells (weak test); k ∈ {6, 8, 12, 24} are **strictly unseen** (the tolerance never saw them). Claims of held-out-k
prediction rest on the strictly unseen cells; seen-in-P0 cells are reported but cannot alone support a claim.

## 3. Equality band, signs and in-band cells

- **Equality band** ε_E = h_G(E) + h_P(E), the summed largest P0 raw within-cell half-ranges of the two templates in
  regime E (`09-numeric-predictions/equality_bands.csv`). ZKsync OS: the larger of the v32 smoke and the P0 v31 native half-ranges.
- **Measured class** of a (regime, k) pair: IN-BAND if |r − 1| ≤ ε_E; otherwise PLONK_COSTLIER (r > 1) or
  PLONK_CHEAPER (r < 1). The all-vs-all separation of the 8 + 8 proofs is reported alongside (no decision role).
- **Predicted class** (`09-numeric-predictions/predictions_signs.csv`): from the prediction intervals, r_lo = P_lo / G_hi, r_hi = P_hi / G_lo:
  PLONK_COSTLIER if r_lo > 1; PLONK_CHEAPER if r_hi < 1; INDETERMINATE otherwise.
- **Sign scoring:** predicted INDETERMINATE → not scored for sign. Predicted decided and measured equal → MATCH.
  Predicted decided and measured the opposite decided class → **FALSIFIED** (counts against H2/H3). Predicted decided
  and measured IN-BAND → IN-BAND-MISS (not a sign falsification; the ratio-error criterion decides).
- **Ratio-error criterion:** PASS iff measured r ∈ [r_lo, r_hi].
- **In-band cells in crossover location:** see §4.

## 4. Crossover-location criterion

- Measured k\*: linear interpolation of the mean difference (P − G) between the two grid points where it changes sign.
  If IN-BAND cells exist around the change, the measured crossover interval is [min, max] of {interpolated k\*} ∪
  {k of in-band cells}. If no sign change occurs inside the grid, the measured statement is "≤ 1" or "> 32".
- PASS iff the measured interval intersects the frozen interval [k\*_lo, k\*_hi] of `09-numeric-predictions/crossover_intervals.csv`
  (and, for "no change in the grid", iff the frozen interval also reaches that boundary).

## 5. ZKsync OS conditional criterion (H4, H8)

Per proof: |e| ≤ τ_cond(b), τ_cond = the largest |held-out error| of the same conditional model on P0 v31 data
(G16 ≈ 0.014 %, PLONK ≈ 0.45 %, FFLONK ≈ 0.57 %; exact values in the tolerance file). H4 passes iff **every** held-out
G16 and PLONK proof (k ≠ 1, k ≤ 32, plus anchors) passes. k = 64 is descriptive.

## 6. Intervention criterion (H5)

For each (k, level, template): the measured binding meter (NATIVE if gas = ⌊N/npg⌋ > EVM gas of the same proof; EVM_GAS
if gas equals the EDR gas) equals the predicted meter of `09-numeric-predictions/zkos_npg_predictions.csv` (INDETERMINATE predictions are not
scored); and the measured gas lies in the predicted [G_lo, G_hi]. The ranking per (k, level) is scored with §3.

## 7. Semantic invariance (H6)

|mean(anchor) − mean(ctx at the same k)| / mean(ctx) ≤ ε_E, on Ync (EVM), Y (EraVM) and N (ZKsync OS), direct call.

## 8. Aggregation into claims

- A Level-4 claim for a regime/template is allowed only if **all** its strictly-unseen held-out cells pass (§2 under R,
  or §5 for ZKsync OS). One failure blocks the claim for that regime/template; it is reported with its error, never
  averaged away.
- An explanatory claim (H3) for regime E is allowed if accounting passes and the §4 crossover criterion passes for E;
  failure of a single sign test in E (FALSIFIED) blocks it.
- Pilot criteria are the same; the pilot only has the k ∈ {2, 16} held-out cells (seen-in-P0), so the pilot can confirm
  or falsify but cannot by itself establish a Level-4 claim.
