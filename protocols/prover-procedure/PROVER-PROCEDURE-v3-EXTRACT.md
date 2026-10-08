# Prover measurement procedure (protocol v3): public extract

This document reproduces, verbatim, the sections of the prover measurement procedure (protocol version 3) that define
the metrics, the round and schedule design, the acceptance rules, the CPU-allocation profiles, the pre-flight
assertions, the recorded metadata and the raw-data schema of the Host A prover data used in D3 and repeated by D2 on
Host B. Section numbers are those of the source protocol. Passages that concern only the development of the protocol
or other workstreams are omitted and marked […]. Provenance (source SHA-256, included line ranges, omissions):
`provenance/EXTRACTS.tsv`. The kit that implements the procedure is in `kit/`.

---

## 1. Artifact provenance: corrected circuit → proving artifacts

### 1.2 How each artifact is tied to the corrected R1CS

| Link | How it is tied | Evidence (all 11 depths) | What it does not show |
|---|---|---|---|
| Source → `.r1cs` and `.wasm` | Recompilation | `circuits/CredentialVerifier_Depth{d}.circom` compiled with circom 2.1.6 and circomlib 2.0.5 (`--r1cs --wasm --sym`) reproduces the committed r1cs **and** wasm **byte-identically** (manifest sha256). The depth files differ from the base template only in the depth parameter. | Nothing beyond the source itself (§1.1) |
| `.r1cs` → Groth16 zkey (`…_0001.zkey`) | `snarkjs zkey verify` (`zKey.verifyFromR1cs`) with the corrected r1cs and `pot16_final.ptau`. It recomputes the phase-2 initialization from r1cs + ptau and checks the recorded contribution chain. | `true` for d = 5…15 | That the contributor's randomness was destroyed. This cannot be checked, and the setup has a single contribution. |
| `.r1cs` → PLONK zkey | snarkjs 0.7.5 has **no** verify command for PLONK keys. Instead: `plonk setup` takes no contribution and is deterministic, so the key was regenerated from the corrected r1cs + `pot16_final.ptau`. | Regenerated sha256 = manifest sha256 of `data/plonk-zkeys/*` for d = 5…15, i.e. **byte identity** | Nothing beyond the ptau identity (hash-checked) |
| zkey → vkey | Export and compare | Groth16: exported vkey = `data/groth16-vkeys/*` (11/11). PLONK: exported vkey = `data/plonk-vkeys/*` (11/11), `nPublic = 1`, power 15 for d ≤ 10 and 16 for d ≥ 11 | — |
| Groth16 vkey → verifier `.sol` | Constant comparison | `contracts/Groth16LegacyVerifierDepth{d}.sol` embeds the vkey (11/11) | Deployed bytecode ↔ `.sol`. This is established at deployment (O6: bytecode keccak; O8: `staticCall` with the frozen proof) |
| Committed proofs | Verification | Groth16 and PLONK proofs verify with the vkeys; public signal = tree root (11/11 each) | — |
| Files mounted into each profile container ↔ manifest | sha256 | `shasum -c ARTIFACTS.sha256` 161/161 on the repository copy on the campaign host (2026-09-24). Required at campaign start, and for the proving artifacts inside every container before its round (§3.7). Manifest digest `9a7829fe…6f156b43be`. | — |
| `pot16_final.ptau` | sha256 only | Matches the manifest | Ceremony origin. `powersoftau verify` was not run; it is outside the circuit relation. |

**Where the checks ran:**

- **Cloud** (independent of the device): Node 22.22.2, snarkjs 0.7.5 / ffjavascript 0.3.1 / fastfile 0.0.20, circom 2.1.6, circomlib 2.0.5, r1csfile 0.0.48. Checks run there: recompilation, R1CS scan, Groth16 zkey verify, PLONK regeneration. The input files were first sha256-matched to the manifest (35/35).
- **Device** (repo `node_modules`, Node 18.20.8): vkeys, `.sol`, proofs and witness rejection.

Checks run 2026-09-24. The cloud logs are not stored in the repository; P7 re-executes all of them and stores the logs with the campaign.

### 1.3 Per-depth results

