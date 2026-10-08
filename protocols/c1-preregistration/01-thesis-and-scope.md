# 01 — Thesis and scope (V2-C1, frozen)

**Status:** pre-registration artifact. Frozen at C1 (2026-10-04). Changes only through `20-deviations-policy.md`
(amendment record before any registered measurement it affects).

## 1. Thesis (bounded form)

> **For the tested verifier templates, backend-relative verification cost varies systematically with the number of
> verifier-visible public inputs and with the execution and metering regime. The environment-specific crossover
> points are explained by the verifier operation structure and the regime's metering components. Where the binding
> resource meter is independently observable, the same structural model is tested predictively on held-out
> configurations.**

Each part of the sentence maps to a registered test:

| Clause | Level | Registered test |
|---|---|---|
| "varies systematically with k and with the regime" | descriptive / Level 1–2 | H1, H2 (`02-…`), cost and sign criteria (`13-criteria.md`) |
| "crossover points are explained by operation structure and metering components" | Level 2/3 (explanatory) | H3: structural counts, component decomposition, crossover interval |
| "where the binding meter is independently observable … tested predictively on held-out configurations" | Level 4 (predictive) | H4 (ZKsync OS, trace-conditional), H5 (`native_per_gas` intervention), H8 (FFLONK held-out backend, conditional) |

"Tested verifier templates" means the snarkjs 0.7.5 Solidity verifier templates for Groth16 and PLONK (CORE), and
FFLONK (VALIDATION, conditional, snarkjs "Beta"), over BN254, generated for one relation family (`05-relation-specification.md`).

## 2. Six concepts kept separate

| Concept | Meaning in V2 | Varied? | Where it enters the model |
|---|---|---|---|
| **Verifier template / structural profile** | The code generator (snarkjs 0.7.5 template) that fixes the verifier's algorithm: which EC operations, pairings, transcript hashes and field operations it performs as a function of k | Backend factor (G16, PLONK; FFLONK conditional) | Template counts n_c,b(k), ρ_b(k), ncalls_b(k) (`06`, ledger) |
| **k** | Number of verifier-visible public inputs (the length of `_pubSignals`) | Main factor: {1, 2, 4, 6, 8, 12, 16, 24, 32}; 64 as a limit check | Every equation |
| **Cryptographic operation mix** | Counts of ecAdd, ecMul, pairing pairs, keccak-f rounds, MULMOD-class field operations per verification | Follows from template and k | Component terms (Level 2/3) |
| **Compiled self-execution** | The non-precompile execution of the compiled verifier (solc 0.8.20 EVM bytecode; zksolc 1.5.15 EraVM bytecode) | Follows from compiler + environment | Calibrated A, B per (environment, template); never composed from microbenchmarks across compilers |
| **Execution / metering regime** | Environment, protocol version and fee parameters that decide what is charged: EVM Osaka gas (EDR), EVM Petersburg gas (control), EraVM v29 / v27 computational gas (anvil-zksync 0.6.11), ZKsync OS v32.0 gas with native and pubdata meters | Regime factor | Selects the tariff vector and the binding rule |
| **Observable tariff / resource-price vector** | Per-operation prices that the regime publishes or exposes: EVM gas schedule (EIPs), EraVM per-call frame costs, ZKsync OS VM native table and `native_per_gas` | Fixed per regime; `native_per_gas` is the intervention | Spec/source parameters in the ledger |

## 3. Scope

**In scope:** synthetic records only; Merkle depth d = 11; the context-tag family plus two semantic anchors and one
disclosure variant; local single-node environments with one transaction per block (EraVM: one transaction per L1
batch, as in V1); one Groth16 key per circuit (phase 2 with one contribution and a public beacon) and deterministic
PLONK keys; the toolchain pinned in `04-toolchain-matrix.md`.

**Out of scope (no claim):**

1. Any universal statement about SNARK verification cost. Claims are bounded to the tested templates, curve (BN254),
   compilers and regimes.
2. Other template generators (gnark, halo2, Noir/Barretenberg, …), other curves (BLS12-381), recursion, aggregation,
   batch verification.
3. Live-network prices or congestion. Fees are fixed by override; no fiat-cost claims.
4. Pallet-revive / PVM; random EVM-equivalent chains; further Merkle depths; unconstrained dummy public inputs (all
   DROPPED at Gate F).
5. A cross-compiler predictive claim for EraVM built from primitive microbenchmarks (DROPPED). EraVM is modelled at
   Level 2/3 within its own compiled verifier only.
6. Security of the research keys (they are measurement keys, not production keys).
7. Prover-side results (D1/D3/D2 are SUPPORTING protocols, specified here, not run in CORE).

## 4. Terminology rules (inherited V1 stances)

- "Execution environment" vs "metering regime": an environment executes; a regime prices. EVM gas, EraVM computational
  gas and ZKsync OS gas/native are **never compared as one unit**; cross-regime comparisons are only between ratios,
  signs and crossover locations.
- EraVM results are time-bounded statements about protocol versions 29 and 27 on a local node (V1 D-106 stance).
- No "first" claims; bounded novelty wording (V1 D-104 stance).
- The context-tag binding is described by its constraint, not by analogy to a named protocol.

## 5. Evidence boundary

P0 diagnostics (`p0-feasibility/`) and the ZKsync OS v32.0 version-selection smoke check are **feasibility data**.
They calibrate the a-priori numeric predictions and size the tolerances (declared in the ledger) and are never
registered evidence. Registered evidence starts with the pilot defined in `15-pilot-protocol.md`.
