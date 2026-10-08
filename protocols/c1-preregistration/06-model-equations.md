# 06 — Model hierarchy and equations (V2-C1, frozen)

Code: `model/c1_model.py` (equations), `model/zkos_native_trace_model.py` (ZKsync OS native model),
`model/c1_predict.py` (a-priori predictions, set **P**), `scoring/score_c1.py` (registered procedure **R** and
scoring). Every parameter is listed in `07-parameter-ledger.csv`. The four levels are scored separately and are
never merged into one "model fit" number.

## Template structure (analytic; checked as accounting, never fitted)

| Template b | EC calls per verification | Pairing | Transcript keccak-f rounds ρ_b(k) | Precompile calls ncalls_b(k) | Calldata (direct call) |
|---|---|---|---|---|---|
| Groth16 | k ecMul + k ecAdd | 1 call, 4 pairs | 0 | 2k + 1 | 4 + 32(8 + k) bytes |
| PLONK | 18 ecMul + 18 ecAdd | 1 call, 2 pairs | ⌈(32(22 + k) + 1)/136⌉ + 7 | 37 | 4 + 32(24 + k) bytes |
| FFLONK | 5 ecMul + 7 ecAdd | 1 call, 2 pairs | ⌈(32(4 + k) + 1)/136⌉ + 7 | 13 | 4 + 32(24 + k) bytes |

ρ_b(k) was read from the snarkjs templates and checked against every P0 trace (PLONK: β-challenge keccak over the 16
vk words, k inputs and 6 proof words plus five fixed-length hashes; FFLONK analogous).

## Level 1 — accounting identities and controls (all regimes)

| ID | Identity | Role |
|---|---|---|
| L1-EVM | gasUsed = 21,000 + calldata gas + Σ_opcodes schedule + Σ_precompiles schedule (= EDR trace gas) | check, exact |
| L1-EraVM | computational gas = outside-frame cost + Σ precompile frames + self-execution (callTracer frames) | check, exact |
| L1-ZK | G = max(G_evm, ⌊N · p_native / p_gas⌋), p_gas = p_native · npg (+ priority fee) | check, ±1 gas |
| L1-STRUCT | trace/frame precompile counts equal the template counts above | check, exact |
| L1-PETERSBURG | Petersburg gas = same trace × Byzantium/Constantinople schedule (68 gas per non-zero calldata byte; ecAdd 500, ecMul 40,000, pairing 100,000 + 80,000/pair) | supporting control |

Level 1 explains nothing by itself; it guarantees that the numbers decomposed at Level 2/3 add up.

## Level 2/3 — structural explanation (within each regime)

For regime E and template b:

**Y_E,b(k) = A_E,b + B_E,b · (k − 1) + K_E · (ρ_b(k) − ρ_b(1))**

- A_E,b: cost at k = 1 (calibration cell).
- B_E,b: per-input increment, calibrated from the k = 1 and k = 4 cells only.
- K_E: tariff per keccak-f round where hashing is priced per round (EraVM 40; ZKsync OS v0.4.0 3,846 native);
  0 where it is priced per word (EVM: 6 gas/word, linear in k, part of B).
- For EVM regimes, Y is the calldata-normalised execution gas Y_nc = gasUsed − c_nz·(bytes − zeros) − 4·zeros
  (c_nz = 16 Osaka, 68 Petersburg). The predicted gasUsed adds back the exact calldata gas of the registered
  transaction (known from the frozen corpus before any run).

**Decomposition (explanation).** B_E,b = Σ_c n_c,b · τ_c,E + s_E,b, where n_c,b are the per-input template counts
(G: one ecMul, one ecAdd; P: none), τ_c,E the regime's per-call price (EVM schedule; EraVM per-call frame cost;
ZKsync OS native table), and s_E,b the compiled self-execution increment (residual). Likewise
A_P − A_G = Σ_c (n_c,P − n_c,G)|_{k=1} · τ_c,E + (s-terms). The crossover is

**k\*_E = 1 + (A_P − A_G) / (B_G − B_P)** (plus the keccak step terms; solved numerically on the model curves).

The decomposition says *which* priced components move k\*: the EC tariff appears in B_G only; the pairing and
17 extra EC calls of PLONK appear in A_P − A_G. That is the explanatory claim (H3). It is computed per regime from
that regime's own measured components; no component is transported between compilers.