| d | R1CS constr. | Booleanity on path bits | PLONK gates | r1cs + wasm byte-identical | G16 zkey verify | PLONK zkey regen = manifest | PLONK power | G16 zkey MB | PLONK zkey MB |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 1,512 | 5/5 | 19,227 | yes | true | yes | 15 | 1.13 | 50.79 |
| 6 | 1,755 | 6/6 | 21,702 | yes | true | yes | 15 | 1.25 | 50.98 |
| 7 | 1,998 | 7/7 | 24,177 | yes | true | yes | 15 | 1.37 | 51.17 |
| 8 | 2,241 | 8/8 | 26,652 | yes | true | yes | 15 | 1.63 | 51.36 |
| 9 | 2,484 | 9/9 | 29,127 | yes | true | yes | 15 | 1.75 | 51.55 |
| 10 | 2,727 | 10/10 | 31,602 | yes | true | yes | 15 | 1.87 | 51.74 |
| 11 | 2,970 | 11/11 | 34,077 | yes | true | yes | 16 | 1.99 | 101.22 |
| 12 | 3,213 | 12/12 | 36,552 | yes | true | yes | 16 | 2.11 | 101.41 |
| 13 | 3,456 | 13/13 | 39,027 | yes | true | yes | 16 | 2.23 | 101.60 |
| 14 | 3,699 | 14/14 | 41,502 | yes | true | yes | 16 | 2.35 | 101.79 |
| 15 | 3,942 | 15/15 | 43,977 | yes | true | yes | 16 | 2.47 | 101.98 |

Every depth also passes the remaining §1.2 checks: vkey equality (both backends), `.sol` embedding, committed-proof verification, and case-C rejection.

**Key sizes co-vary with the proving domain.** The PLONK zkey grows ×1.96 at d = 10→11, exactly where the domain moves from 2¹⁵ to 2¹⁶. The Groth16 zkey grows ×1.18 at d = 7→8, where its domain moves from 2¹¹ to 2¹². §3.4 addresses this.


## 3. Prover measurement protocol

### 3.1 Metric definitions

| Metric | Definition |
|---|---|
| `input_ms` | In-process `generateInputForDepth()`: read the processed-record and tree JSON, assemble the input, write it to container-local tmp |
| `witness_ms` | `snarkjs.wtns.calculate` (wasm instantiate + witness + write `.wtns` to tmp) |
| `prove_ms` | **End-to-end latency of one snarkjs proving call**, `groth16.prove(zkeyPath, wtnsPath)` / `plonk.prove(zkeyPath, wtnsPath)`, under a warm file cache. It includes opening the zkey, parsing its header, and reading the key sections the prover needs. It is **not** a measurement of the proving computation alone. |
| `verify_first_ms` | First `verify` call with the in-memory vkey |
| `verify_steady_ms` | Median of 3 further back-to-back `verify` calls |
| `stage_sum_ms` | `input_ms + witness_ms + prove_ms + verify_first_ms`. A **derived diagnostic quantity**, not "total time". |
| `wall_ms` | **End-to-end wall-clock latency of the complete pipeline**: from immediately before the input stage to immediately after `verify_first` returns, including the glue I/O between stages (for example, reading the generated input file). It excludes the `gc()` before the pipeline, the steady-state verifies, validation checks and row writing. |
| `zkey_bytes` | Size of the key file used (recorded per row) |

**Totals.** […] `stage_sum_ms` and `wall_ms` are both kept in every raw row and never merged; the summary script checks that `stage_sum_ms` equals the sum of the four stage metrics and that `wall_ms` ≥ `stage_sum_ms`.

**No stage is assumed to be, or not to be, sensitive to the CPU allocation.** Every stage is measured in every profile, and the data decide.

**Library and runtime facts that shape the design** (snarkjs 0.7.5, ffjavascript 0.3.1, fastfile 0.0.20, binfileutils 0.0.12, Node 18.20.8 / libuv 1.44.2):

- **Every proving call re-reads the zkey** (`groth16Prove` L893, `plonk16Prove` L8254). It uses a new fastfile descriptor with a 32 MB page cache. Only the kernel page cache persists between calls. PLONK reads lazily, interleaved with computation, so key loading is not a separable prefix of the call (§3.4).
- **Worker count.** ffjavascript starts `min(os.cpus().length, 64)` workers when it builds the bn128 curve. Two facts were verified in the pre-flight (§4.3):
  - inside a container, `os.cpus()` lists every CPU of the Linux VM (10), whatever the cpuset;
  - a CPU quota changes neither `os.cpus()` nor `availableParallelism()`.

  The **CPU-visibility adapter** (`bench/lib/cpu-visibility.js`, loaded with `--require`) is therefore part of the benchmark harness. It:
  - reads the effective cpuset;
  - aborts (exit 97) unless the cpuset size, the scheduler-affinity size and `ZCORP_CPUS` agree;
  - makes `os.cpus()` return exactly the entries of the cpuset CPUs;
  - exposes the values it used as a frozen global for recording;
  - changes nothing else (no prover code, timers, filesystem or other API).

  Its sha256 is recorded in `CAMPAIGN.json`. Pre-flight version: `749eea66…`.
- **Curve cache and load order.** The curve and its worker pool are cached per process in `globalThis.curve_bn128`. Loading snarkjs also loads `r1csfile`, whose nested ffjavascript 0.3.0 resets that cache at load time. The harness must therefore:
  - `require('snarkjs')` before anything builds a curve;
  - run the in-process warm-up;
  - then record `globalThis.curve_bn128.tm.concurrency`, i.e. the pool snarkjs actually uses, and assert it equals `ZCORP_CPUS`.
