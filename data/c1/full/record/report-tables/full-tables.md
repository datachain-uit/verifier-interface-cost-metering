### S1. Strictly unseen k ∈ {6, 8, 12, 24} — EVM Osaka and EraVM v29 (prediction set P and registered-calibration procedure R side by side)

P: frozen a-priori prediction and interval (PASS iff the 8-proof mean lies in [lo, hi]). R: A, B refitted on registered k = 1, 4; PASS iff |e| ≤ τ (EVM on calldata-normalised gas). Errors e = (measured − predicted) / predicted. Ranking (direct call only): frozen predicted class vs measured class at the same k.

| regime | backend | k | metric | P pred | P interval | P ± | observed mean | proof range | P abs err | P rel err % | P verdict | R metric | R pred | R abs err | R rel err % | R τ | R verdict | predicted rank | measured rank | rank verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| evm-osaka | groth16 | 6 | Y_dir | 250,466 | [249,977, 250,955] | 0.201 % | 250,331.0 | 250,313 – 250,349 | -135.0 | -0.0539 | PASS | Ync_dir | 243,312 | -135.0 | -0.0555 | 0.201 % | PASS | PLONK_COSTLIER | PLONK_COSTLIER | MATCH |
| evm-osaka | groth16 | 6 | Y_app | 259,880 | [259,273, 260,487] | 0.240 % | 259,677.0 | 259,659 – 259,695 | -203.0 | -0.0781 | PASS | Ync_app | 252,726 | -203.0 | -0.0805 | 0.240 % | PASS |  |  |  |
| evm-osaka | groth16 | 8 | Y_dir | 264,807 | [264,291, 265,323] | 0.201 % | 264,618.0 | 264,597 – 264,645 | -189.0 | -0.0714 | PASS | Ync_dir | 256,662 | -189.0 | -0.0736 | 0.201 % | PASS | PLONK_COSTLIER | PLONK_COSTLIER | MATCH |
| evm-osaka | groth16 | 8 | Y_app | 274,243 | [273,604, 274,882] | 0.240 % | 273,915.0 | 273,894 – 273,942 | -328.0 | -0.1196 | PASS | Ync_app | 266,098 | -328.0 | -0.1231 | 0.240 % | PASS |  |  |  |
| evm-osaka | groth16 | 12 | Y_dir | 293,498 | [292,929, 294,067] | 0.201 % | 293,201.0 | 293,165 – 293,213 | -297.0 | -0.1012 | PASS | Ync_dir | 283,362 | -297.0 | -0.1048 | 0.201 % | PASS | PLONK_COSTLIER | PLONK_COSTLIER | MATCH |
| evm-osaka | groth16 | 12 | Y_app | 302,976 | [302,273, 303,680] | 0.240 % | 302,518.0 | 302,482 – 302,530 | -458.0 | -0.1512 | PASS | Ync_app | 292,840 | -458.0 | -0.1565 | 0.240 % | PASS |  |  |  |
| evm-osaka | groth16 | 24 | Y_dir | 379,576 | [378,845, 380,306] | 0.201 % | 378,954.5 | 378,917 – 378,977 | -621.5 | -0.1637 | PASS | Ync_dir | 363,462 | -621.0 | -0.1709 | 0.201 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| evm-osaka | groth16 | 24 | Y_app | 389,182 | [388,286, 390,078] | 0.240 % | 388,455.5 | 388,418 – 388,478 | -726.5 | -0.1867 | PASS | Ync_app | 373,068 | -726.0 | -0.1947 | 0.240 % | PASS |  |  |  |
| evm-osaka | plonk | 6 | Y_dir | 297,765 | [293,538, 301,992] | 1.496 % | 297,236.5 | 295,208 – 299,062 | -528.5 | -0.1775 | PASS | Ync_dir | 282,417 | -493.5 | -0.1746 | 1.496 % | PASS | PLONK_COSTLIER | PLONK_COSTLIER | MATCH |
| evm-osaka | plonk | 6 | Y_app | 306,746 | [302,232, 311,260] | 1.549 % | 306,302.5 | 304,274 – 308,128 | -443.5 | -0.1446 | PASS | Ync_app | 291,397 | -407.5 | -0.1399 | 1.549 % | PASS |  |  |  |
| evm-osaka | plonk | 8 | Y_dir | 300,272 | [296,022, 304,521] | 1.496 % | 300,589.0 | 298,472 – 302,460 | +317.0 | +0.1056 | PASS | Ync_dir | 283,933 | +352.0 | +0.1240 | 1.496 % | PASS | PLONK_COSTLIER | PLONK_COSTLIER | MATCH |
| evm-osaka | plonk | 8 | Y_app | 309,245 | [304,708, 313,782] | 1.549 % | 309,622.0 | 307,505 – 311,493 | +377.0 | +0.1219 | PASS | Ync_app | 292,906 | +412.0 | +0.1406 | 1.549 % | PASS |  |  |  |
| evm-osaka | plonk | 12 | Y_dir | 305,296 | [301,001, 309,591] | 1.496 % | 306,431.5 | 305,070 – 308,166 | +1,135.5 | +0.3719 | PASS | Ync_dir | 286,966 | +1,167.5 | +0.4070 | 1.496 % | PASS | PLONK_COSTLIER | PLONK_COSTLIER | MATCH |
| evm-osaka | plonk | 12 | Y_app | 314,255 | [309,671, 318,839] | 1.549 % | 315,489.5 | 314,128 – 317,224 | +1,234.5 | +0.3928 | PASS | Ync_app | 295,924 | +1,267.5 | +0.4282 | 1.549 % | PASS |  |  |  |
| evm-osaka | plonk | 24 | Y_dir | 320,352 | [315,921, 324,783] | 1.496 % | 322,388.0 | 321,217 – 323,859 | +2,036.0 | +0.6356 | PASS | Ync_dir | 296,064 | +2,062.0 | +0.6966 | 1.496 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| evm-osaka | plonk | 24 | Y_app | 329,267 | [324,543, 333,991] | 1.549 % | 331,534.0 | 330,363 – 333,005 | +2,267.0 | +0.6885 | PASS | Ync_app | 304,978 | +2,294.0 | +0.7521 | 1.549 % | PASS |  |  |  |
| eravm-29 | groth16 | 6 | Y_dir | 478,976 | [478,678, 479,275] | 0.062 % | 479,055.0 | 479,055 – 479,055 | +79.0 | +0.0165 | PASS | Y_dir | 479,024 | +31.0 | +0.0064 | 0.062 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| eravm-29 | groth16 | 6 | Y_app | 486,179 | [486,020, 486,339] | 0.033 % | 486,222.0 | 486,222 – 486,222 | +43.0 | +0.0088 | PASS | Y_app | 486,227 | -5.0 | -0.0011 | 0.033 % | PASS |  |  |  |
| eravm-29 | groth16 | 8 | Y_dir | 492,862 | [492,555, 493,169] | 0.062 % | 492,923.0 | 492,923 – 492,923 | +61.0 | +0.0124 | PASS | Y_dir | 492,910 | +13.0 | +0.0027 | 0.062 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| eravm-29 | groth16 | 8 | Y_app | 500,141 | [499,977, 500,305] | 0.033 % | 500,154.0 | 500,154 – 500,154 | +13.0 | +0.0026 | PASS | Y_app | 500,189 | -35.0 | -0.0069 | 0.033 % | PASS |  |  |  |
| eravm-29 | groth16 | 12 | Y_dir | 520,632 | [520,308, 520,957] | 0.062 % | 520,812.0 | 520,812 – 520,812 | +180.0 | +0.0346 | PASS | Y_dir | 520,680 | +132.0 | +0.0253 | 0.062 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| eravm-29 | groth16 | 12 | Y_app | 528,063 | [527,890, 528,237] | 0.033 % | 528,171.0 | 528,171 – 528,171 | +108.0 | +0.0205 | PASS | Y_app | 528,111 | +60.0 | +0.0113 | 0.033 % | PASS |  |  |  |
| eravm-29 | groth16 | 24 | Y_dir | 603,944 | [603,568, 604,321] | 0.062 % | 604,272.0 | 604,272 – 604,272 | +328.0 | +0.0543 | PASS | Y_dir | 603,992 | +280.0 | +0.0463 | 0.062 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| eravm-29 | groth16 | 24 | Y_app | 611,831 | [611,631, 612,032] | 0.033 % | 612,039.0 | 612,039 – 612,039 | +208.0 | +0.0340 | FAIL | Y_app | 611,879 | +160.0 | +0.0261 | 0.033 % | PASS |  |  |  |
| eravm-29 | plonk | 6 | Y_dir | 458,221 | [449,000, 467,443] | 2.012 % | 456,305.2 | 453,894 – 458,760 | -1,915.8 | -0.4181 | PASS | Y_dir | 458,348 | -2,042.8 | -0.4456 | 2.012 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| eravm-29 | plonk | 6 | Y_app | 465,900 | [456,315, 475,485] | 2.057 % | 463,956.2 | 461,545 – 466,411 | -1,943.8 | -0.4172 | PASS | Y_app | 466,027 | -2,070.8 | -0.4443 | 2.057 % | PASS |  |  |  |
| eravm-29 | plonk | 8 | Y_dir | 463,111 | [453,791, 472,430] | 2.012 % | 461,302.5 | 458,790 – 463,488 | -1,808.5 | -0.3905 | PASS | Y_dir | 463,353 | -2,050.5 | -0.4425 | 2.012 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| eravm-29 | plonk | 8 | Y_app | 470,882 | [461,194, 480,569] | 2.057 % | 468,993.5 | 466,481 – 471,179 | -1,888.5 | -0.4011 | PASS | Y_app | 471,124 | -2,130.5 | -0.4522 | 2.057 % | PASS |  |  |  |
| eravm-29 | plonk | 12 | Y_dir | 472,849 | [463,334, 482,365] | 2.012 % | 470,509.0 | 468,322 – 472,744 | -2,340.0 | -0.4949 | PASS | Y_dir | 473,323 | -2,814.0 | -0.5945 | 2.012 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| eravm-29 | plonk | 12 | Y_app | 480,804 | [470,913, 490,696] | 2.057 % | 478,328.0 | 476,141 – 480,563 | -2,476.0 | -0.5150 | PASS | Y_app | 481,278 | -2,950.0 | -0.6129 | 2.057 % | PASS |  |  |  |
| eravm-29 | plonk | 24 | Y_dir | 502,025 | [491,922, 512,128] | 2.012 % | 495,510.0 | 493,605 – 498,171 | -6,515.0 | -1.2977 | PASS | Y_dir | 503,193 | -7,683.0 | -1.5268 | 2.012 % | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH |
| eravm-29 | plonk | 24 | Y_app | 510,532 | [500,029, 521,035] | 2.057 % | 503,713.0 | 501,808 – 506,374 | -6,819.0 | -1.3357 | PASS | Y_app | 511,700 | -7,987.0 | -1.5608 | 2.057 % | PASS |  |  |  |

