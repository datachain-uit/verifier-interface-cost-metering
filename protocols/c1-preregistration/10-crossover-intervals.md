# 10 — Predicted crossover intervals (V2-C1, frozen)

**Generated** by `model/render_tables.py` from `09-numeric-predictions/` (frozen). Do not edit by hand.

k\* = k at which mean PLONK cost equals mean Groth16 cost (linear interpolation between modelled integer k). Interval from the
prediction intervals of both templates (`13-criteria.md` §4). Source CSV: `09-numeric-predictions/crossover_intervals.csv`.

| Regime | Metric | k\* point | k\* interval | Sign at k = 1 | Class |
|---|---|---|---|---|---|
| evm-osaka | dir | 13.99 | [13.17, 14.83] | PLONK_COSTLIER | CORE |
| evm-osaka | app | 13.9 | [13.01, 14.81] | PLONK_COSTLIER | CORE |
| eravm-29 | dir | 1.4 | [<=1, 3.48] | PLONK_COSTLIER | CORE |
| eravm-29 | app | 1.49 | [<=1, 3.63] | PLONK_COSTLIER | CORE |
| eravm-27 | dir | 6.94 | [6.48, 7.4] | PLONK_COSTLIER | VALIDATION |
| evm-petersburg | dir | 15.85 | [15.81, 15.89] | PLONK_COSTLIER | SUPPORTING |
| zkos-v32 | native | 3.53 | [3.14, 3.92] | PLONK_COSTLIER | CORE (native) |
| zkos-v32@npg100 | dir | 3.53 | [3.14, 3.92] | PLONK_COSTLIER | CORE (gas, default npg) |

## Predicted sign per grid point (Y_dir; ZKsync OS native and default-npg gas)

| Regime | k=1 | k=2 | k=4 | k=6 | k=8 | k=12 | k=16 | k=24 | k=32 |
|---|---|---|---|---|---|---|---|---|---|
| evm-osaka | G<P (1.358) | G<P (1.320) | G<P (1.250) | G<P (1.189) | G<P (1.134) | G<P (1.040) | P<G (0.963) | P<G (0.844) | P<G (0.756) |
| eravm-29 | ≈ (1.004) | ≈ (0.994) | P<G (0.975) | P<G (0.957) | P<G (0.940) | P<G (0.908) | P<G (0.880) | P<G (0.831) | P<G (0.791) |
| zkos-v32@npg100 | G<P (1.060) | G<P (1.035) | P<G (0.990) | P<G (0.948) | P<G (0.910) | P<G (0.843) | P<G (0.785) | P<G (0.691) | P<G (0.618) |
| eravm-27 | G<P (1.208) | — | G<P (1.093) | G<P (1.028) | P<G (0.970) | — | P<G (0.792) | — | — |
| evm-petersburg | G<P (2.220) | — | G<P (1.770) | — | — | — | P<G (0.995) | — | — |

"G<P": Groth16 cheaper (PLONK/Groth16 ratio interval above 1); "P<G": PLONK cheaper; "≈": interval contains 1 (not sign-scored). Value in parentheses: predicted ratio.