- **Heap limit.** V8's default heap limit follows the container memory limit, so it is pinned with `--max-old-space-size=4096` in every profile. The pre-flight recorded 4144 MiB.

### 3.2 Structure: rounds × profiles

1. **Campaign pre-flight** (P5, P6, P7) on the host and in one container per profile.
2. **One container per (round, profile).** Every round runs all three profiles, one after another. Each profile runs in a fresh container, i.e. a fresh `node --expose-gc` process.
   - **Profile order.** The positions of `cpu2`/`cpu4`/`cpu8` within each round come from a pre-generated, position-balanced schedule: cyclic Latin-square rows, with a seeded choice of row order for each block of three rounds. In every block of three rounds, each profile occupies each position once. A final partial block (round 10, and the fifth diagnostic round) takes a seeded subset of rows.
   - **Freezing.** The schedule file and its seed are committed before the campaign (`prover/schedule.csv`).
   - **Exclusivity.** Only one benchmark container runs at a time, and no other container runs.
3. **Inside each container:**
   - (a) container pre-flight assertions (§3.7);
   - (b) warm the file cache by reading all key files once;
   - (c) `require('snarkjs')`, then the in-process warm-up (discarded): one Groth16 d = 5 pipeline and one PLONK d = 5 pipeline;
   - (d) record the ffjavascript concurrency;
   - (e) run the round's configurations in a **seeded random order**. Seed = round number, so a round has the same configuration order in every profile;
   - (f) `global.gc()` before each measured pipeline;
   - (g) one raw row per pipeline;
   - (h) at exit, record the container's `memory.peak`, `memory.events` and `cpu.stat`.
4. **Round 0,** discarded but kept (`is_warmup=1`): one full sweep of all 22 configurations in each profile.
5. **Rounds 1…10.** Rounds 1–5 contain all 22 configurations; rounds 6–10 contain only the 11 Groth16 configurations (§3.3).
6. **Then the diagnostic block** (§3.4).
7. **Splitting the campaign.** The campaign may be split across sessions only between complete rounds, never inside a round. Host state is recorded at every restart. Implemented as round-level resume (§3.2.1).

#### 3.2.1 Sessions, attempts and round-level resume (operational; 2026-09-25)

- **Unit.** A round unit is one (kind, round) of the frozen schedule, primary or diagnostic, **with all its profiles**. It is atomic: a session never resumes inside a profile or inside a round. Units run in schedule order: primary rounds 0–10, then diagnostic rounds 1–5.
- **Attempt.** Each execution of a unit is an attempt (`round_attempt` = 1, 2, …). Every raw row carries `campaign_id`, `session_id`, `round`, `round_attempt`, `profile_id` and `container_id` (§7.2).
- **Acceptance.** After the last profile of an attempt, `bench/validate_round.js` accepts the attempt only if every scheduled profile completed with one container record; all expected rows exist in the scheduled configuration order (and, for diagnostic rounds, call order); every proof is valid with the committed root and input; no OOM kill, throttled period, container-assertion or artifact failure occurred; CPU counts, cpuset, memory and swap limits and image match the profile; the profiles ran in the scheduled order; and this session's container pre-flight and adapter controls passed. The outcome is appended to `prover/round_ledger.csv` (`complete`, accepted; or `failed`).
- **Session.** Every invocation of the runner is a new session (`S<UTC>`), recorded with its start and end in `environment/sessions.csv` (git HEAD, image, Docker Desktop, Engine, kernel, VM size, power source, Low Power Mode, caffeinate).
- **Restart.** A resumed session (`bash bench/run-campaign.sh resume <campaign-dir>`) re-runs the host checks (including P9 in campaign mode) and the container pre-flight and adapter controls for every profile. It **refuses to continue** if any of the following differ from `CAMPAIGN.json`: campaign ID; git commit; uncommitted state of the campaign paths; artifact manifest; adapter; runner, Compose file and Dockerfile; benchmark image ID (tag `zcorp-bench:<campaign_id>`); Docker Desktop, Engine, LinuxKit kernel, VM vCPUs and memory (checked by the runner); protocol version, harness files in the image, schedule and execution plan (checked by `bench/campaign_state.js`).
- **Interrupted attempts.** Rows of an attempt without a ledger outcome (for example after a crash or power loss) are recorded as `incomplete` and preserved as evidence. They are never continued or overwritten. The whole unit is rerun as a new attempt.
- **Accepted units** are never rerun: the harness refuses (exit 7) to write rows for a unit that has an accepted attempt, or for an attempt that is not newer than every recorded one.
- **Summaries** use only the accepted attempt of each unit (`derived/validation.json` lists the ledger; the derived files list the round attempts used). Rows of failed or incomplete attempts are kept, never summarised.
- **Planned stop.** `ZCORP_STOP_AFTER_ROUNDS=N` ends a session cleanly after N accepted units. `ZCORP_TEST_INTERRUPT_AFTER_CONTAINERS` (simulated crash) is refused outside dry runs.