### S2. Strictly unseen k ∈ {6, 8, 12, 24} — ZKsync OS v32.0 @ npg 100 (computational native N, final gas G; conditional Level-4 test ZC per proof)

| backend | k | N pred | N interval | N ± | N observed mean | N proof range | N abs err | N rel err % | P verdict (N) | ZC pass | ZC mean err % | ZC max abs err % | τ_cond % | ZC verdict | G pred [interval] | G observed | G proof range | G rel err % | P verdict (G) | predicted rank | measured rank (N) | rank verdict (N) | rank verdict (G) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| groth16 | 6 | 40,975,083 | [40,958,839, 40,991,326] | 0.040 % | 40,968,045.0 | 40,968,045 – 40,968,045 | -7,038.0 | -0.0172 | PASS | 8 / 8 | -0.0104 | 0.0104 | 0.0138 | PASS | 409,751 [409,588, 409,914] | 409,680.0 | 409,680 – 409,680 | -0.0173 | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH | MATCH |
| groth16 | 8 | 42,762,370 | [42,745,417, 42,779,322] | 0.040 % | 42,752,457.0 | 42,752,457 – 42,752,457 | -9,913.0 | -0.0232 | PASS | 0 / 8 | -0.0141 | 0.0141 | 0.0138 | FAIL | 427,624 [427,454, 427,794] | 427,524.0 | 427,524 – 427,524 | -0.0234 | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH | MATCH |
| groth16 | 12 | 46,336,944 | [46,318,574, 46,355,313] | 0.040 % | 46,321,721.0 | 46,321,721 – 46,321,721 | -15,223.0 | -0.0329 | PASS | 0 / 8 | -0.0200 | 0.0200 | 0.0138 | FAIL | 463,369 [463,185, 463,554] | 463,217.0 | 463,217 – 463,217 | -0.0328 | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH | MATCH |
| groth16 | 24 | 57,060,666 | [57,038,046, 57,083,287] | 0.040 % | 57,029,103.0 | 57,029,103 – 57,029,103 | -31,563.0 | -0.0553 | FAIL | 0 / 8 | -0.0337 | 0.0337 | 0.0138 | FAIL | 570,607 [570,380, 570,833] | 570,291.0 | 570,291 – 570,291 | -0.0554 | FAIL | PLONK_CHEAPER | PLONK_CHEAPER | MATCH | MATCH |
| plonk | 6 | 38,844,615 | [38,526,134, 39,163,096] | 0.820 % | 38,840,837.5 | 38,786,769 – 38,888,131 | -3,777.5 | -0.0097 | PASS | 8 / 8 | +0.0428 | 0.0429 | 0.4521 | PASS | 388,446 [385,261, 391,631] | 388,407.9 | 387,867 – 388,881 | -0.0098 | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH | MATCH |
| plonk | 8 | 38,911,537 | [38,592,507, 39,230,567] | 0.820 % | 38,938,756.0 | 38,884,655 – 38,988,623 | +27,219.0 | +0.0700 | PASS | 8 / 8 | +0.0589 | 0.0590 | 0.4521 | PASS | 389,115 [385,925, 392,306] | 389,387.2 | 388,846 – 389,886 | +0.0700 | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH | MATCH |
| plonk | 12 | 39,041,535 | [38,721,439, 39,361,631] | 0.820 % | 39,108,021.5 | 39,071,737 – 39,153,817 | +66,486.5 | +0.1703 | PASS | 8 / 8 | +0.0924 | 0.0925 | 0.4521 | PASS | 390,415 [387,214, 393,617] | 391,079.8 | 390,717 – 391,538 | +0.1703 | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH | MATCH |
| plonk | 24 | 39,427,683 | [39,104,421, 39,750,945] | 0.820 % | 39,570,620.0 | 39,540,589 – 39,608,859 | +142,937.0 | +0.3625 | PASS | 8 / 8 | +0.1915 | 0.1916 | 0.4521 | PASS | 394,277 [391,044, 397,510] | 395,705.6 | 395,405 – 396,088 | +0.3623 | PASS | PLONK_CHEAPER | PLONK_CHEAPER | MATCH | MATCH |

