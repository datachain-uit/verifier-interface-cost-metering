# 16 — Full protocol: CORE, VALIDATION, SUPPORTING (V2-C1, frozen; NOT run in C1)

Cell list: `configs/design-cells.csv`. Order, freshness and controls as in `03-…` §5 and `17-…`. Evidence schema
`18-…`. Scoring `19-…`. Deviations `20-…`.

## 1. CORE

1. **Grid:** Groth16, PLONK × k ∈ {1, 2, 4, 6, 8, 12, 16, 24, 32} × {EVM Osaka, EraVM v29, ZKsync OS v32.0 @ npg 100};
   cells already measured in the pilot are not re-measured, except the **bridge cells** (k = 1 and k = 4, all three
   regimes, both templates), which must reproduce the pilot (`17-…`). k = 64 cells: limit check.
2. **Per cell:** 8 roots, 8 `verifyCredential`, 8 direct `verifyProof`, controls; EDR opcode trace for every direct
   call; EraVM refund trace + callTracer frames for every direct call; ZKsync OS DEBUG native line for every transaction.
3. **`native_per_gas` intervention (primary route = operator configuration):** for k ∈ {1, 4, 16}, each level of
   `09-numeric-predictions/zkos_npg_levels.csv`; the server is restarted with `fee_native_per_gas=<level>`; same binaries, same chain
   config, same L1 state, same deployment script and the same corpus. Levels were derived from the predicted switch
   points (around: the predicted switch ± twice its half-width; between: midway between the two templates' switches;
   away: 100 and 300). k = 1 levels belong to the pilot.
4. **Robustness route (not primary):** k = 1, npg 100 with a 1e8 wei priority fee (transaction-price route). Expected:
   both templates EVM-bound (as in the smoke check). Reported only as robustness of the binding rule.

## 2. VALIDATION

| Protocol | Cells | Specific rules |
|---|---|---|
| **EraVM v27** (historical regime) | k ∈ {1, 4, 6, 8, 16} × 2 templates, anvil-zksync 0.6.11 `--protocol-version 27` | k = 1 calibration; 6 and 8 bracket the predicted crossover (≈ 7). Frame accounting of every direct call; side differences against v29 reported per frame class (outside, ecAdd, ecMul, pairing, keccak, self). Wording: "EraVM protocol version 27 on a local node (historical)" |
| **Semantic anchors** | `c1_a4`, `c1_a8`, `c1_disc_k04` × 2 templates × 3 CORE regimes | Exact relations in `05-…` §3–4; compared with the context-tag cell at the same k (H6) |
| **FFLONK** (conditional) | `c1_ff_k01/04/16/32` × 3 CORE regimes | Only after the FFLONK gate (`21-…`) and amendment AMD-FF-1; base, c are **not** re-fitted with FFLONK data; Beta status disclosed |

## 3. SUPPORTING (specified here; not scheduled)

### 3.1 Petersburg control
Cells: Groth16, PLONK × k ∈ {1, 4, 16}, EDR hardfork `petersburg`, the **same Paris-profile bytecode** as Osaka.
Purpose: Level-1 accounting under an older tariff vector (68 gas per non-zero calldata byte; Byzantium EC prices).
Prediction: `09-numeric-predictions/predictions_cells.csv` rows `evm-petersburg`; crossover ≈ 16 (`10-…`).

### 3.2 Deployment / lifecycle (no new measurement)
From registered deploy and verify costs per regime and template: break-even number of verifications
n\* = (Deploy_P − Deploy_G) / (Y_G − Y_P) where the signs make it meaningful, per k. EIP-170 / EIP-3860 / EraVM size
limits reported per k. Descriptive; no hypothesis.

### 3.3 Prover — D1 (fixed-depth domain intervention)
V1 relation at d = 10 plus 1,150 (PLONK 2¹⁵) and 1,180 (PLONK 2¹⁶) inert chained squaring constraints; Groth16 stays 2¹²
(control). Unpadded d = 10 and d = 11 as anchors. Quiet dedicated host; ≥ 10 repetitions per cell; phase timing
(witness, prove). Question: is the PLONK proving step at d = 10 → 11 caused by the domain-size doubling?

### 3.4 Prover — D3 (statistics re-analysis of V1 prover data, no new runs)
Input: V1 `research/submission/csi/generated/prover_per_round.csv` (read-only). CV per cell, IQR, percentile bootstrap
over rounds (labelled coarse for 5 PLONK rounds), within-round ratios.

### 3.5 Prover — D2 (x86 native-Linux replication), skeleton
Same pinned image for `linux/amd64` plus a bare-metal run; ≥ 20 repetitions per cell; d ∈ {5, 8, 10, 11, 15};
CPU allocations {2, 4, 8}. **Hardware: OPEN** (owner workstation checklist in the Gate-F report §12: CPU, ≥ 8 physical
cores, ≥ 32 GB RAM, native Linux, NVMe ≥ 200 GB, dedicated during runs).

## 4. Campaign completion

The full campaign ends when every scheduled cell has a complete scored attempt or a deviation record. The scorer then
runs once on all registered evidence (pilot + full). Results go to a V2-M4 report; the manuscript is not edited in
this protocol.
