# 11 — ZKsync OS v32.0: `native_per_gas` switch intervals and intervention levels (V2-C1, frozen)

**Generated** by `model/render_tables.py` from `09-numeric-predictions/` (frozen). Do not edit by hand.

npg\*(b, k) = N_b(k) / G_evm,b(k): below it the transaction is native-bound, above it EVM-gas-bound. Interval from the native and
EVM-gas prediction intervals. CSVs: `zkos_switch_intervals.csv`, `zkos_npg_levels.csv`, `zkos_npg_predictions.csv`.

| Template | k | native (pred) | EVM gas (pred) | npg\* | interval |
|---|---|---|---|---|---|
| groth16 | 1 | 36,506,865 | 214,590 | 170.12 | [169.72, 170.53] |
| groth16 | 2 | 37,400,509 | 221,762 | 168.65 | [168.26, 169.05] |
| groth16 | 4 | 39,187,796 | 236,104 | 165.98 | [165.59, 166.37] |
| groth16 | 6 | 40,975,083 | 250,466 | 163.6 | [163.21, 163.98] |
| groth16 | 8 | 42,762,370 | 264,807 | 161.49 | [161.11, 161.86] |
| groth16 | 12 | 46,336,944 | 293,498 | 157.88 | [157.51, 158.25] |
| groth16 | 16 | 49,911,518 | 322,195 | 154.91 | [154.55, 155.27] |
| groth16 | 24 | 57,060,666 | 379,576 | 150.33 | [149.98, 150.68] |
| groth16 | 32 | 64,209,814 | 436,971 | 146.94 | [146.6, 147.28] |
| plonk | 1 | 38,683,079 | 291,490 | 132.71 | [129.76, 135.74] |
| plonk | 2 | 38,714,617 | 292,748 | 132.25 | [129.31, 135.26] |
| plonk | 4 | 38,781,539 | 295,242 | 131.35 | [128.45, 134.34] |
| plonk | 6 | 38,844,615 | 297,765 | 130.45 | [127.57, 133.42] |
| plonk | 8 | 38,911,537 | 300,272 | 129.59 | [126.73, 132.53] |
| plonk | 12 | 39,041,535 | 305,296 | 127.88 | [125.07, 130.77] |
| plonk | 16 | 39,167,687 | 310,318 | 126.22 | [123.46, 129.06] |
| plonk | 24 | 39,427,683 | 320,352 | 123.08 | [120.4, 125.83] |
| plonk | 32 | 39,687,679 | 330,424 | 120.11 | [117.52, 122.78] |

## Pre-registered intervention levels and predictions

Levels: 100 and 300 (away), each template's predicted switch × (1 ± 2 × relative half-width of its interval), rounded outward (around), and the midpoint of the two switches (between).