### R1. Held-out k seen in P0 (k ∈ {2, 16, 32}; weak test)

| regime | backend | metric | k | R pred | measured | err % | τ % | verdict |
|---|---|---|---|---|---|---|---|---|
| evm-osaka | groth16 | Ync_dir | 2 | 216612 | 216625 | +0.0060 | 0.201 | PASS |
| evm-osaka | groth16 | Ync_dir | 16 | 310062 | 309657 | -0.1306 | 0.201 | PASS |
| evm-osaka | groth16 | Ync_dir | 32 | 416862 | 416025 | -0.2008 | 0.201 | PASS |
| evm-osaka | groth16 | Ync_app | 2 | 225984 | 225965 | -0.0083 | 0.240 | PASS |
| evm-osaka | groth16 | Ync_app | 16 | 319583 | 318988 | -0.1862 | 0.240 | PASS |
| evm-osaka | groth16 | Ync_app | 32 | 426554 | 425530 | -0.2400 | 0.240 | PASS |
| evm-osaka | plonk | Ync_dir | 2 | 279384 | 278906.25 | -0.1710 | 1.496 | PASS |
| evm-osaka | plonk | Ync_dir | 16 | 289998 | 291505.75 | +0.5198 | 1.496 | PASS |
| evm-osaka | plonk | Ync_dir | 32 | 302129 | 304891 | +0.9142 | 1.496 | PASS |
| evm-osaka | plonk | Ync_app | 2 | 288379 | 287836.25 | -0.1883 | 1.549 | PASS |
| evm-osaka | plonk | Ync_app | 16 | 298942 | 300609.75 | +0.5578 | 1.549 | PASS |
| evm-osaka | plonk | Ync_app | 32 | 311014 | 314073 | +0.9835 | 1.549 | PASS |
| eravm-29 | groth16 | Y_dir | 2 | 451254 | 451263 | +0.0021 | 0.062 | PASS |
| eravm-29 | groth16 | Y_dir | 16 | 548451 | 548632 | +0.0330 | 0.062 | PASS |
| eravm-29 | groth16 | Y_dir | 32 | 659534 | 659944 | +0.0622 | 0.062 | PASS |
| eravm-29 | groth16 | Y_app | 2 | 458305 | 458326 | +0.0047 | 0.033 | PASS |
| eravm-29 | groth16 | Y_app | 16 | 556034 | 556113 | +0.0142 | 0.033 | PASS |
| eravm-29 | groth16 | Y_app | 32 | 667725 | 667943 | +0.0327 | 0.033 | PASS |
| eravm-29 | plonk | Y_dir | 2 | 448378 | 447635.5 | -0.1655 | 2.012 | PASS |
| eravm-29 | plonk | Y_dir | 16 | 483253 | 478713.5 | -0.9393 | 2.012 | PASS |
| eravm-29 | plonk | Y_dir | 32 | 523133 | 512225.75 | -2.0849 | 2.012 | FAIL |
| eravm-29 | plonk | Y_app | 2 | 455873 | 455134.5 | -0.1619 | 2.057 | PASS |
| eravm-29 | plonk | Y_app | 16 | 491392 | 486672.5 | -0.9604 | 2.057 | PASS |
| eravm-29 | plonk | Y_app | 32 | 532008 | 520684.75 | -2.1284 | 2.057 | FAIL |

### R2. Limit check k = 64 (descriptive)

| regime | backend | metric | k | R pred | measured | err % | τ % | verdict |
|---|---|---|---|---|---|---|---|---|
| evm-osaka | groth16 | Ync_dir | 64 | 630462 | 628761 | -0.2698 | 0.201 | DESCRIPTIVE FAIL |
| evm-osaka | groth16 | Ync_app | 64 | 640495 | 638488 | -0.3134 | 0.240 | DESCRIPTIVE FAIL |
| evm-osaka | plonk | Ync_dir | 64 | 326390 | 332712.75 | +1.9371 | 1.496 | DESCRIPTIVE FAIL |
| evm-osaka | plonk | Ync_app | 64 | 335158 | 342140.75 | +2.0833 | 1.549 | DESCRIPTIVE FAIL |
| eravm-29 | groth16 | Y_dir | 64 | 881699 | 882464 | +0.0868 | 0.062 | DESCRIPTIVE FAIL |
| eravm-29 | groth16 | Y_app | 64 | 891106 | 891499 | +0.0441 | 0.033 | DESCRIPTIVE FAIL |
| eravm-29 | plonk | Y_dir | 64 | 602893 | 582098.5 | -3.4491 | 2.012 | DESCRIPTIVE FAIL |
| eravm-29 | plonk | Y_app | 64 | 613240 | 591605.5 | -3.5279 | 2.057 | DESCRIPTIVE FAIL |

### R3. EraVM v27 transfer (H7)

| regime | backend | metric | k | R pred | measured | err % | τ % | verdict |
|---|---|---|---|---|---|---|---|---|
| eravm-27 | groth16 | Y_dir | 4 | 9601964 | 9581493.75 | -0.2132 | 0.821 | PASS |
| eravm-27 | groth16 | Y_dir | 6 | 10215506 | 10187355 | -0.2756 | 0.821 | PASS |
| eravm-27 | groth16 | Y_dir | 8 | 10829049 | 10785183.75 | -0.4051 | 0.821 | PASS |
| eravm-27 | groth16 | Y_dir | 16 | 13283220 | 13202782.5 | -0.6056 | 0.821 | PASS |
| eravm-27 | groth16 | Y_app | 4 | 9609090 | 9588620.75 | -0.2130 | 0.822 | PASS |
| eravm-27 | groth16 | Y_app | 6 | 10222709 | 10194522 | -0.2757 | 0.822 | PASS |
| eravm-27 | groth16 | Y_app | 8 | 10836328 | 10792414.75 | -0.4052 | 0.822 | PASS |
| eravm-27 | groth16 | Y_app | 16 | 13290804 | 13210263.5 | -0.6060 | 0.822 | PASS |
| eravm-27 | plonk | Y_dir | 4 | 10497234 | 10488568.75 | -0.0826 | 0.513 | PASS |
| eravm-27 | plonk | Y_dir | 6 | 10502199 | 10499328 | -0.0273 | 0.513 | PASS |
| eravm-27 | plonk | Y_dir | 8 | 10507204 | 10479390.75 | -0.2647 | 0.513 | PASS |
| eravm-27 | plonk | Y_dir | 16 | 10527104 | 10525487.75 | -0.0154 | 0.513 | PASS |
| eravm-27 | plonk | Y_app | 4 | 10504821 | 10496155.75 | -0.0825 | 0.513 | PASS |
| eravm-27 | plonk | Y_app | 6 | 10509878 | 10506979 | -0.0276 | 0.513 | PASS |
| eravm-27 | plonk | Y_app | 8 | 10514975 | 10487081.75 | -0.2653 | 0.513 | PASS |
| eravm-27 | plonk | Y_app | 16 | 10535243 | 10533446.75 | -0.0171 | 0.513 | PASS |

