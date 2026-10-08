# 09 — Numeric predictions, set P (V2-C1, frozen; immutable before the pilot)

**Generated** by `model/render_tables.py` from `09-numeric-predictions/` (frozen). Do not edit by hand.

Generator: `model/c1_predict.py` (calibration sources in its header and in `07-parameter-ledger.csv`). Files in `09-numeric-predictions/`:

| File | Content |
|---|---|
| `predictions_cells.csv` | one row per (regime, template, circuit, metric): point prediction, [lo, hi], τ, calldata gas added (EVM), role |
| `predictions_signs.csv` | predicted PLONK/Groth16 ratio, ratio interval and predicted class per (regime, k) |
| `crossover_intervals.csv` | k\* point and interval per regime (`10-…`) |
| `zkos_switch_intervals.csv`, `zkos_npg_levels.csv`, `zkos_npg_predictions.csv` | ZKsync OS switch points, intervention levels and per-level predictions (`11-…`) |
| `equality_bands.csv` | ε per regime |
| `fitted_parameters_and_tolerances.json` | A, B, base, c and every τ with its basis |
| `p0_model_check.csv` | residuals of the calibrated models at P0 seen-not-fitted k (the only use of those P0 cells: τ_struct) |

## Pilot cells (direct verifier call, a-priori)

| Regime | Template | k | prediction | [lo, hi] | role |
|---|---|---|---|---|---|
| evm-osaka (Y_dir, gas) | groth16 | 1 | 214,590 | [214,167, 215,012] | CALIBRATION |
| evm-osaka (Y_dir, gas) | groth16 | 2 | 221,762 | [221,326, 222,197] | HELD-OUT-k/seen-in-P0 |
| evm-osaka (Y_dir, gas) | groth16 | 4 | 236,104 | [235,642, 236,566] | CALIBRATION |
| evm-osaka (Y_dir, gas) | groth16 | 16 | 322,195 | [321,572, 322,818] | HELD-OUT-k/seen-in-P0 |
| evm-osaka (Y_dir, gas) | plonk | 1 | 291,490 | [287,320, 295,661] | CALIBRATION |
| evm-osaka (Y_dir, gas) | plonk | 2 | 292,748 | [288,567, 296,930] | HELD-OUT-k/seen-in-P0 |
| evm-osaka (Y_dir, gas) | plonk | 4 | 295,242 | [291,038, 299,447] | CALIBRATION |
| evm-osaka (Y_dir, gas) | plonk | 16 | 310,318 | [305,978, 314,658] | HELD-OUT-k/seen-in-P0 |
| eravm-29 (Y_dir, eravm_computational_gas) | groth16 | 1 | 444,263 | [443,986, 444,540] | CALIBRATION |
| eravm-29 (Y_dir, eravm_computational_gas) | groth16 | 2 | 451,206 | [450,924, 451,487] | HELD-OUT-k/seen-in-P0 |
| eravm-29 (Y_dir, eravm_computational_gas) | groth16 | 4 | 465,091 | [464,801, 465,381] | CALIBRATION |
| eravm-29 (Y_dir, eravm_computational_gas) | groth16 | 16 | 548,403 | [548,061, 548,745] | HELD-OUT-k/seen-in-P0 |
| eravm-29 (Y_dir, eravm_computational_gas) | plonk | 1 | 446,058 | [437,081, 455,035] | CALIBRATION |
| eravm-29 (Y_dir, eravm_computational_gas) | plonk | 2 | 448,483 | [439,457, 457,508] | HELD-OUT-k/seen-in-P0 |
| eravm-29 (Y_dir, eravm_computational_gas) | plonk | 4 | 453,372 | [444,248, 462,496] | CALIBRATION |
| eravm-29 (Y_dir, eravm_computational_gas) | plonk | 16 | 482,548 | [472,837, 492,259] | HELD-OUT-k/seen-in-P0 |
| zkos-v32 (N_dir, computational_native) | groth16 | 1 | 36,506,865 | [36,492,392, 36,521,338] | CALIBRATION |
| zkos-v32 (N_dir, computational_native) | groth16 | 2 | 37,400,509 | [37,385,682, 37,415,335] | HELD-OUT-k/seen-in-P0-trace |
| zkos-v32 (N_dir, computational_native) | groth16 | 4 | 39,187,796 | [39,172,260, 39,203,331] | HELD-OUT-k/seen-in-P0-trace |
| zkos-v32 (N_dir, computational_native) | groth16 | 16 | 49,911,518 | [49,891,732, 49,931,304] | HELD-OUT-k/seen-in-P0-trace |
| zkos-v32 (N_dir, computational_native) | plonk | 1 | 38,683,079 | [38,365,922, 39,000,236] | CALIBRATION |
| zkos-v32 (N_dir, computational_native) | plonk | 2 | 38,714,617 | [38,397,202, 39,032,032] | HELD-OUT-k/seen-in-P0-trace |
| zkos-v32 (N_dir, computational_native) | plonk | 4 | 38,781,539 | [38,463,575, 39,099,503] | HELD-OUT-k/seen-in-P0-trace |
| zkos-v32 (N_dir, computational_native) | plonk | 16 | 39,167,687 | [38,846,557, 39,488,817] | HELD-OUT-k/seen-in-P0-trace |
| zkos-v32@npg100 (G_dir, gas) | groth16 | 1 | 365,069 | [364,923, 365,214] | CALIBRATION/binding=NATIVE |
| zkos-v32@npg100 (G_dir, gas) | groth16 | 2 | 374,005 | [373,856, 374,154] | HELD-OUT-k/binding=NATIVE |
| zkos-v32@npg100 (G_dir, gas) | groth16 | 4 | 391,878 | [391,722, 392,034] | HELD-OUT-k/binding=NATIVE |
| zkos-v32@npg100 (G_dir, gas) | groth16 | 16 | 499,115 | [498,917, 499,314] | HELD-OUT-k/binding=NATIVE |
| zkos-v32@npg100 (G_dir, gas) | plonk | 1 | 386,831 | [383,659, 390,003] | CALIBRATION/binding=NATIVE |
| zkos-v32@npg100 (G_dir, gas) | plonk | 2 | 387,146 | [383,972, 390,321] | HELD-OUT-k/binding=NATIVE |
| zkos-v32@npg100 (G_dir, gas) | plonk | 4 | 387,815 | [384,635, 390,996] | HELD-OUT-k/binding=NATIVE |
| zkos-v32@npg100 (G_dir, gas) | plonk | 16 | 391,677 | [388,465, 394,889] | HELD-OUT-k/binding=NATIVE |