### 3.3 Repetitions and pairing

**R = 10 for Groth16 and R = 5 for PLONK, in every profile.** The precision rationale […]:

- Groth16 depth effects are small, and its pipelines are cheap.
- PLONK rounds are expensive, and five rounds give five paired ratios per profile.

No decision is attached to any number.

**Pairing rules:**

- **Cross-backend comparisons use only rounds 1–5.** Both backends' pipelines for depth d in round r run in the same container. Per-round ratio: PLONK_{r,p}(d) / Groth16_{r,p}(d), for each profile p.
- **Profile comparisons are paired by round.** All three profiles of round r run consecutively, in balanced positions. Per-round speedups are:
  - S_{r}(n) = T_{r,cpu2} / T_{r,cpun}, for n = 4, 8;
  - doubling ratios T_{r,cpu2}/T_{r,cpu4} and T_{r,cpu4}/T_{r,cpu8}.

  These are computed for every (backend, stage, depth), with rounds 1–5 for both backends.
- **Groth16 rounds 6–10** are used only in Groth16-specific depth analyses within each profile. Those analyses use rounds 1–10 and also report rounds 1–5 and 6–10 separately, because rounds 6–10 run without PLONK in the process.

### 3.4 zkey-loading diagnostic ([…] run in every profile)

**What can and cannot be separated without modifying the prover** […]:

- **Separable:** the file-system read component. The unchanged `snarkjs.{groth16,plonk}.prove` accepts the key bytes preloaded in memory, through fastfile's in-memory backend.
- **Not separable:** header parsing, and copying key sections into the prover's buffers.

`prove_ms` stays end-to-end. **No causal claim about the proving domain is made:** domain size, key size, FFT sizes and buffer sizes all change together at d = 10→11.

**Diagnostic block** (after primary rounds 1–10):

- **Rounds.** Five diagnostic rounds. Each round runs all three profiles in balanced positions, one fresh container each.
- **Configurations.** PLONK d ∈ {5, 10, 11, 15}; Groth16 d ∈ {5, 7, 8, 15}.
- **Per configuration:** witness once, untimed. Then two proving calls in seeded, balanced order:
  - `path`: exactly the primary call;
  - `mem`: `fs.readFileSync(zkeyPath)` immediately before, timed as `zkey_readfile_ms`, then `prove(zkeyBytes, wtnsPath)`.

  `global.gc()` before each call. Both proofs verified, untimed.
- **Rows** go to `diag.csv`. They never enter the primary summaries.

The file-read share is not assumed to be the same in every profile. It is measured in each one.

### 3.5 Pre-specified descriptive quantities (no decision thresholds)

All quantities are computed from raw rows only; warm-up rows are excluded. Each is reported as its per-round values, their median and their min–max. **Nothing is compared against a pass/fail threshold.**

**Per (profile, backend, depth, stage):**

- n, median, Q1, Q3, IQR, min, max;
- rounds 1–5 for cross-backend and cross-profile outputs;
- rounds 1–10 for Groth16-specific depth outputs.

**PLONK, per profile, rounds 1–5.** L = {5…10}, U = {11…15}.

- A_r = prove_r(11)/prove_r(10);
- S_r = median_U / median_L;
- within-plateau adjacent ratios (5 pairs in L, 4 in U), with their distribution;
- plateau-end ratios prove_r(10)/prove_r(5) and prove_r(15)/prove_r(11), next to the structural growth over the same ranges: gates +64 % / +29 %; key size +1.9 % / +0.8 %.

**Groth16, per profile, rounds 1–10** (plus the 1–5 and 6–10 split):

- prove_r(15)/prove_r(5);
- all adjacent ratios;
- the boundary ratio prove_r(8)/prove_r(7);
- the plateau ratio with L = {5,6,7} and U = {8…15};
- the within-plateau adjacent distribution.

**Cross-backend, per profile, rounds 1–5:** per depth, PLONK_r(d)/Groth16_r(d) for prove and for `wall_ms` (the pipeline total). Report the range of the per-depth medians.

**Resource scaling, rounds 1–5, per (backend, stage, depth).** Stages are input, witness, prove and verify_first; the total is `wall_ms`. `stage_sum_ms` is reported only as a diagnostic.


- S_r(4) and S_r(8) relative to `cpu2`;
- both doubling ratios;
- their median and min–max over rounds;
- their median and min–max over depths, per backend and stage. […]

Also reported:

- whether the PLONK A_r and S_r and the Groth16 quantities differ between profiles. Described, not tested.
- the ffjavascript concurrency and per-container `memory.peak`, as recorded facts.