**EraVM v27 transfer (H7).** A_27,b from the v27 k = 1 cell; B_27,b = B_29,b + Σ_{per-input calls} (frame_27 − frame_29),
with per-call frames measured at k = 1 in each regime (G: one ecAdd + one ecMul per input; P: no per-input EC call, so
B_27,P = B_29,P). This uses only the shared compiled bytecode (identical zksolc output in both protocol versions) and
the measured tariff difference.

**Excluded:** an EraVM model that composes self-execution from opcode/primitive microbenchmarks compiled separately
(cross-compiler composition) is not used for any prediction or claim (Gate F DROP). The P0 microbenchmarks stay
diagnostic.

## Level 4 — prediction where the binding meter is observable (ZKsync OS v32.0)

**N = T_v0.4.0(trace) + base + c · ncalls_b(k)**

- T_v0.4.0(trace) = Σ_opcodes count × (native_cost(op) + STEP 20) + Σ precompile natives (ecAdd 58,000; ecMul 811,000;
  pairing 6,244,000 + 6,908,000 per pair) + Σ keccak (1,150 + 3,846 per round) + Σ copies (80 + 2 per byte), all read
  from the VM source at the pinned commit (`toolchain/zksync-os-v0.4.0-*.rs`).
- trace = the EDR Osaka opcode trace **of the same proof** (same bytecode and calldata; the EVM arm observes it
  independently of the ZKsync OS meter).
- base, c: the only two fitted constants, **shared by all templates and all k**, see §"The two constants".
- G (gas) follows from L1-ZK. The binding meter for a cell is NATIVE if ⌊N/npg⌋ > G_evm, EVM_GAS otherwise.

Two uses:
1. **Conditional test (H4, H8; procedure R):** per proof, using its registered EVM trace; base and c re-estimated from
   the registered k = 1 G16 and PLONK cells only.
2. **A-priori numbers (set P):** the same equation evaluated on P0 EDR traces at k ∈ {1, 4}, with base and c from the
   v32.0 smoke check, then the Level-2 k-model on those natives (keccak term K = 3,846). These numbers exist so that
   every cell has a frozen numeric prediction before the pilot.

**Switch point** of the `native_per_gas` intervention for (b, k): npg\*_b(k) = N_b(k) / G_evm,b(k). Below npg\* the cell is
native-bound, above it EVM-gas-bound. The ranking at a given npg follows from both backends' G.

### The two constants

| | base | c |
|---|---|---|
| Meaning | per-transaction native not visible in the opcode trace (intrinsic transaction processing, receipt, fee transfer) | per precompile call native not in the opcode table (call frame set-up, input/output copying) |
| Calibration cells | Groth16 k = 1 and PLONK k = 1 (`c1_k01`), npg = 100 | same |
| Shared or specific | **shared** across templates and k (one pair of numbers) | shared |
| Identification | exact: two equations (G16, PLONK), two unknowns; identified because ncalls differs (3 vs 37) | same |
| Set P value | from the smoke check (P0 proof j0, P0 trace) | same |
| Procedure R value | from registered k = 1 cells: mean over j = 0…7 of (N_measured − T(trace)) per backend | same |

**Why FFLONK is legitimately held out:** no FFLONK measurement enters base, c, the native table or the model form; the
model form and both constants are frozen here before any d = 11 FFLONK cell exists; FFLONK differs from both calibration
templates in call count (13), EC mix (5 / 7) and field-arithmetic volume (≈ 7× PLONK's MULMOD count). Its prediction
uses only its own EVM trace, the published table and the two shared constants.

**Forbidden inputs for any Level-4 prediction:** the measured native or gas of the predicted cell or of any other
non-calibration cell; any FFLONK native; any ZKsync OS measurement at k ≠ 1; any post-hoc change to the native table,
to ncalls, to ρ_b or to the model form; any re-selection of calibration cells. Allowed: the EVM trace of the same proof
(independent meter) and the frozen corpus calldata.

## What each level may support

| Level | Supports | Never supports |
|---|---|---|
| 1 | "the measured numbers add up as stated" | explanation, prediction |
| 2/3 | "the crossover in E sits where E's prices of the template's operations put it" | out-of-sample accuracy claims |
| 4 | "given the trace, the published prices and two constants from k = 1, the meter is predicted within τ on held-out k and templates" | claims for other VMs, versions or templates |