## P0 model check used for τ_struct

| Model | Template | Metric | k | model | P0 | e (%) |
|---|---|---|---|---|---|---|
| evm-osaka | groth16 | Y_dir | 2 | 216612 | 216625.0 | 0.006 |
| evm-osaka | groth16 | Y_dir | 16 | 310062 | 309657.0 | -0.1306 |
| evm-osaka | groth16 | Y_dir | 32 | 416862 | 416025.0 | -0.2008 |
| evm-osaka | groth16 | Y_dir | 64 | 630462 | 628761.0 | -0.2698 |
| evm-osaka | groth16 | Y_app | 2 | 225984 | 225965.0 | -0.0083 |
| evm-osaka | groth16 | Y_app | 16 | 319583 | 318988.0 | -0.1862 |
| evm-osaka | groth16 | Y_app | 32 | 426554 | 425530.0 | -0.24 |
| evm-osaka | groth16 | Y_app | 64 | 640495 | 638488.0 | -0.3134 |
| evm-osaka | plonk | Y_dir | 2 | 279422 | 279050.0 | -0.133 |
| evm-osaka | plonk | Y_dir | 16 | 290029 | 290555.0 | 0.1814 |
| evm-osaka | plonk | Y_dir | 32 | 302152 | 305335.0 | 1.0536 |
| evm-osaka | plonk | Y_dir | 64 | 326397 | 334233.0 | 2.4008 |
| evm-osaka | plonk | Y_app | 2 | 288417 | 287980.0 | -0.1515 |
| evm-osaka | plonk | Y_app | 16 | 298973 | 299659.0 | 0.2295 |
| evm-osaka | plonk | Y_app | 32 | 311037 | 314517.0 | 1.1188 |
| evm-osaka | plonk | Y_app | 64 | 335165 | 343661.0 | 2.5349 |
| evm-petersburg | groth16 | Y_dir | 16 | 1118462 | 1118057.0 | -0.0362 |
| evm-petersburg | groth16 | Y_app | 16 | 1122283 | 1121688.0 | -0.053 |
| evm-petersburg | plonk | Y_dir | 16 | 1077529 | 1078055.0 | 0.0488 |
| evm-petersburg | plonk | Y_app | 16 | 1080773 | 1081459.0 | 0.0635 |
| eravm-29 | groth16 | Y_dir | 2 | 451206 | 451223.0 | 0.0038 |
| eravm-29 | groth16 | Y_dir | 16 | 548403 | 548592.0 | 0.0345 |
| eravm-29 | groth16 | Y_dir | 32 | 659486 | 659896.0 | 0.0622 |
| eravm-29 | groth16 | Y_dir | 64 | 881651 | 882416.0 | 0.0868 |
| eravm-29 | groth16 | Y_app | 2 | 458257 | 458286.0 | 0.0064 |
| eravm-29 | groth16 | Y_app | 16 | 555986 | 556073.0 | 0.0156 |
| eravm-29 | groth16 | Y_app | 32 | 667677 | 667895.0 | 0.0327 |
| eravm-29 | groth16 | Y_app | 64 | 891058 | 891451.0 | 0.0441 |
| eravm-29 | plonk | Y_dir | 2 | 448483 | 447655.0 | -0.1845 |
| eravm-29 | plonk | Y_dir | 16 | 482548 | 477472.0 | -1.0519 |
| eravm-29 | plonk | Y_dir | 32 | 521503 | 512934.0 | -1.6431 |
| eravm-29 | plonk | Y_dir | 64 | 599412 | 584113.0 | -2.5523 |
| eravm-29 | plonk | Y_app | 2 | 455978 | 455154.0 | -0.1806 |
| eravm-29 | plonk | Y_app | 16 | 490687 | 485431.0 | -1.0712 |
| eravm-29 | plonk | Y_app | 32 | 530378 | 521393.0 | -1.694 |
| eravm-29 | plonk | Y_app | 64 | 609759 | 593620.0 | -2.6468 |
| eravm-27 | groth16 | Y_dir | 4 | 9599886 | 9578687.0 | -0.2208 |
| eravm-27 | groth16 | Y_dir | 16 | 13283078 | 13208982.0 | -0.5578 |
| eravm-27 | groth16 | Y_app | 4 | 9607013 | 9585814.0 | -0.2207 |
| eravm-27 | groth16 | Y_app | 16 | 13290661 | 13216463.0 | -0.5583 |
| eravm-27 | plonk | Y_dir | 4 | 10495326 | 10466806.0 | -0.2717 |
| eravm-27 | plonk | Y_dir | 16 | 10524502 | 10510274.0 | -0.1352 |
| eravm-27 | plonk | Y_app | 4 | 10502913 | 10474393.0 | -0.2715 |
| eravm-27 | plonk | Y_app | 16 | 10532641 | 10518233.0 | -0.1368 |
| zkos-v31 P0 (VM v0.3.2) conditional | plonk | N_dir | 4 | 64041123 | 64070233 | 0.0455 |
| zkos-v31 P0 (VM v0.3.2) conditional | groth16 | N_dir | 4 | 80329538 | 80328169 | -0.0017 |
| zkos-v31 P0 (VM v0.3.2) conditional | plonk | N_dir | 16 | 64918857 | 65063643 | 0.223 |
| zkos-v31 P0 (VM v0.3.2) conditional | fflonk | N_dir | 16 | 55956232 | 56274630 | 0.569 |
| zkos-v31 P0 (VM v0.3.2) conditional | plonk | N_dir | 4 | 64061123 | 64090233 | 0.0454 |
| zkos-v31 P0 (VM v0.3.2) conditional | plonk | N_dir | 2 | 63816909 | 63826589 | 0.0152 |
| zkos-v31 P0 (VM v0.3.2) conditional | groth16 | N_dir | 4 | 80329538 | 80328169 | -0.0017 |
| zkos-v31 P0 (VM v0.3.2) conditional | fflonk | N_dir | 1 | 54843216 | 55008259 | 0.3009 |
| zkos-v31 P0 (VM v0.3.2) conditional | groth16 | N_dir | 8 | 83723442 | 83720021 | -0.0041 |
| zkos-v31 P0 (VM v0.3.2) conditional | groth16 | N_dir | 16 | 90516729 | 90509885 | -0.0076 |
| zkos-v31 P0 (VM v0.3.2) conditional | groth16 | N_dir | 32 | 104103304 | 104088933 | -0.0138 |
| zkos-v31 P0 (VM v0.3.2) conditional | groth16 | N_dir | 4 | 80329538 | 80328169 | -0.0017 |
| zkos-v31 P0 (VM v0.3.2) conditional | fflonk | N_dir | 4 | 55059844 | 55255933 | 0.3561 |
| zkos-v31 P0 (VM v0.3.2) conditional | plonk | N_dir | 8 | 64299485 | 64366975 | 0.105 |
| zkos-v31 P0 (VM v0.3.2) conditional | groth16 | N_dir | 2 | 78630276 | 78629593 | -0.0009 |
| zkos-v31 P0 (VM v0.3.2) conditional | fflonk | N_dir | 2 | 54919296 | 55094801 | 0.3196 |
| zkos-v31 P0 (VM v0.3.2) conditional | plonk | N_dir | 32 | 66217841 | 66517219 | 0.4521 |
| zkos-v32 (trace-model natives) | groth16 | N_dir | 16 | 49911518 | 49903408 | -0.0162 |
| zkos-v32 (trace-model natives) | groth16 | N_dir | 32 | 64209814 | 64193224 | -0.0258 |
| zkos-v32 (trace-model natives) | groth16 | N_dir | 2 | 37400509 | 37400759 | 0.0007 |
| zkos-v32 (trace-model natives) | plonk | N_dir | 16 | 39167687 | 39183859 | 0.0413 |
| zkos-v32 (trace-model natives) | plonk | N_dir | 2 | 38714617 | 38661291 | -0.1377 |
| zkos-v32 (trace-model natives) | plonk | N_dir | 32 | 39687679 | 39794857 | 0.2701 |
| zkos-v32 (trace-model natives) | fflonk | N_dir | 16 | 28522609 | 28502361 | -0.071 |
| zkos-v32 (trace-model natives) | fflonk | N_dir | 2 | 28018261 | 28021653 | 0.0121 |