### P0. Prediction set P — verdict counts by frozen role (all registered evidence)

| role | status | n |
|---|---|---|
| CALIBRATION | TRANSFER-CHECK PASS | 22 |
| CALIBRATION/binding=NATIVE | TRANSFER-CHECK PASS | 2 |
| HELD-OUT-BACKEND | MISSING | 4 |
| HELD-OUT-REGIME/k-seen-in-P0 | PASS | 8 |
| HELD-OUT-REGIME/k-unseen | PASS | 8 |
| HELD-OUT-k/binding=NATIVE | FAIL | 5 |
| HELD-OUT-k/binding=NATIVE | PASS | 13 |
| HELD-OUT-k/seen-in-P0 | FAIL | 2 |
| HELD-OUT-k/seen-in-P0 | PASS | 22 |
| HELD-OUT-k/seen-in-P0-trace | FAIL | 2 |
| HELD-OUT-k/seen-in-P0-trace | PASS | 6 |
| HELD-OUT-k/strictly-unseen | FAIL | 2 |
| HELD-OUT-k/strictly-unseen | PASS | 38 |
| LIMIT-CHECK | DESCRIPTIVE FAIL | 10 |
| SEMANTIC | PASS | 30 |
| SUPPORTING-CONTROL/calibration | MISSING | 8 |
| SUPPORTING-CONTROL/held-out-k | MISSING | 4 |

### P0-F. Every P cell outside its interval

| cell | role | pred | lo | hi | measured mean | err % |
|---|---|---|---|---|---|---|
| evm-osaka|groth16|c1_ctx_k64|Y_dir | LIMIT-CHECK | 666510 | 665243 | 667776 | 664808.5 | -0.2553 |
| evm-osaka|groth16|c1_ctx_k64|Y_app | LIMIT-CHECK | 676542 | 675005 | 678080 | 674535.5 | -0.2966 |
| evm-osaka|plonk|c1_ctx_k64|Y_dir | LIMIT-CHECK | 370614 | 365729 | 375499 | 376929.75 | +1.7041 |
| evm-osaka|plonk|c1_ctx_k64|Y_app | LIMIT-CHECK | 379382 | 374191 | 384573 | 386357.75 | +1.8387 |
| eravm-29|groth16|c1_ctx_k32|Y_dir | HELD-OUT-k/seen-in-P0 | 659486 | 659075 | 659896 | 659944 | +0.0694 |
| eravm-29|groth16|c1_ctx_k64|Y_dir | LIMIT-CHECK | 881651 | 881102 | 882200 | 882464 | +0.0922 |
| eravm-29|groth16|c1_ctx_k24|Y_app | HELD-OUT-k/strictly-unseen | 611831 | 611631 | 612032 | 612039 | +0.0340 |
| eravm-29|groth16|c1_ctx_k32|Y_app | HELD-OUT-k/seen-in-P0 | 667677 | 667458 | 667895 | 667943 | +0.0398 |
| eravm-29|groth16|c1_ctx_k64|Y_app | LIMIT-CHECK | 891058 | 890766 | 891350 | 891499 | +0.0495 |
| eravm-29|plonk|c1_ctx_k64|Y_dir | LIMIT-CHECK | 599412 | 587349 | 611475 | 582098.5 | -2.8884 |
| eravm-29|plonk|c1_ctx_k64|Y_app | LIMIT-CHECK | 609759 | 597215 | 622303 | 591605.5 | -2.9772 |
| zkos-v32|groth16|c1_ctx_k16|N_dir | HELD-OUT-k/seen-in-P0-trace | 49911518 | 49891732 | 49931304 | 49890945 | -0.0412 |
| zkos-v32|groth16|c1_ctx_k24|N_dir | HELD-OUT-k/strictly-unseen | 57060666 | 57038046 | 57083287 | 57029103 | -0.0553 |
| zkos-v32|groth16|c1_ctx_k32|N_dir | HELD-OUT-k/seen-in-P0-trace | 64209814 | 64184360 | 64235269 | 64167241 | -0.0663 |
| zkos-v32|groth16|c1_ctx_k64|N_dir | LIMIT-CHECK | 92806407 | 92769617 | 92843198 | 92720553 | -0.0925 |
| zkos-v32|plonk|c1_ctx_k64|N_dir | LIMIT-CHECK | 40727663 | 40393743 | 41061583 | 41160692.25 | +1.0632 |
| zkos-v32@npg100|groth16|c1_ctx_k16|G_dir | HELD-OUT-k/binding=NATIVE | 499115 | 498917 | 499314 | 498909 | -0.0413 |
| zkos-v32@npg100|groth16|c1_ctx_k24|G_dir | HELD-OUT-k/binding=NATIVE | 570607 | 570380 | 570833 | 570291 | -0.0554 |
| zkos-v32@npg100|groth16|c1_ctx_k32|G_dir | HELD-OUT-k/binding=NATIVE | 642098 | 641843 | 642353 | 641672 | -0.0663 |
| zkos-v32@npg100|groth16|c1_ctx_k64|G_dir | HELD-OUT-k/binding=NATIVE | 928064 | 927696 | 928432 | 927205 | -0.0926 |
| zkos-v32@npg100|plonk|c1_ctx_k64|G_dir | HELD-OUT-k/binding=NATIVE | 407277 | 403937 | 410616 | 411606.38 | +1.0630 |

### E1. Signs and ratio intervals (all k, all regimes)

