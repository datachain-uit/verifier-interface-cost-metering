# 01 — Purpose, chronology and claim boundary (V2-C2, stage 1)

## 1. Purpose

F4 falsified the frozen C1 high-precision ZKsync OS claim for Groth16 (V2-D-32 / V2-D-33). The post hoc audits V2-M7A
(V2-D-39) and V2-M7B-A (V2-D-44) explain the residual with source-defined transaction / frame charges that the frozen
C1 trace model omits, plus one environment-level constant. An explanation built after seeing the Groth16 / PLONK data
can only be tested on data it has not seen. FFLONK — a third proof system whose d = 11 verifier has never been set up,
compiled, executed or measured in V2 — is the one remaining held-out backend in the registered design. C2 freezes the
extended accounting model, its single calibrated constant and the complete prediction and scoring procedure **before any
d = 11 FFLONK artifact exists**, so that the later FFLONK cells are a genuine forward test of it.

C2 does not change C1: C1, its tolerances, H4, F4, H8, its predictions, the scorer and all registered evidence are
unchanged. C2 is not described as having been pre-registered before the Groth16 / PLONK campaigns.

## 2. Chronology (UTC)

| When | Event | Record |
|---|---|---|
| 2026-10-04 09:01 (package hash time) | C1 frozen (`SHA256SUMS` `7dac8482…bfc8f`); H8 = FFLONK validation by C1 procedure R, τ_cond(F) 0.569 % | V2-D-29 |
| 2026-10-04 11:03 | registered pilot V2-MPI-PILOT-01 starts (G16 / PLONK; no FFLONK cell) | V2-D-31 |
| 2026-10-04 12:31 | V2-MPI-FULL-01 and bridge start (G16 / PLONK; FFLONK cells not run) | V2-D-33 |
| 2026-10-04 12:45–12:48 | FFLONK gate G1 not passed (power-19 ptau HTTP 403); FFLONK arm stopped; no setup run | V2-D-34; workstation `FFLONK-STOP.txt` |
| 2026-10-04 (after scoring) | F4 confirmed and extended (Groth16 k = 8 … 32) | V2-D-33 |
| 2026-10-04 15:06 | V2-M7A F4 mechanism audit (post hoc) | V2-D-39 |
| 2026-10-04 | owner: Gate A APPROVED; FFLONK doc-21 fallback approved, execution deferred | V2-D-36, V2-D-38 |
| 2026-10-05 01:32:38 | V2-M7B-A protocol and prediction frozen | `V2-M7B-heap-retrace/` |
| 2026-10-05 01:33–01:36 | V2-M7B-A re-trace of 18 frozen G16 / PLONK proofs: 9 / 9 MATCH | V2-D-44 |
| 2026-10-05 | C2 calibration (G16 / PLONK only) and engineering tests | `calibration/`, `engineering-tests/` |
| **2026-10-05 (`FROZEN-UTC.txt`)** | **C2 stage 1 frozen** | V2-D-45 |
| later | C1 doc-21 gates G1–G3 (local research ptau AMD-FF-1, setup, compile, proofs) | — |
| later | **C2 stage 2**: structural derivation, numeric predictions frozen | separate stage-2 record |
| later | registered FFLONK cells (C1 harness, unchanged), then C1 / H8 and C2 scored separately | — |

## 3. FFLONK-related material that exists at the stage-1 freeze (inventory)

| Material | Nature | Used by C2? |
|---|---|---|
| d = 11 FFLONK (c1_ff_k01 / k04 / k16 / k32): ptau, zkey, vkey, verifier, compiled artifact, proofs, any EVM / EraVM / ZKsync OS execution | **does not exist** (G1 never passed; prepared fallback jobs 101–130 never queued) | — |
| C1 doc 21 and the C1 FFLONK rows of `09-numeric-predictions/` (set P, built from P0 depth-0 traces) | frozen C1 documents | no (C1 / H8 only) |
| P0 depth-0 FFLONK diagnostics (`p0-feasibility/`: mini_d0_k1 / k2 / k4 / k16 verifiers, proofs, EVM / EraVM / ZKsync OS v31 records; pre-C1) | feasibility diagnostics, other circuit family and VM version | no — neither used nor inspected for C2 |
| harness self-test fixture `fx_ff_k04` (= the P0 mini_d0_k4 verifier; TOOLING self-test of the FULL harness on 2026-10-04, cloud workspace only) | engineering fixture, depth 0 | no — neither used nor inspected for C2 |
| `snarkjs` 0.7.5 FFLONK Solidity template (`templates/verifier_fflonk.sol.ejs`) | public template text | read for structure only (precompile targets 0x6 / 0x7 / 0x8, no EXP, one CALLDATACOPY) |

No FFLONK quantity enters any C2 parameter. C_env is calibrated on registered Groth16 / PLONK data only (`03-calibration.md`).

## 4. Model name and claim boundary

**Name.** Source-augmented ZKsync OS native-cost model (extended transaction-level accounting), short **C2-SA**. It is
**not** called source-complete: the environment-level constant C_env (1,669,012 native) is calibrated, not decomposed
from source.

**What a C2 PASS would support.** "Given the EVM-observable structure of the same proof (opcode counts, precompile calls,
keccak and copy sizes, heap-resize sequence), the verifier bytecode length and the calldata length, source-defined
ZKsync OS v0.4.0 constants plus one environment-level constant calibrated on Groth16 and PLONK predicted the
computational native of direct `verifyProof` transactions of an unseen third proof system (snarkjs FFLONK, d = 11
family, k ∈ {1, 4, 16, 32}) on ZKsync OS v32.0 at npg 100 within 0.0138 %."

**What it never supports.** Exact cost from source alone (C_env is calibrated); other ZKsync OS / VM versions; gas,
fees or other `native_per_gas` levels; the application path (manager contract); EraVM or EVM cost (C1 roles only);
other circuits, depths or proof systems; that every low-level component was observed inside ZKsync OS (the model
applies source constants to structure observed on EDR; ZKsync OS reports only the total native).