**Verification:** verify_first and verify_steady medians per profile, and the distribution of the per-run first/steady ratio.

**Diagnostic, per (profile, backend, depth):**

- median `path` and `mem`;
- the paired difference and ratio;
- `zkey_readfile_ms`;
- A_r^path and A_r^mem;
- plateau-end ratios under both call types.

### 3.6 How results are worded

- **Effect sizes, not verdicts.** Template (placeholders, not results): "on `cpu8`, prove(d11)/prove(d10) was ⟨median⟩ (range ⟨min⟩–⟨max⟩ over five paired rounds)".
- **Scaling.** Scaling is described only from the measured speedups. No stage is labelled parallel or sequential in advance. Where a speedup is within its round-to-round spread, the spread is reported alongside it.
- **Profiles are named as allocations.** Wording: "`cpu4`: 4 allocated vCPUs (cpuset), 4 ffjavascript workers, 8 GiB, on the named host". Never "a 4-core server" or any hardware class.
- **PLONK step.** Described as coinciding with the domain and key-size change. The `path − mem` difference is reported as the measured file-read component.
- […]
- **Totals** are `wall_ms` (§3.1). A figure or table that shows `stage_sum_ms` names it explicitly and says why.

### 3.7 Pre-flight assertions (runner and container abort on failure)

**Campaign start and every resumed session** (host runner):

- `shasum -c ARTIFACTS.sha256`: all OK; the digest is recorded.
- P7 provenance checks pass.
- `docker info`: arch `aarch64`, cgroup v2, NCPU ≥ 9, VM memory ≥ 11 GiB visible (≥ 12 GiB configured); Resource Saver not enabled where Docker Desktop exposes the setting.
- The benchmark image digest and platform (`linux/arm64`) match `CAMPAIGN.json`.
- No other container is running.
- Host conditions (P9) are recorded, and enforced in `preflight` and `campaign` mode (AC power, Low Power Mode off, `caffeinate` verified by PID and power assertion); in `campaign` mode also before every container.
- On resume, the identity checks of §3.2.1.

**Every container, before its round** (checks demonstrated in the pre-flight, §4.3):

- `cpuset.cpus.effective` equals the profile's cpuset (`1-2`, `1-4`, `1-8`);
- `cpu.max` = `max 100000` (no quota);
- `memory.max` = 8589934592 and `memory.swap.max` = 0;
- adapter present, and `os.cpus().length` = `availableParallelism()` = `ZCORP_CPUS`;
- ffjavascript concurrency of the snarkjs pool = `ZCORP_CPUS`;
- `process.arch` = `arm64`, machine = `aarch64`, CPU implementer = `0x61` (no emulation);
- `memory.events.oom_kill` = 0 and `cpu.stat.nr_throttled` = 0, before and after the round;
- V8 heap limit recorded;
- sha256 of the zkeys, wasm and vkeys used = manifest;
- versions: Node 18.20.8, snarkjs 0.7.5, ffjavascript 0.3.1, fastfile 0.0.20;
- at d = 5 and d = 11 for both backends, `prove(zkeyBytes, wtnsPath)` returns a proof that verifies with public signal = root. Diagnostic call path only, untimed, once per campaign.

**Controls, once per campaign:**

- a container with a mismatched `ZCORP_CPUS` must exit 97;
- a quota-only container (no cpuset) must exit 97.

## 4. Execution environment and resource profiles

### 4.1 The experimental factor

| Profile | cpuset (VM vCPUs) | ffjavascript workers | Memory | Swap | CPU quota |
|---|---|---|---|---|---|
| `cpu2` | 1–2 | 2 | 8 GiB | 0 | none |
| `cpu4` | 1–4 | 4 | 8 GiB | 0 | none |
| `cpu8` | 1–8 | 8 | 8 GiB | 0 | none |

- **One variable changes.** Only the number of allocated vCPUs changes, with the worker count matched to it. The image, kernel, Node, packages, keys, memory limit, heap limit, host and procedure stay fixed.
- **Why powers of two.** In ffjavascript 0.3.1, the FFT mix/join routines round the worker count down to a power of two (`nChunks = 1 << log2(tm.concurrency)`).
- **Why vCPU 0 is excluded.** It is left to the VM and the Docker daemon.
- **Fallback, if `cpu8` ever fails the §3.7 assertions:** `cpu1` (1), `cpu2` (1–2) and `cpu4` (1–4). Profile sizes are **not** derived from the host's core types, because the VM's vCPUs cannot be pinned to physical cores.

### 4.2 Campaign host and runtime (real-host pre-flight, 2026-09-25)