| env | metric | k | ratio | measured_class | all_vs_all | predicted_sign | sign_verdict | ratio_in_interval |
|---|---|---|---|---|---|---|---|---|
| evm-osaka | Y_dir | 1 | 1.358185 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| evm-osaka | Y_dir | 2 | 1.317702 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| evm-osaka | Y_dir | 4 | 1.250321 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| evm-osaka | Y_dir | 6 | 1.187374 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| evm-osaka | Y_dir | 8 | 1.135936 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| evm-osaka | Y_dir | 12 | 1.045124 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| evm-osaka | Y_dir | 16 | 0.968939 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| evm-osaka | Y_dir | 24 | 0.85073 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| evm-osaka | Y_dir | 32 | 0.763902 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| evm-osaka | Y_dir | 64 | 0.566975 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | False |
| eravm-29 | Y_dir | 1 | 1.003566 | IN-BAND | overlapping | INDETERMINATE | NOT-SCORED | True |
| eravm-29 | Y_dir | 2 | 0.991961 | PLONK_CHEAPER | separated | INDETERMINATE | NOT-SCORED | True |
| eravm-29 | Y_dir | 4 | 0.974725 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| eravm-29 | Y_dir | 6 | 0.952511 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| eravm-29 | Y_dir | 8 | 0.935851 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| eravm-29 | Y_dir | 12 | 0.903414 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| eravm-29 | Y_dir | 16 | 0.872558 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| eravm-29 | Y_dir | 24 | 0.820012 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| eravm-29 | Y_dir | 32 | 0.776165 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| eravm-29 | Y_dir | 64 | 0.659629 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | False |
| eravm-27 | Y_dir | 1 | 1.208267 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| eravm-27 | Y_dir | 4 | 1.094669 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| eravm-27 | Y_dir | 6 | 1.030624 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| eravm-27 | Y_dir | 8 | 0.971647 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| eravm-27 | Y_dir | 16 | 0.797217 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | N_dir | 1 | 1.059169 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| zkos-v32@npg100 | N_dir | 2 | 1.034487 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| zkos-v32@npg100 | N_dir | 4 | 0.989647 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | N_dir | 6 | 0.948076 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | N_dir | 8 | 0.910796 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | N_dir | 12 | 0.84427 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | N_dir | 16 | 0.786935 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | N_dir | 24 | 0.693867 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | N_dir | 32 | 0.62158 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | N_dir | 64 | 0.443922 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | False |
| zkos-v32@npg100 | Y_dir | 1 | 1.05917 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 2 | 1.034485 | PLONK_COSTLIER | separated | PLONK_COSTLIER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 4 | 0.989646 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 6 | 0.948076 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 8 | 0.910796 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 12 | 0.844269 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 16 | 0.786935 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 24 | 0.693866 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 32 | 0.62158 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | True |
| zkos-v32@npg100 | Y_dir | 64 | 0.443922 | PLONK_CHEAPER | separated | PLONK_CHEAPER | MATCH | False |

### E2. Monotonicity of the PLONK / Groth16 ratio

| env | metric | n_k | violations | verdict |
|---|---|---|---|---|
| eravm-27 | Y_dir | 5 |  | PASS |
| eravm-29 | Y_dir | 9 |  | PASS |
| evm-osaka | Y_dir | 9 |  | PASS |
| zkos-v32@npg100 | N_dir | 9 |  | PASS |
| zkos-v32@npg100 | Y_dir | 9 |  | PASS |

### E3. Crossovers

| env | metric | kstar_measured | measured_interval | predicted | verdict |
|---|---|---|---|---|---|
| evm-osaka | Y_dir | 14.279 | [14.278591649354704,14.278591649354704] | 13.99 [13.17,14.83] | PASS |
| eravm-29 | Y_dir | 1.304 | [1,1.3039765913560704] | 1.4 [<=1,3.48] | PASS |
| eravm-27 | Y_dir | 7.01 | [7.010003787841999,7.010003787841999] | 6.94 [6.48,7.4] | PASS |
| zkos-v32@npg100 | N_dir | 3.521 | [3.5214539837425227,3.5214539837425227] | 3.53 [3.14,3.92] | PASS |
| zkos-v32@npg100 | Y_dir | 3.521 | [3.5214067165554614,3.5214067165554614] | 3.53 [3.14,3.92] | PASS |

### Z1. ZKsync OS conditional model per (backend, k, relation) — all held-out proofs

Constants (scorer, registered k = 1): {"base": 1692688.705882353, "per_call": 5866.764705882353}

| backend | k | relation | n | pass | fail | mean err % | min err % | max err % | τ_cond % | unpriced opcodes |
|---|---|---|---|---|---|---|---|---|---|---|
| groth16 | 2 | ctx | 8 | 8 | 0 | -0.0028 | -0.0028 | -0.0028 | 0.0138 | — |
| groth16 | 4 | a4 | 8 | 8 | 0 | -0.0064 | -0.0064 | -0.0064 | 0.0138 | — |
| groth16 | 4 | ctx | 8 | 8 | 0 | -0.0064 | -0.0064 | -0.0064 | 0.0138 | — |
| groth16 | 4 | disc | 8 | 8 | 0 | -0.0064 | -0.0064 | -0.0064 | 0.0138 | — |
| groth16 | 6 | ctx | 8 | 8 | 0 | -0.0104 | -0.0104 | -0.0104 | 0.0138 | — |
| groth16 | 8 | a8 | 8 | 0 | 8 | -0.0141 | -0.0141 | -0.0141 | 0.0138 | — |
| groth16 | 8 | ctx | 8 | 0 | 8 | -0.0141 | -0.0141 | -0.0141 | 0.0138 | — |
| groth16 | 12 | ctx | 8 | 0 | 8 | -0.0200 | -0.0200 | -0.0200 | 0.0138 | — |
| groth16 | 16 | ctx | 8 | 0 | 8 | -0.0250 | -0.0250 | -0.0250 | 0.0138 | — |
| groth16 | 24 | ctx | 8 | 0 | 8 | -0.0337 | -0.0337 | -0.0337 | 0.0138 | — |
| groth16 | 32 | ctx | 8 | 0 | 8 | -0.0405 | -0.0405 | -0.0405 | 0.0138 | — |
| groth16 | 64 | ctx | 8 | 0 | 8 | -0.0564 | -0.0564 | -0.0564 | 0.0138 | — |
| plonk | 2 | ctx | 8 | 8 | 0 | +0.0086 | +0.0086 | +0.0086 | 0.4521 | — |
| plonk | 4 | a4 | 8 | 8 | 0 | +0.0258 | +0.0258 | +0.0258 | 0.4521 | — |
| plonk | 4 | ctx | 8 | 8 | 0 | +0.0258 | +0.0258 | +0.0258 | 0.4521 | — |
| plonk | 4 | disc | 8 | 8 | 0 | +0.0258 | +0.0258 | +0.0258 | 0.4521 | — |
| plonk | 6 | ctx | 8 | 8 | 0 | +0.0428 | +0.0428 | +0.0429 | 0.4521 | — |
| plonk | 8 | a8 | 8 | 8 | 0 | +0.0589 | +0.0589 | +0.0589 | 0.4521 | — |
| plonk | 8 | ctx | 8 | 8 | 0 | +0.0589 | +0.0588 | +0.0590 | 0.4521 | — |
| plonk | 12 | ctx | 8 | 8 | 0 | +0.0924 | +0.0923 | +0.0925 | 0.4521 | — |
| plonk | 16 | ctx | 8 | 8 | 0 | +0.1256 | +0.1255 | +0.1257 | 0.4521 | — |
| plonk | 24 | ctx | 8 | 8 | 0 | +0.1915 | +0.1913 | +0.1916 | 0.4521 | — |
| plonk | 32 | ctx | 8 | 8 | 0 | +0.2563 | +0.2560 | +0.2565 | 0.4521 | — |
| plonk | 64 | ctx | 8 | 0 | 8 | +0.5064 | +0.5060 | +0.5068 | 0.4521 | — |