| k | npg | purpose | G16 meter | G16 gas [lo, hi] | PLONK meter | PLONK gas [lo, hi] | PLONK/G16 ratio [lo, hi] → class |
|---|---|---|---|---|---|---|---|
| 1 | 100 | away (below both switches) | NATIVE | 365,069 [364,923, 365,214] | NATIVE | 386,831 [383,659, 390,003] | 1.05961 [1.05051, 1.06872] → PLONK_COSTLIER |
| 1 | 126 | around a predicted switch | NATIVE | 289,737 [289,622, 289,852] | NATIVE | 307,009 [304,491, 309,526] | 1.05961 [1.05051, 1.06872] → PLONK_COSTLIER |
| 1 | 139 | around a predicted switch | NATIVE | 262,639 [262,535, 262,744] | EVM_GAS | 291,490 [287,320, 295,661] | 1.10985 [1.09354, 1.12617] → PLONK_COSTLIER |
| 1 | 151 | between the two switches | NATIVE | 241,767 [241,671, 241,864] | EVM_GAS | 291,490 [287,320, 295,661] | 1.20567 [1.18795, 1.2234] → PLONK_COSTLIER |
| 1 | 169 | around a predicted switch | NATIVE | 216,017 [215,931, 216,103] | EVM_GAS | 291,490 [287,320, 295,661] | 1.34939 [1.32956, 1.36923] → PLONK_COSTLIER |
| 1 | 171 | around a predicted switch | EVM_GAS | 214,590 [214,167, 215,012] | EVM_GAS | 291,490 [287,320, 295,661] | 1.35836 [1.33631, 1.38051] → PLONK_COSTLIER |
| 1 | 300 | away (above both switches) | EVM_GAS | 214,590 [214,167, 215,012] | EVM_GAS | 291,490 [287,320, 295,661] | 1.35836 [1.33631, 1.38051] → PLONK_COSTLIER |
| 4 | 100 | away (below both switches) | NATIVE | 391,878 [391,722, 392,034] | NATIVE | 387,815 [384,635, 390,996] | 0.98963 [0.98113, 0.99814] → PLONK_CHEAPER |
| 4 | 125 | around a predicted switch | NATIVE | 313,502 [313,378, 313,627] | NATIVE | 310,252 [307,708, 312,797] | 0.98963 [0.98113, 0.99814] → PLONK_CHEAPER |
| 4 | 138 | around a predicted switch | NATIVE | 283,970 [283,856, 284,083] | EVM_GAS | 295,242 [291,038, 299,447] | 1.0397 [1.02449, 1.05492] → PLONK_COSTLIER |
| 4 | 149 | between the two switches | NATIVE | 263,005 [262,901, 263,110] | EVM_GAS | 295,242 [291,038, 299,447] | 1.12257 [1.10615, 1.13901] → PLONK_COSTLIER |
| 4 | 165 | around a predicted switch | NATIVE | 237,502 [237,407, 237,596] | EVM_GAS | 295,242 [291,038, 299,447] | 1.24312 [1.22493, 1.26132] → PLONK_COSTLIER |
| 4 | 167 | around a predicted switch | EVM_GAS | 236,104 [235,642, 236,566] | EVM_GAS | 295,242 [291,038, 299,447] | 1.25048 [1.23027, 1.27077] → PLONK_COSTLIER |
| 4 | 300 | away (above both switches) | EVM_GAS | 236,104 [235,642, 236,566] | EVM_GAS | 295,242 [291,038, 299,447] | 1.25048 [1.23027, 1.27077] → PLONK_COSTLIER |
| 16 | 100 | away (below both switches) | NATIVE | 499,115 [498,917, 499,314] | NATIVE | 391,677 [388,465, 394,889] | 0.78474 [0.778, 0.79149] → PLONK_CHEAPER |
| 16 | 120 | around a predicted switch | NATIVE | 415,929 [415,764, 416,095] | NATIVE | 326,397 [323,721, 329,074] | 0.78474 [0.778, 0.79149] → PLONK_CHEAPER |
| 16 | 132 | around a predicted switch | NATIVE | 378,118 [377,967, 378,268] | EVM_GAS | 310,318 [305,978, 314,658] | 0.82069 [0.80889, 0.8325] → PLONK_CHEAPER |
| 16 | 141 | between the two switches | NATIVE | 353,982 [353,842, 354,123] | EVM_GAS | 310,318 [305,978, 314,658] | 0.87665 [0.86405, 0.88926] → PLONK_CHEAPER |
| 16 | 154 | around a predicted switch | NATIVE | 324,101 [323,972, 324,230] | EVM_GAS | 310,318 [305,978, 314,658] | 0.95747 [0.94371, 0.97125] → PLONK_CHEAPER |
| 16 | 156 | around a predicted switch | EVM_GAS | 322,195 [321,572, 322,818] | EVM_GAS | 310,318 [305,978, 314,658] | 0.96314 [0.94784, 0.9785] → PLONK_CHEAPER |
| 16 | 300 | away (above both switches) | EVM_GAS | 322,195 [321,572, 322,818] | EVM_GAS | 310,318 [305,978, 314,658] | 0.96314 [0.94784, 0.9785] → PLONK_CHEAPER |
