# V2-PRV-D1-01 — Fixed-depth PLONK domain intervention (protocol, FROZEN before any timing)

Status: frozen 2026-10-04; owner design choices approved (V2-D-37). Class: SUPPORTING. Supersedes the draft
`D1-domain-intervention-protocol-DRAFT.md`. **No timing has been collected under this protocol.**

## 1. Question and primary contrast

Is PLONK's observed d = 10 → 11 proving-time step associated with the evaluation-domain doubling (2^15 → 2^16) rather than
with the additional Merkle level? **Primary contrast: pad-above vs pad-below** (same d = 10 relation, +30 constraints,
PLONK domain ×2). Groth16 is the built-in control (domain 2^12 in every cell). The V1 v3 data already show the step at
the doubling boundary (D3: PLONK cpu8 median prove 9.67 s at d = 10 vs 19.02 s at d = 11, while d = 5 → 10 and
d = 11 → 15 are flat); D1 isolates it at fixed depth.

## 2. Cells (frozen artifacts, `artifacts/`; hashes `artifacts/ARTIFACTS-SHA256SUMS`, PLONK keys `artifacts/KEYS-SHA256SUMS`)

| Cell | Circuit | R1CS (Groth16 domain) | PLONK gates (domain) | Source |
|---|---|---|---|---|
| `d10` (anchor) | V1 relation d = 10 | 2,727 (2^12) | 31,602 (2^15) | V1 `CredentialVerifier_Depth10` (V2 copy, V1-manifest hashes) |
| `p1150` (pad-below) | d = 10 + 1,150 inert chained squarings | 3,877 (2^12) | 32,752 (2^15) | P0 `pad_d10_p1150.circom` (`51f6fc82…`), circom 2.1.6 |
| `p1180` (pad-above) | d = 10 + 1,180 inert chained squarings | 3,907 (2^12) | 32,782 (2^16) | P0 `pad_d10_p1180.circom` (`31542870…`), circom 2.1.6 |
| `d11` (anchor) | V1 relation d = 11 | 2,970 (2^12) | 34,077 (2^16) | V1 `CredentialVerifier_Depth11` (= C1 `c1_k01` R1CS, `670ffb5d…`) |

Keys: anchors use the V1 Groth16 keys; padded Groth16 keys = `groth16 setup` (pot16) + deterministic `zkey beacon`
(sha256("V2-D1|<circuit>|<r1cs sha256>"), 2^10). PLONK keys are deterministic from `pot16_final.ptau` (`4a64b121…`): the
anchors reproduce the V1 manifest hashes byte for byte (`bebeabf9…`, `55b85a8c…`); all four are regenerated on the Mac
inside the D1 image and must equal `KEYS-SHA256SUMS` before any timed round.

Inputs: synthetic records only (V2-D-18), `artifacts/inputs/` from `kit/d1_inputs.js` (seed "V2-D1-inputs-2026-10-04";
same construction as the C1 corpus). Padded cells use the d = 10 input plus `padSeed`. Untimed proof check: 8 / 8
(cell × backend) proofs verified off-chain with matching root (`build-records/D1-UNTIMED-PROOF-CHECK.json`). Off-host
engineering tests of the harness (one untimed dry run, 8 / 8 valid, host assertions disabled) and of the analysis script
(synthetic rows) passed; their timings are not evidence and are not kept (`build-records/D1-ENGINEERING-TEST.md`).

## 3. Host, allocation and environment

- Host: the existing MacBook Pro Mac17,2 (Apple M5) with Docker Desktop (as V1 v3); **not the workstation**.
- Allocation **cpu8**: Docker cpuset `1-8` of the Docker Desktop VM's vCPUs, 8 ffjavascript workers via the V1
  CPU-visibility adapter (byte-identical copy), 8 GiB memory, swap 0, no CPU quota, V8 heap 4,096 MiB, no network,
  artifacts and keys read-only. It is an allocation of VM vCPUs on heterogeneous cores, not 8 physical cores.
- Image: `kit/Dockerfile`, same pinned base (`node:18.20.8-bookworm-slim@sha256:f9ab18e3…830e`, `linux/arm64`) and the
  same dependency lock as V1 v3 (snarkjs 0.7.5, ffjavascript 0.3.1); image ID recorded per session.
- Host conditions (V1 v3 P9): AC power, Low Power Mode off, `caffeinate` held by the runner, no other container;
  checked at start and before and after every timed round; host samples recorded (`pmset -g therm`, load average).

## 4. Procedure

1. `kit/run-d1.sh preflight`: protocol / kit / artifact hashes, pot16 hash, P9, Docker VM (aarch64, ≥ 9 vCPUs,
   ≥ 11 GiB, cgroup v2), image build, PLONK key regeneration + hash check, adapter controls (mismatched `ZCORP_CPUS`
   and quota-only container must exit 97), container preflight (all assertions, in-process warm-up, ffjavascript
   concurrency = 8). No timing.
2. `kit/run-d1.sh campaign`: preflight again, one **untimed dry run** (all 8 configurations; values not interpreted), then
   **rounds 0–20**, one fresh container per round, all 8 configurations (4 cells × Groth16 / PLONK) per round in the
   frozen seeded order (`artifacts/schedule.csv` = ascending sha256("V2-D1-order|round=r|config")); round 0 is a
   discarded warm-up (kept). In every container: hash checks, assertions, file-cache warm-up, in-process warm-up
   (Groth16 d10, PLONK d10; discarded), then the round.
3. **20 accepted timed repetitions per backend and cell** (rounds 1–20). A round is accepted only if all 8 proofs are
   valid with the matching root, no assertion failed, no OOM kill or throttled period occurred and P9 held before and
   after. A failed round stops the session; it is rerun whole as a new attempt with `run-d1.sh resume` (attempts are
   never deleted; no silent retry).

Metrics per configuration (V1 v3 definitions): `witness_ms`, `prove_ms` (end-to-end proving call with the key path under
a warm file cache), `verify_ms` (first verify), `wall_ms`; memory and cgroup counters per container.

## 5. Analysis (pre-specified, descriptive; `kit/d1_analysis.py`, run once)

Per round: R_pad = prove(pad-above) / prove(pad-below); R_anchor = prove(d11) / prove(d10); also pad-below / d10 and
d11 / pad-above, and the same for witness and wall; per backend: per-round values, median, min–max, CV, 95 %
percentile-bootstrap interval of the median (B = 10,000, recorded seeds); share of the anchor step reproduced by the
padding contrast = (median R_pad − 1) / (median R_anchor − 1), interpreted for PLONK only (the Groth16 anchor step is
close to 1, so its share is numerically unstable and is reported but not read). Reading guide fixed in advance: a domain-doubling cause
gives PLONK R_pad ≈ PLONK R_anchor with Groth16 R_pad ≈ 1; a Merkle-level cause gives PLONK R_pad ≈ 1. No decision
threshold; results are reported as effect sizes. Never pooled with D2 or D3.

## 6. Artifact retention

If D1 enters the manuscript, the padded circuits, keys, inputs, kit and raw rows are retained in the future V2
reproducibility artifact (owner choice).

## 7. Status at freeze

READY / WAITING: everything above is frozen and verified off-host; the Mac host conditions, the image build, the key
regeneration and the container preflight can only be checked by running the runner in macOS Terminal (Docker Desktop),
which this session cannot do. Kit changes after a failed preflight are recorded as amendments before any timing.
