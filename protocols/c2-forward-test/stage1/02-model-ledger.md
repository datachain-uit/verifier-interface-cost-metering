# 02 — Model and parameter ledger (V2-C2-SA, frozen)

Scope: ZKsync OS v32.0 (VM v0.4.0, source commit `69bc430549e88f9264066d14f2001707572c5d33`), computational native of
one direct `verifyProof` transaction (npg 100, no priority fee). Code: `code/c2_model.py`. Machine-readable: `02-model-ledger.csv`.

**N̂ = OPS + PRE + KEC + COP + CDT + DEC + HEAPB + HEAPE + CALL + C_env**

Structural inputs (all from `code/c2_structural.js`, a deterministic EDR execution of the same proof; no cost field is
written): opcode counts, precompile calls (address, input length, requested output length), KECCAK256 input sizes,
copy sizes, EXP exponent byte lengths, heap-resize events and final heap size (ZKsync OS v0.4.0 resize rule, as in
V2-M7B-A), calldata length; plus the verifier runtime bytecode length.

| # | Term | Formula | Source (pinned v0.4.0) | Kind | Calibration data | By backend | With k |
|---|---|---|---|---|---|---|---|
| 1 | OPS — opcode native | Σ_op n_op · (native(op) + STEP 20); EXP per occurrence 700 + 5,000 · exponent bytes | `evm_interpreter/src/native_resource_constants.rs` (`c3e722f4…`); EXP `instructions/arithmetic.rs:210–224` | source constants × structural counts | none | yes (trace) | yes |
| 2 | PRE — BN254 precompiles | ecAdd 58,000; ecMul 811,000; pairing 6,244,000 + 6,908,000 per pair (192 input bytes) | `basic_system/src/cost_constants.rs` (delegation coefficient 4), as pinned in C1 | source constants × structural counts | none | yes | G16 yes, PLONK / FFLONK no |
| 3 | KEC — keccak | Σ (1,150 + 3,846 · ⌈(s + 1)/136⌉) | `basic_system/src/cost_constants.rs:26–32` (C1 pin) | source × structure | none | yes | yes |
| 4 | COP — explicit copies | Σ (80 + 2 · len) over CALLDATACOPY, CODECOPY, RETURNDATACOPY, EXTCODECOPY, MCOPY (len 0 included) | `native_resource_constants.rs:74, 80`; `instructions/system.rs`, `heap.rs` | source × structure | none | yes | weak |
| 5 | CDT — calldata intrinsic | 60 · calldata bytes (2 copy + 2 × ⌈3,846/136⌉ hashing) | `basic_bootloader/src/bootloader/constants.rs:145, 154`; `transaction_flow/gas_helpers.rs:84` | source × structure | none | yes | yes |
| 6 | DEC — bytecode decommitment | 500 + 800 + 340 · ⌈(n + pad₈(n) + 8⌈n/64⌉)/64⌉, n = verifier runtime bytes | `flat_storage_model/preimage_cache.rs:363–371`; `account_cache_entry.rs:138–163`; `evm_interpreter/src/lib.rs:192, 321–328` | source × artifact size | none | yes | yes |
| 7 | HEAPB — heap bytes | 1 · final heap size (bytes) | `evm_interpreter/src/gas.rs:93–111`; `native_resource_constants.rs:69` | source × structure | none | yes | yes (PLONK) |
| 8 | HEAPE — heap-expansion events | 35 · events (each `resize_heap` call that grows the heap; CALL family: input then output region) | `utils.rs` `resize_heap_implementation`; `gas.rs:93–111`; `native_resource_constants.rs:68` | source × structure; **directly confirmed** by V2-M7B-A | none | yes | yes (PLONK) |
| 9 | CALL — external-call overhead | per precompile call: 4,000 + (80 + 2 · m if m > 0), m = min(output size, requested length); outputs ecAdd / ecMul 64, pairing 32 | `flat_storage_model/account_cache.rs:242`; `cost_constants.rs:41`; `evm_interpreter/src/interpreter.rs:446–456` | source × structure | none | yes | G16 yes |
| 10 | C_env — environment-level constant | 1,669,012 native | not source-decomposed (intrinsic transaction processing, account / frame handling not in terms 1–9) | **calibrated** | registered ZKsync OS natives of 18 Groth16 / PLONK proofs (`03-calibration.md`) | assumed no | assumed no |

Facts behind the two assumptions of term 10: C_env is the same native value for all 18 calibration proofs (2 templates,
k = 1 … 64, calldata 292 … 2,820 bytes, verifier 1,372 … 18,918 bytes) and the model with this constant reproduces the
190 non-calibration Groth16 / PLONK proofs (incl. k = 6 and the anchor and disclosure relations) exactly. Whether it
transfers to a third template is what C2 tests.

**Fixed choices (no free parameter):** native table read from the pinned source file (hash-checked); precompile
constants as in C1; no fitted per-call constant (C1's c is not used); no k-model; no FFLONK input; τ from C1.
**Gate rule:** an opcode with no source native, a precompile other than 0x6 / 0x7 / 0x8, or a pairing input that is not
a multiple of 192 makes the affected prediction NOT EVALUABLE at stage 2 (recorded before measurement; the model is not
extended).