| Item | Value |
|---|---|
| Host | MacBook Pro, `Mac17,2`, Apple M5 |
| CPU cores | 10: 4 "Super" (perflevel0) + 6 Efficiency (perflevel1) |
| RAM | 32 GiB |
| macOS | 26.6.2 (build 25G83) |
| Container runtime | Docker Desktop **4.92.0** (updated from 4.90.0 during the resource change); Engine 29.8.0; containerd v2.3.5; runc 1.5.1; docker-init 0.19.0; context `desktop-linux`; containerd image store; Docker Desktop CLI plugin v0.4.4 |
| Linux VM | LinuxKit kernel 7.0.12-linuxkit, `aarch64`, cgroup v2 (cgroupfs driver); **10 vCPUs; 15.60 GiB visible**; `MemoryMiB` = 16384 in `settings-store.json` |
| VM manager, Rosetta, file-sharing implementation, Resource Saver | **Not exposed.** `settings-store.json` (4.92.0) contains no keys for them, and the Docker Desktop CLI plugin reports only engine status. Not recorded, and not inferred. Resource Saver can only pause an idle VM; the runner starts containers back to back. |
| Base image | `node:18.20.8-bookworm-slim`, index digest `sha256:f9ab18e354e6855ae56ef2b290dd225c1e51a564f87584b9bd21dd651838830e`; `linux/arm64/v8` manifest digest `sha256:0cc5f8897ffbf799d16ffe58bf3ce6242d23e5f9aa658e55b8d5ca8fc7f01bad`; Debian 12 |
| Benchmark image | `zcorp-bench:v3`, built from `bench/` (image ID recorded per campaign in `CAMPAIGN.json`; dry run: `sha256:7cde9e10…a113a20`) |
| Runtime in container | Node 18.20.8 (libuv 1.44.2, V8 10.2.154.26-node.39) |
| Packages in container | snarkjs 0.7.5, ffjavascript 0.3.1, fastfile 0.0.20, binfileutils 0.0.12, r1csfile 0.0.48, circom_runtime 0.1.28, circom2 0.2.16 (circom 2.1.6), circomlib 2.0.5 — from `bench/package-lock.json` |

#### 4.2.1 Software environment freeze (2026-09-25) and author operational requirements