### N1. `native_per_gas` intervention: binding meter and final gas (k ∈ {1, 4, 16})

| k | npg | backend | predicted_meter | measured_meter | meter_verdict | pred_gas | measured_gas | gas_in_interval |
|---|---|---|---|---|---|---|---|---|
| 1 | 100 | groth16 | NATIVE | NATIVE | PASS | 365,069 [364,923, 365,214] | 365068 | True |
| 1 | 100 | plonk | NATIVE | NATIVE | PASS | 386,831 [383,659, 390,003] | 386669.12 | True |
| 1 | 126 | groth16 | NATIVE | NATIVE | PASS | 289,737 [289,622, 289,852] | 289737 | True |
| 1 | 126 | plonk | NATIVE | NATIVE | PASS | 307,009 [304,491, 309,526] | 306880 | True |
| 1 | 139 | groth16 | NATIVE | NATIVE | PASS | 262,639 [262,535, 262,744] | 262639 | True |
| 1 | 139 | plonk | EVM_GAS | EVM_GAS | PASS | 291,490 [287,320, 295,661] | 291452.25 | True |
| 1 | 151 | groth16 | NATIVE | NATIVE | PASS | 241,767 [241,671, 241,864] | 241767 | True |
| 1 | 151 | plonk | EVM_GAS | EVM_GAS | PASS | 291,490 [287,320, 295,661] | 291452.25 | True |
| 1 | 169 | groth16 | NATIVE | NATIVE | PASS | 216,017 [215,931, 216,103] | 216016 | True |
| 1 | 169 | plonk | EVM_GAS | EVM_GAS | PASS | 291,490 [287,320, 295,661] | 291452.25 | True |
| 1 | 171 | groth16 | EVM_GAS | EVM_GAS | PASS | 214,590 [214,167, 215,012] | 214589.5 | True |
| 1 | 171 | plonk | EVM_GAS | EVM_GAS | PASS | 291,490 [287,320, 295,661] | 291452.25 | True |
| 1 | 300 | groth16 | EVM_GAS | EVM_GAS | PASS | 214,590 [214,167, 215,012] | 214589.5 | True |
| 1 | 300 | plonk | EVM_GAS | EVM_GAS | PASS | 291,490 [287,320, 295,661] | 291452.25 | True |
| 4 | 100 | groth16 | NATIVE | NATIVE | PASS | 391,878 [391,722, 392,034] | 391852 | True |
| 4 | 100 | groth16 | NATIVE | NATIVE | PASS | 391,878 [391,722, 392,034] | 391853 | True |
| 4 | 100 | groth16 | NATIVE | NATIVE | PASS | 391,878 [391,722, 392,034] | 391852 | True |
| 4 | 100 | plonk | NATIVE | NATIVE | PASS | 387,815 [384,635, 390,996] | 387737.62 | True |
| 4 | 100 | plonk | NATIVE | NATIVE | PASS | 387,815 [384,635, 390,996] | 387795.88 | True |
| 4 | 100 | plonk | NATIVE | NATIVE | PASS | 387,815 [384,635, 390,996] | 387761.88 | True |
| 4 | 125 | groth16 | NATIVE | NATIVE | PASS | 313,502 [313,378, 313,627] | 313482 | True |
| 4 | 125 | plonk | NATIVE | NATIVE | PASS | 310,252 [307,708, 312,797] | 310236.5 | True |
| 4 | 138 | groth16 | NATIVE | NATIVE | PASS | 283,970 [283,856, 284,083] | 283951 | True |
| 4 | 138 | plonk | EVM_GAS | EVM_GAS | PASS | 295,242 [291,038, 299,447] | 295205.75 | True |
| 4 | 149 | groth16 | NATIVE | NATIVE | PASS | 263,005 [262,901, 263,110] | 262988 | True |
| 4 | 149 | plonk | EVM_GAS | EVM_GAS | PASS | 295,242 [291,038, 299,447] | 295205.75 | True |
| 4 | 165 | groth16 | NATIVE | NATIVE | PASS | 237,502 [237,407, 237,596] | 237486 | True |
| 4 | 165 | plonk | EVM_GAS | EVM_GAS | PASS | 295,242 [291,038, 299,447] | 295205.75 | True |
| 4 | 167 | groth16 | EVM_GAS | EVM_GAS | PASS | 236,104 [235,642, 236,566] | 236104 | True |
| 4 | 167 | plonk | EVM_GAS | EVM_GAS | PASS | 295,242 [291,038, 299,447] | 295205.75 | True |
| 4 | 300 | groth16 | EVM_GAS | EVM_GAS | PASS | 236,104 [235,642, 236,566] | 236104 | True |
| 4 | 300 | plonk | EVM_GAS | EVM_GAS | PASS | 295,242 [291,038, 299,447] | 295205.75 | True |
| 16 | 100 | groth16 | NATIVE | NATIVE | PASS | 499,115 [498,917, 499,314] | 498909 | False |
| 16 | 100 | plonk | NATIVE | NATIVE | PASS | 391,677 [388,465, 394,889] | 392608.75 | True |
| 16 | 120 | groth16 | NATIVE | NATIVE | PASS | 415,929 [415,764, 416,095] | 415757 | False |
| 16 | 120 | plonk | NATIVE | NATIVE | PASS | 326,397 [323,721, 329,074] | 327173.75 | True |
| 16 | 132 | groth16 | NATIVE | NATIVE | PASS | 378,118 [377,967, 378,268] | 377961 | False |
| 16 | 132 | plonk | EVM_GAS | EVM_GAS | PASS | 310,318 [305,978, 314,658] | 311794.75 | True |
| 16 | 141 | groth16 | NATIVE | NATIVE | PASS | 353,982 [353,842, 354,123] | 353836 | False |
| 16 | 141 | plonk | EVM_GAS | EVM_GAS | PASS | 310,318 [305,978, 314,658] | 311794.75 | True |
| 16 | 154 | groth16 | NATIVE | NATIVE | PASS | 324,101 [323,972, 324,230] | 323967 | False |
| 16 | 154 | plonk | EVM_GAS | EVM_GAS | PASS | 310,318 [305,978, 314,658] | 311794.75 | True |
| 16 | 156 | groth16 | EVM_GAS | EVM_GAS | PASS | 322,195 [321,572, 322,818] | 321790 | True |
| 16 | 156 | plonk | EVM_GAS | EVM_GAS | PASS | 310,318 [305,978, 314,658] | 311794.75 | True |
| 16 | 300 | groth16 | EVM_GAS | EVM_GAS | PASS | 322,195 [321,572, 322,818] | 321790 | True |
| 16 | 300 | plonk | EVM_GAS | EVM_GAS | PASS | 310,318 [305,978, 314,658] | 311794.75 | True |

### N2. Ranking per level

