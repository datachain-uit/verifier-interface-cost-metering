# 02 — Research questions and hypotheses (V2-C1, frozen)

Notation: G = Groth16, P = PLONK, F = FFLONK; k = verifier-visible public-input count; r_E(k) = mean cost of P / mean
cost of G in regime E (same proofs IDs j = 0…7, same metric). Metrics are defined in `18-evidence-schema.md`; the
primary metric is the direct verifier transaction **Y_dir**. Criteria are in `13-criteria.md`; falsifiers in `12-falsifiers.md`.

| ID | Class | Research question | Hypothesis (what would be confirmed) | Level |
|---|---|---|---|---|
| **RQ1 / H1** | CORE | How does the backend-relative cost change with k inside each regime? | In every CORE regime, G's cost rises by a per-input increment that contains exactly one ecMul and one ecAdd call; P's per-input increment contains no EC call. Hence r_E(k) is non-increasing in k (strictly decreasing between grid points whose costs are outside the equality band). | 1–2 |
| **RQ2 / H2** | CORE | Where does the ranking reverse, and does the location depend on the regime? | Each regime has its own crossover k\*_E, located inside the frozen interval of `09-numeric-predictions/crossover_intervals.csv`: EVM Osaka in the low teens; EraVM v29 at or just above k = 1; ZKsync OS v32.0 at the default `native_per_gas` = 100 between k = 2 and k = 4 | 2 |
| **RQ3 / H3** | CORE | Can the crossovers be explained by operation structure and metering components? | (a) template counts are exact (trace / frame counts); (b) the per-input slope difference B_G − B_P is accounted for by named components (EC precompile tariff, calldata, transcript hashing, compiled self-execution) whose spec/source prices are in the ledger; (c) the crossover implied by the component model lies in the frozen interval. | 2/3 |
| **RQ4 / H4** | CORE | Where the binding meter is observable, does the structural model predict held-out configurations? | ZKsync OS v32.0 native = published v0.4.0 table × the EVM opcode trace of the same proof + two shared constants calibrated only on k = 1 (G, P). Every held-out cell (k ≠ 1, anchors) is within the conditional tolerance τ_cond. | 4 |
| **RQ5 / H5** | CORE | Does the operator's `native_per_gas` causally switch the binding meter and the ranking? | For each tested (k, level): the binding meter is the predicted one; gas = max(EVM gas, ⌊native/npg⌋); the ranking at k = 4 reverses between the two pre-registered levels that bracket its predicted switch (full design); at k = 1 the ratio follows the predicted levels without reversal. | 4 (interventional) |
| **RQ6 / H6** | VALIDATION | Is verifier cost at fixed k independent of what the public inputs mean? | The k = 4 and k = 8 semantic anchors and the k = 4 disclosure variant cost the same as the context-tag circuit at the same k, within the regime's equality band. | 1–2 |
| **RQ7 / H7** | VALIDATION | Does the structural account transfer to a historical regime with a different tariff vector? | EraVM v27 cost at k ∈ {4, 6, 8, 16} is predicted from its own k = 1 cell plus the v29 per-input structure with v27 per-call frame tariffs; the v27 crossover lies in its frozen interval (≈ 7). Wording stays historical (protocol 27, local node). | 3 |
| **RQ8 / H8** | VALIDATION (conditional) | Does the ZKsync OS model predict a backend it never saw? | FFLONK (same d = 11 family) natives predicted by the H4 procedure with no FFLONK data in calibration are within τ_cond(F). Run only if the FFLONK gate passes (`21-…`). | 4 |
| SQ1 | SUPPORTING (specified, not run in CORE) | Does EVM accounting hold under an older tariff vector? | Petersburg cells: gas = trace × Petersburg schedule; crossover moves as the tariff vector predicts. | 1 |
| SQ2 | SUPPORTING | When does a deployment amortise? | Lifecycle break-even computed from registered deploy and verify costs (no new measurement). | descriptive |
| SQ3 | SUPPORTING | Prover robustness (D1 / D3 / D2) | Specified in `16-full-protocol.md` §5; hardware for D2 OPEN. | descriptive |

## Directional expectations frozen from structure (not from fitting)

1. G per-input increment ⊇ {1 ecMul, 1 ecAdd, 32 calldata bytes, input field check, IC accumulation}.
2. P per-input increment ⊇ {≈9 MULMOD-class operations, 32 calldata bytes, 32 transcript bytes, one Lagrange term}; no EC call.
3. Therefore B_G > B_P in every regime whose EC tariff is positive; the sign of A_P − A_G decides whether k\* ≤ 1.
4. Under ZKsync OS VM v0.4.0 the 4-pair pairing that G pays (6.244M + 4 × 6.908M native) is no longer heavier than P's
   18 ecMul + 18 ecAdd + 2-pair pairing by the margin it was under v0.3.2. The ranking at k = 1 therefore flips relative
   to v31 (G cheaper at k = 1 under v32), and an interior crossover appears. This is a **forward prediction**: no
   ZKsync OS v32 measurement at k > 1 exists.

## What is not hypothesised

- No hypothesis compares absolute costs across regimes.
- No hypothesis claims the model holds outside the tested templates, curve, compilers or k range (k = 64 is a limit
  check, scored descriptively).
- Y_app (manager path) is secondary: it is scored for EVM and EraVM and kept for V1 comparability at k = 1.