| Frozen item | Value | Checked |
|---|---|---|
| Docker Desktop | 4.92.0 | every session (runner; `CAMPAIGN.json` → `environment.docker_desktop`) |
| Docker Engine | 29.8.0 | every session |
| Linux VM kernel | 7.0.12-linuxkit | every session |
| VM size | 10 vCPUs; 16,745,824,256 bytes visible; `MemoryMiB` 16384 configured | every session |
| Base image | `node:18.20.8-bookworm-slim`, index `sha256:f9ab18e3…830e`, `linux/arm64` manifest `sha256:0cc5f889…7f01bad` | image build (digest-pinned `FROM`); arm64 digest recorded in `CAMPAIGN.json` |
| Benchmark image | built from `bench/` at tag `rerun-baseline-20260925`; image manifest `sha256:257d9d8a106dcb9efc1768136119106e88e314d6779be543bdbe49e3b267e5a5`, config `sha256:3f3ad4add97c954e9492e621f9844671c0ccf0ae51495c1fef0d09af0d2d32ab` (identical in every build of this kit on 2026-09-25; recorded in each session's `docker-build-<S>.log`). The ID Docker reports for a build (`sha256:db35885d…2dac3` for `preflight-20260925T041734Z`) is the digest of a manifest list that also holds a BuildKit provenance attestation with a build timestamp, so it differs per build; each campaign records its own in `CAMPAIGN.json` and keeps that image under the tag `zcorp-bench:<campaign_id>` | every session (per-build ID via tag `zcorp-bench:<campaign_id>`) |
| Kit | adapter `749eea66…`; runner, Compose file, Dockerfile and harness files by sha256 | every session |

**No software updates between rounds or sessions**: not macOS, not Docker Desktop, not the Engine, kernel or VM resources, and no `docker` pruning of the campaign image. A resumed session with a different Docker Desktop, Engine, kernel, VM size or image is refused (§3.2.1); a changed environment means a new campaign, not a resumed one.

**Other author requirements for the campaign:** start from tag `rerun-baseline-20260925` without new commits until the campaign ends (a different git commit refuses resume); do not modify the campaign paths; keep the Mac on AC power with Low Power Mode off, other applications closed and no other container running (enforced at the start of every session; power and thermal state recorded before and after every container); do not edit files in the repository while a session runs (the whole-tree `git status` is compared before and after each session).

### 4.3 Pre-flight results (untimed; campaign `dryrun-20260925T021823Z`, `environment/preflight/`)

| Check | `cpu2` | `cpu4` | `cpu8` |
|---|---|---|---|
| `cpuset.cpus.effective` | 1-2 | 1-4 | 1-8 |
| `cpu.max` | max 100000 | max 100000 | max 100000 |
| `memory.max` / `memory.swap.max` | 8 GiB / 0 | 8 GiB / 0 | 8 GiB / 0 |
| `os.cpus()` before → after adapter | 10 → 2 | 10 → 4 | 10 → 8 |
| `availableParallelism()` | 2 | 4 | 8 |
| ffjavascript concurrency (pool used by snarkjs) | 2 | 4 | 8 |
| Arch / machine / CPU implementer | arm64 / aarch64 / 0x61 | arm64 / aarch64 / 0x61 | arm64 / aarch64 / 0x61 |
| OOM kills / throttled periods | 0 / 0 | 0 / 0 | 0 / 0 |
| V8 heap limit | 4144 MiB | 4144 MiB | 4144 MiB |
| Repository mount | read-only (EROFS) | read-only (EROFS) | read-only (EROFS) |
| `memory.peak` after the pre-flight proofs (incl. page cache) | 748 MiB | 882 MiB | 1122 MiB |
| Untimed proofs: Groth16 d = 5, PLONK d = 10, 11 (key path); Groth16 d = 5, 11 and PLONK d = 5, 11 (key in memory) | all verify | all verify | all verify |

For every proof in every profile the public root equals the committed public signal, the in-process input equals the committed input, and a shifted root is rejected.

**Controls:**

| Control | Result |
|---|---|
| cpuset 1–2 without the adapter | `os.cpus()` = 10, `availableParallelism()` = 2, **ffjavascript 10 workers** |
| cpuset 1–2 with `ZCORP_CPUS=4` | Adapter abort, exit 97 |
| `--cpus=2` quota without cpuset (effective cpuset 0–9) | Adapter abort, exit 97 |

**P7** passed for all 11 depths in the same run (161/161 manifest entries; R1CS byte-identical with circom 2.1.6 as WebAssembly; wasm witness-equivalent; Groth16 `zkey verify`; PLONK regeneration byte-identical; vkeys, verifier contracts and committed proofs).

### 4.4 Limitations specific to this host and runtime

- **Heterogeneous cores, unpinnable vCPUs.** The M5 has 4 performance ("Super") and 6 Efficiency cores. macOS schedules the VM's vCPU threads, and they cannot be pinned.
  - `cpu8` keeps 8 vCPUs busy on a 10-core host with only 4 performance cores, so part of its work necessarily runs on Efficiency cores.
  - The placement of `cpu2` and `cpu4` is also not guaranteed.

  The factor is therefore **allocated vCPUs on this heterogeneous host**, not a count of identical cores. ffjavascript splits work evenly across workers, so slower cores can bound a phase. This is described, not corrected.
- **Host headroom.** With 10 vCPUs on 10 physical cores, `cpu8` leaves about two cores for macOS, the VM kernel and the Docker daemon. Hence the idle-host conditions (P9).
- **Laptop power and thermals.** Recorded per (round, profile), not controlled (P9).
- **Memory.** Resolved 2026-09-25: the VM has 15.60 GiB visible, above the 8 GiB container limit.
- **What the image does not pin.** The kernel and VM manager belong to Docker Desktop (4.92.0 for this campaign), not to the image. They are recorded and frozen by the author for the campaign (§4.2.1), and the runner refuses to resume if Docker Desktop, the Engine or the kernel changed; the VM manager is not exposed and is not recorded.
- **Architecture.** `linux/arm64` only. There is no x86 emulation, and nothing is generalized to x86.

### 4.5 Optional engineering checks (artifact package only; not part of the factor, figures or tables; never blocking)

- **A host-native run** (macOS arm64, Node 18.20.8, `ZCORP_CPUS=8` set explicitly, since macOS has no cpuset). It is a sanity check of the VM + Linux + container stack, not of container overhead alone.
- **A native `linux/amd64` replication** on any x86 Linux host, using the same Compose profiles. Report it separately and never pool it.

### 4.6 Metadata recorded per campaign

- **`host.json`:** model, chip, core counts per type, RAM, macOS version, power source and Low Power Mode state.
- **`vm.json`:** runtime and version, VM manager, vCPUs, memory, kernel, cgroup version, Resource Saver setting.
- **`image.json`:** base index digest, built image digest, platform, package versions, lockfile sha256.
- **`profile-<p>.json`:** the container pre-flight record (§3.7), in the format of `preflight.js`.
- **Per (round, profile) container,** in `rounds.csv`: container ID, start/end UTC, host load average, `pmset -g therm`, `memory.peak`, `oom_kill`, `nr_throttled`, ffjavascript concurrency.
- **Per session** (implemented file names): `environment/sessions.csv`; `host-<S>.txt`; `p9-<S>.json`; `pmset-assertions-<S>.txt`; `docker-desktop-settings-<S>.txt`, `docker-desktop-cli-<S>.txt`, `docker-version-<S>.json`, `docker-info-<S>.json`; `preflight/<S>/profile-<p>.json`, `controls.json`; `manifest-{before,after}-<S>.txt`; `git-status-{before,after}-<S>.txt`, `git-status-campaign-paths-<S>.txt`; `integrity-<S>.json`; `RESULT-<S>.txt`; `prover/sessions/<S>/units.csv`.
- **Per round attempt:** one row in `prover/round_ledger.csv`.

## 7. Raw-data schema, anti-mixing […]

### 7.1 Directory layout

```
results/postcorr-<YYYYMMDD>/
  CAMPAIGN.json            campaign_id, commit, baseline tag, ARTIFACTS.sha256 digest,
                           protocol version "v3", dates, base-image and built-image digests,
                           adapter sha256, schedule and layer-order file sha256s,
                           […]
  provenance/              P7 logs: recompilation hashes, booleanity scan, G16 zkey verify,
                           PLONK regeneration hashes, vkey/.sol/proof checks
  environment/host.json, vm.json, image.json
  environment/preflight/<session>/profile-<cpu2|cpu4|cpu8>.json, controls.json
  environment/sessions.csv, p9-<session>.json, integrity-<session>.json, …   (§4.6)
  prover/schedule.csv              round, kind (primary|diag), position, profile, config seed
  prover/execution_plan.csv        container order
  prover/round_ledger.csv          one row per round attempt outcome (§3.2.1)
  prover/host_samples.csv          host state before and after every container
  prover/sessions/<session>/units.csv   units still to run at the start of the session
  prover/<cpu2|cpu4|cpu8>/rounds.csv   one row per (round, profile) container
  prover/<cpu2|cpu4|cpu8>/runs.csv     one row per primary pipeline (incl. warm-ups)
  prover/<cpu2|cpu4|cpu8>/diag.csv     one row per diagnostic proving call
  […]
  derived/prover_summary.csv, prover_boundary.csv, prover_crossbackend.csv,
          prover_scaling.csv, prover_diag.csv, onchain_summary.csv, values.tex
```

### 7.2 Row schemas

Implemented in `bench/lib/schema.js` (column order fixed; headers are checked).

**`rounds.csv`:** campaign_id, session_id, profile_id, kind, round, round_attempt, position_in_round, container_id, image_id, cpuset, zcorp_cpus, os_cpus_length, available_parallelism, ffjs_concurrency, heap_limit_mb, started_at_utc, ended_at_utc, rows_written, memory_peak_bytes, memory_max_bytes, swap_max, cpu_max, oom_kill, nr_throttled, repo_readonly, artifacts_verified, assertions_passed, status, error.

**`runs.csv`:** campaign_id, session_id, profile_id, container_id, kind, run_id, round, round_attempt, order_in_round, seed, is_warmup, warmup_kind (`in_process` | `round0` | empty), backend, depth, leaf_index, started_at_utc, input_ms, witness_ms, prove_ms, verify_first_ms, verify_steady_ms, **stage_sum_ms**, **wall_ms**, zkey_bytes, zkey_sha256, proof_valid, root_matches, input_matches_committed, public_root, expected_root, heap_used_mb, rss_mb, image_id, manifest_sha256, status, error.

**`diag.csv`:** campaign_id, session_id, profile_id, container_id, diag_round, round_attempt, seed, backend, depth, pair_order (path_first|mem_first), call (path|mem), call_position, started_at_utc, zkey_readfile_ms (mem only), prove_ms, zkey_bytes, zkey_sha256, proof_valid, root_matches, heap_used_mb, rss_mb, image_id, manifest_sha256, status, error.

**`host_samples.csv`** (host side, before and after every container): campaign_id, session_id, seq, kind, round, round_attempt, profile_id, phase, utc, loadavg, power_source, low_power_mode, pmset_therm.

**`round_ledger.csv`** (append-only): campaign_id, kind, round, round_attempt, session_id, status (`complete` | `failed` | `incomplete`), accepted, recorded_utc, recorded_by_session, profiles, rows_runs, rows_diag, detail.

**`sessions.csv`:** campaign_id, session_id, event (start | end), utc, mode, git_head, image_id, docker_desktop, engine, kernel, vm_ncpu, vm_mem_bytes, power_source, low_power_mode, caffeinated, detail.

### 7.3 Anti-mixing

- Every plot and summary script takes `--campaign <dir>`. It asserts:
  - a single `campaign_id`;
  - the same commit across all inputs;
  - a single built-image digest across all profile rows.
- Summary scripts select rounds explicitly (1–5 or 1–10, §3.3) and write the rounds used into each derived file.
- Rows from a container whose pre-flight failed, or whose `oom_kill` or `nr_throttled` is non-zero, are kept but flagged, and are excluded from summaries. The exclusion is listed in the derived files.
- Only the accepted attempt of each round unit is summarised; rows of failed or incomplete attempts are kept and never summarised (§3.2.1).
- `diag.csv` is never read by the primary summaries.