| k | npg | ratio | measured_class | predicted_class | ratio_in_interval | verdict |
|---|---|---|---|---|---|---|
| 1 | 100 | 1.05917 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 1 | 126 | 1.059167 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 1 | 139 | 1.109707 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 1 | 151 | 1.205509 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 1 | 169 | 1.349216 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 1 | 171 | 1.358185 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 1 | 300 | 1.358185 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 4 | 100 | 0.989646 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |
| 4 | 125 | 0.989647 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |
| 4 | 138 | 1.039636 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 4 | 149 | 1.122507 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 4 | 165 | 1.243045 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 4 | 167 | 1.250321 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 4 | 300 | 1.250321 | PLONK_COSTLIER | PLONK_COSTLIER | True | MATCH |
| 16 | 100 | 0.786935 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |
| 16 | 120 | 0.786935 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |
| 16 | 132 | 0.824939 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |
| 16 | 141 | 0.881184 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |
| 16 | 154 | 0.962428 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |
| 16 | 156 | 0.968939 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |
| 16 | 300 | 0.968939 | PLONK_CHEAPER | PLONK_CHEAPER | True | MATCH |

### H6. Semantic anchors vs context-tag cell at the same k

| env | backend | anchor | k | metric | rel_diff | epsilon | verdict |
|---|---|---|---|---|---|---|---|
| eravm-29 | groth16 | c1_a4 | 4 | Y_dir | 0.0 | 0.003693 | PASS |
| eravm-29 | groth16 | c1_a8 | 8 | Y_dir | 0.0 | 0.003693 | PASS |
| eravm-29 | groth16 | c1_disc_k04 | 4 | Y_dir | 0.0 | 0.003693 | PASS |
| eravm-29 | plonk | c1_a4 | 4 | Y_dir | -0.001011 | 0.003693 | PASS |
| eravm-29 | plonk | c1_a8 | 8 | Y_dir | -0.001156 | 0.003693 | PASS |
| eravm-29 | plonk | c1_disc_k04 | 4 | Y_dir | -0.000807 | 0.003693 | PASS |
| evm-osaka | groth16 | c1_a4 | 4 | Ync_dir | 0.0 | 0.004224 | PASS |
| evm-osaka | groth16 | c1_a8 | 8 | Ync_dir | 0.0 | 0.004224 | PASS |
| evm-osaka | groth16 | c1_disc_k04 | 4 | Ync_dir | 0.0 | 0.004224 | PASS |
| evm-osaka | plonk | c1_a4 | 4 | Ync_dir | -0.000784 | 0.004224 | PASS |
| evm-osaka | plonk | c1_a8 | 8 | Ync_dir | -0.001652 | 0.004224 | PASS |
| evm-osaka | plonk | c1_disc_k04 | 4 | Ync_dir | -0.000457 | 0.004224 | PASS |
| zkos-v32@npg100 | groth16 | c1_a4 | 4 | N_dir | -1e-06 | 0.000977 | PASS |
| zkos-v32@npg100 | groth16 | c1_a4 | 4 | Y_dir | -3e-06 | 0.000977 | PASS |
| zkos-v32@npg100 | groth16 | c1_a8 | 8 | N_dir | 0.0 | 0.000977 | PASS |
| zkos-v32@npg100 | groth16 | c1_a8 | 8 | Y_dir | 0.0 | 0.000977 | PASS |
| zkos-v32@npg100 | groth16 | c1_disc_k04 | 4 | N_dir | -1e-06 | 0.000977 | PASS |
| zkos-v32@npg100 | groth16 | c1_disc_k04 | 4 | Y_dir | -3e-06 | 0.000977 | PASS |
| zkos-v32@npg100 | plonk | c1_a4 | 4 | N_dir | -0.00015 | 0.000977 | PASS |
| zkos-v32@npg100 | plonk | c1_a4 | 4 | Y_dir | -0.00015 | 0.000977 | PASS |
| zkos-v32@npg100 | plonk | c1_a8 | 8 | N_dir | -0.000318 | 0.000977 | PASS |
| zkos-v32@npg100 | plonk | c1_a8 | 8 | Y_dir | -0.000318 | 0.000977 | PASS |
| zkos-v32@npg100 | plonk | c1_disc_k04 | 4 | N_dir | -8.7e-05 | 0.000977 | PASS |
| zkos-v32@npg100 | plonk | c1_disc_k04 | 4 | Y_dir | -8.8e-05 | 0.000977 | PASS |

### A1. Accounting identities and controls

