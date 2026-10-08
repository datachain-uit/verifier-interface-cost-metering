# V2-M7B-A — direct heap-expansion-event confirmation (protocol and prediction, frozen BEFORE any re-trace)

Frozen 2026-10-05 before the re-trace script was run and before any new trace output existed. Post hoc mechanism
confirmation of the V2-M7A audit; **not** C1 confirmatory evidence; F4 unchanged. Authorization: owner V2-M7 phase-1
adjudication ("AUTHORIZE A SMALL M7B", part A).

## 1. Prediction recorded from V2-M7A before inspection

M7A inferred, from the ZKsync OS remainders (all mod 35 = 0), the difference in heap-expansion-event counts
PLONK − Groth16 for the context-tag relation:

| k | 1 | 2 | 4 | 8 | 12 | 16 | 24 | 32 | 64 |
|---|---|---|---|---|---|---|---|---|---|
| predicted E_PLONK − E_Groth16 | 22 | 22 | 24 | 24 | 28 | 32 | 40 | 48 | 80 |

Implied auxiliary predictions (same audit): (P2) E_Groth16(k) is the same for every k (the Groth16 remainder is one
constant); (P3) after subtracting 35 × the observed event count, the M7A remainder of all 18 selected proofs (both
backends) is one and the same constant.

## 2. Proofs (fixed selection rule)

One Groth16 and one PLONK proof per k: proof `j0` of the frozen C1 corpus (`research/csi/protocols/v2/V2-C1-preregistration/
corpus/`, CORPUS-SHA256SUMS) for circuit c1_k01 (k = 1) and c1_ctx_kNN (k = 2 … 64): proof IDs `<circuit>/<backend>/j0`.
No new proof is generated. Verifier = the frozen compiled artifact of the registered campaigns (`compiled/<circuit>-<backend>.json`,
runtime sha256 checked).

## 3. Re-trace (deterministic; EVM Osaka on EDR, as in the registered EVM cells)

Hardhat 2.29.1 / EDR 0.12.0-next.23, hardfork osaka, the registered network configuration; deploy the verifier; send
`verifyProof(proof, publicSignals)` as a transaction (gasLimit 3,000,000, zero fees); `debug_traceTransaction` with
storage and memory disabled and the stack enabled (each step: pc, op, gas, gasCost, depth, memSize, stack). Raw step
logs are kept (gzip) and hashed. No ZKsync OS run, no timing.

**Determinism gate.** The re-trace's profile (steps, gas, per-opcode count and gas, precompile calls, keccak sizes,
explicit copies) must equal the frozen `evm_trace` of the same proof in the registered evidence; otherwise that proof is
reported as NOT COMPARABLE and not counted.

## 4. Counting rules (fixed now)

**Primary — ZKsync OS v0.4.0 heap-resize semantics** (`evm_interpreter/src/utils.rs` `resize_heap_implementation`:
an event = one resize call with ceil32(offset + len) > current heap size; native 35 + bytes; `gas.rs:93–111`), applied to
the observed operand sequence of the verifier frame (depth 1), with the call sites of v0.4.0:
MLOAD / MSTORE (offset, 32); MSTORE8 (offset, 1); KECCAK256, CALLDATACOPY, CODECOPY, RETURNDATACOPY, RETURN, REVERT
(offset, len) only if len > 0; MCOPY (max(dst, src), len) if len > 0; EXTCODECOPY, LOGn, CREATE / CREATE2 (offset, len),
len = 0 → no resize; CALL / CALLCODE / DELEGATECALL / STATICCALL: **two** resize calls, input region then output region
(each len = 0 → no resize). Precompiles are system hooks (no EVM frame, no heap of their own).
**Secondary — direct EVM observation:** number of steps after which EDR's memSize increases (plus the final RETURN), i.e.
EVM expansions (one per opcode).
**Consistency checks:** the primary replay's heap size after every step equals EDR's memSize at the next depth-1 step;
the final heap size equals the M7A heap words.

## 5. Decision rule

Per k: MATCH iff observed E_PLONK − E_Groth16 (primary) equals the prediction exactly. CONFIRMED iff 9 / 9 MATCH and
the determinism gate passes for all 18 proofs. Report P2 and P3. Any mismatch is recorded as such; no alternative
mechanism is fitted to make it match, and the accounting explanation is reassessed in the report.