| check | env | n | not_true | values |
|---|---|---|---|---|
| AC-CTRL-cross_regime_identity | eravm-27 | 80 | 0 | {'True': 80} |
| AC-CTRL-cross_regime_identity | eravm-29 | 208 | 0 | {'True': 208} |
| AC-CTRL-cross_regime_identity | evm-osaka | 208 | 0 | {'True': 208} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg100 | 208 | 0 | {'True': 208} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg100+prio100000000 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg120 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg125 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg126 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg132 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg138 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg139 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg141 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg149 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg151 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg154 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg156 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg165 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg167 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg169 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg171 | 16 | 0 | {'True': 16} |
| AC-CTRL-cross_regime_identity | zkos-v32@npg300 | 48 | 0 | {'True': 48} |
| AC-CTRL-foreign_vk_proof | eravm-27 | 4 | 0 | {'True': 4} |
| AC-CTRL-foreign_vk_proof | eravm-29 | 10 | 0 | {'True': 10} |
| AC-CTRL-foreign_vk_proof | evm-osaka | 10 | 0 | {'True': 10} |
| AC-CTRL-foreign_vk_proof | zkos-v32@npg100 | 10 | 0 | {'True': 10} |
| AC-CTRL-foreign_vk_proof | zkos-v32@npg125 | 2 | 0 | {'True': 2} |
| AC-CTRL-foreign_vk_proof | zkos-v32@npg138 | 2 | 0 | {'True': 2} |
| AC-CTRL-foreign_vk_proof | zkos-v32@npg149 | 2 | 0 | {'True': 2} |
| AC-CTRL-foreign_vk_proof | zkos-v32@npg165 | 2 | 0 | {'True': 2} |
| AC-CTRL-foreign_vk_proof | zkos-v32@npg167 | 2 | 0 | {'True': 2} |
| AC-CTRL-foreign_vk_proof | zkos-v32@npg300 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | eravm-27 | 10 | 0 | {'True': 10} |
| AC-CTRL-out_of_field_pub | eravm-29 | 26 | 0 | {'True': 26} |
| AC-CTRL-out_of_field_pub | evm-osaka | 26 | 0 | {'True': 26} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg100 | 26 | 0 | {'True': 26} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg100+prio100000000 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg120 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg125 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg126 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg132 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg138 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg139 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg141 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg149 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg151 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg154 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg156 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg165 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg167 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg169 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg171 | 2 | 0 | {'True': 2} |
| AC-CTRL-out_of_field_pub | zkos-v32@npg300 | 6 | 0 | {'True': 6} |
| AC-CTRL-perturb_pub | eravm-27 | 70 | 0 | {'True': 70} |
| AC-CTRL-perturb_pub | eravm-29 | 370 | 0 | {'True': 370} |
| AC-CTRL-perturb_pub | evm-osaka | 370 | 0 | {'True': 370} |
| AC-CTRL-perturb_pub | zkos-v32@npg100 | 370 | 0 | {'True': 370} |
| AC-CTRL-perturb_pub | zkos-v32@npg100+prio100000000 | 2 | 0 | {'True': 2} |
| AC-CTRL-perturb_pub | zkos-v32@npg120 | 32 | 0 | {'True': 32} |
| AC-CTRL-perturb_pub | zkos-v32@npg125 | 8 | 0 | {'True': 8} |
| AC-CTRL-perturb_pub | zkos-v32@npg126 | 2 | 0 | {'True': 2} |
| AC-CTRL-perturb_pub | zkos-v32@npg132 | 32 | 0 | {'True': 32} |
| AC-CTRL-perturb_pub | zkos-v32@npg138 | 8 | 0 | {'True': 8} |
| AC-CTRL-perturb_pub | zkos-v32@npg139 | 2 | 0 | {'True': 2} |
| AC-CTRL-perturb_pub | zkos-v32@npg141 | 32 | 0 | {'True': 32} |
| AC-CTRL-perturb_pub | zkos-v32@npg149 | 8 | 0 | {'True': 8} |
| AC-CTRL-perturb_pub | zkos-v32@npg151 | 2 | 0 | {'True': 2} |
| AC-CTRL-perturb_pub | zkos-v32@npg154 | 32 | 0 | {'True': 32} |
| AC-CTRL-perturb_pub | zkos-v32@npg156 | 32 | 0 | {'True': 32} |
| AC-CTRL-perturb_pub | zkos-v32@npg165 | 8 | 0 | {'True': 8} |
| AC-CTRL-perturb_pub | zkos-v32@npg167 | 8 | 0 | {'True': 8} |
| AC-CTRL-perturb_pub | zkos-v32@npg169 | 2 | 0 | {'True': 2} |
| AC-CTRL-perturb_pub | zkos-v32@npg171 | 2 | 0 | {'True': 2} |
| AC-CTRL-perturb_pub | zkos-v32@npg300 | 42 | 0 | {'True': 42} |
| AC-CTRL-replay | eravm-27 | 10 | 0 | {'True': 10} |
| AC-CTRL-replay | eravm-29 | 26 | 0 | {'True': 26} |
| AC-CTRL-replay | evm-osaka | 26 | 0 | {'True': 26} |
| AC-CTRL-replay | zkos-v32@npg100 | 26 | 0 | {'True': 26} |
| AC-CTRL-replay | zkos-v32@npg100+prio100000000 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg120 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg125 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg126 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg132 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg138 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg139 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg141 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg149 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg151 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg154 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg156 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg165 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg167 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg169 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg171 | 2 | 0 | {'True': 2} |
| AC-CTRL-replay | zkos-v32@npg300 | 6 | 0 | {'True': 6} |
| AC-CTRL-tampered_proof | eravm-27 | 10 | 0 | {'True': 10} |
| AC-CTRL-tampered_proof | eravm-29 | 26 | 0 | {'True': 26} |
| AC-CTRL-tampered_proof | evm-osaka | 26 | 0 | {'True': 26} |
| AC-CTRL-tampered_proof | zkos-v32@npg100 | 26 | 0 | {'True': 26} |
| AC-CTRL-tampered_proof | zkos-v32@npg100+prio100000000 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg120 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg125 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg126 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg132 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg138 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg139 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg141 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg149 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg151 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg154 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg156 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg165 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg167 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg169 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg171 | 2 | 0 | {'True': 2} |
| AC-CTRL-tampered_proof | zkos-v32@npg300 | 6 | 0 | {'True': 6} |
| AC-CTRL-unknown_root_tx | eravm-27 | 10 | 0 | {'True': 10} |
| AC-CTRL-unknown_root_tx | eravm-29 | 26 | 0 | {'True': 26} |
| AC-CTRL-unknown_root_tx | evm-osaka | 26 | 0 | {'True': 26} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg100 | 26 | 0 | {'True': 26} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg100+prio100000000 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg120 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg125 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg126 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg132 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg138 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg139 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg141 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg149 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg151 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg154 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg156 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg165 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg167 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg169 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg171 | 2 | 0 | {'True': 2} |
| AC-CTRL-unknown_root_tx | zkos-v32@npg300 | 6 | 0 | {'True': 6} |
| AC-CTRL-valid | eravm-27 | 10 | 0 | {'True': 10} |
| AC-CTRL-valid | eravm-29 | 26 | 0 | {'True': 26} |
| AC-CTRL-valid | evm-osaka | 26 | 0 | {'True': 26} |
| AC-CTRL-valid | zkos-v32@npg100 | 26 | 0 | {'True': 26} |
| AC-CTRL-valid | zkos-v32@npg100+prio100000000 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg120 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg125 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg126 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg132 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg138 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg139 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg141 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg149 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg151 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg154 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg156 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg165 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg167 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg169 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg171 | 2 | 0 | {'True': 2} |
| AC-CTRL-valid | zkos-v32@npg300 | 6 | 0 | {'True': 6} |
| AC-ERAVM-frame-closure | eravm-27 | 80 | 0 | {'True': 80} |
| AC-ERAVM-frame-closure | eravm-29 | 208 | 0 | {'True': 208} |
| AC-EVM-trace-closure | evm-osaka | 208 | 0 | {'True': 208} |
| AC-STRUCT-ERAVM-precompile-counts | eravm-27 | 80 | 0 | {'True': 80} |
| AC-STRUCT-ERAVM-precompile-counts | eravm-29 | 208 | 0 | {'True': 208} |
| AC-STRUCT-EVM-precompile-counts | evm-osaka | 208 | 0 | {'True': 208} |
| AC-STRUCT-EVM-transcript-rounds | evm-osaka | 208 | 0 | {'True': 208} |
| AC-ZK-gas-rule | zkos-v32@npg100 | 416 | 0 | {'True': 416} |
| AC-ZK-gas-rule | zkos-v32@npg100+prio100000000 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg120 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg125 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg126 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg132 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg138 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg139 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg141 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg149 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg151 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg154 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg156 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg165 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg167 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg169 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg171 | 32 | 0 | {'True': 32} |
| AC-ZK-gas-rule | zkos-v32@npg300 | 96 | 0 | {'True': 96} |

### Scorer summary.json

```
{
 "AC": {
  "total": 5342,
  "failed": 0
 },
 "ZC_constants": {
  "base": 1692688.705882353,
  "per_call": 5866.764705882353
 },
 "P": {
  "TRANSFER-CHECK PASS": 24,
  "PASS": 125,
  "DESCRIPTIVE FAIL": 10,
  "FAIL": 11,
  "MISSING": 16
 },
 "R": {
  "PASS": 70,
  "DESCRIPTIVE FAIL": 8,
  "FAIL": 2
 },
 "ZC": {
  "PASS": 128,
  "FAIL": 48,
  "DESCRIPTIVE FAIL": 16
 },
 "SG": {
  "MATCH": 43,
  "NOT-SCORED": 2
 },
 "XO": {
  "PASS": 5
 },
 "NPG": {
  "PASS": 46
 },
 "NPG_rank": {
  "MATCH": 21
 },
 "MONO": {
  "PASS": 5
 },
 "SEM": {
  "PASS": 24
 },
 "n_records": 6520,
 "n_measurement_records": 2016
}
```
