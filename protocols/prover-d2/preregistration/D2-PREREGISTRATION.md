# V2-PRV-D2-01 — x86_64 native-Linux replication of the v3 prover procedure (PREREGISTRATION)

Status: **D2 PROTOCOL PREPARED — AWAITING HOST-B DRY RUN.** Text frozen 2026-10-04 (hash in `SHA256SUMS`). Owner
choices approved in V2-D-37: v3-matched replication; Docker only; no container-free arm; pinning below; record-as-is
frequency policy; dedicated quiet window as the key acceptance criterion. **No D2 timing has been collected and D2 timing
is not authorized** (the workstation is shared and busy). Class: SUPPORTING (C1 `16-full-protocol.md` §3.5). Supersedes
`../prover-drafts/D2-x86-replication-preregistration-DRAFT.md`.

## 1. Question and claims allowed

- **Within-host scaling on Host B**: how `input`, `witness`, `prove`, `verify_first`, `verify_steady` and `wall` change
  from allocation cpu2 → cpu4 → cpu8, for Groth16 and PLONK, across Merkle depths d = 5 … 15.
- **Cross-host pattern replication**: does Host B reproduce the *pattern* measured on Host A (allocation speedups,
  within-round PLONK / Groth16 ratio per depth, the PLONK d = 10 → 11 step, the zkey-loading diagnostic)?
- **Never pooled; no population claim.** Hosts are reported side by side. There is one ARM host and one x86 host, so no
  statement about ARM versus x86 (or Apple versus Intel) as hardware classes is made. cpu2 / cpu4 / cpu8 are
  allocations on a host, never devices.

## 2. Hosts

| | Host A (existing evidence; no new run) | Host B (new) |
|---|---|---|
| Machine | MacBook Pro `Mac17,2`, Apple M5 (4 P + 6 E cores) | Dell Precision 7920 Tower, 2 × Xeon Platinum 8173M (2 × 28 cores, SMT 2) |
| Runtime | Docker Desktop 4.92.0 VM (10 vCPU, 16 GiB), Engine 29.8.0, `linux/arm64` | native Docker Engine (27.5.1 at fingerprint), Ubuntu 24.04.3, kernel 6.14, `linux/amd64` |
| Evidence | V1 campaign `campaign-20260925T060607Z` (`research/results/postcorr-20260925`), statistics in V2-PRV-D3-01 | `research/results/v2/V2-PRV-D2-01` (to be created) |
| Allocation unit | VM vCPU (cpuset of the VM; heterogeneous cores; not pinnable) | logical CPU = one hardware thread of a distinct physical core, socket 0 / NUMA node 0 |
| Inputs | V1 credential corpus | frozen synthetic corpus of the same schema and size (§4.3; V2-D-18) |

## 3. Allocation and pinning on Host B (exact)

From `lscpu -p` and `thread_siblings_list` (records `research/results/v2/workstation-20261004/`): NUMA node 0 = CPUs
0–27 (cores 0–27, socket 0) and their SMT siblings 56–83; sibling(i) = i + 56.

| Profile | `--cpuset-cpus` | Physical cores | SMT siblings (not allocated; must stay idle) | `--cpuset-mems` | ffjavascript workers |
|---|---|---|---|---|---|
| cpu2 | `1-2` | 1, 2 | 57, 58 | `0` | 2 |
| cpu4 | `1-4` | 1–4 | 57–60 | `0` | 4 |
| cpu8 | `1-8` | 1–8 | 57–64 | `0` | 8 |

CPU 0 and its sibling 56 are left to the OS and the Docker daemon (as vCPU 0 on Host A). One hardware thread per
physical core; SMT stays enabled in firmware and the siblings are checked idle (§5). The full 112-CPU host, the second
socket and SMT siblings are never used as an allocation. The worker count is enforced by the byte-identical v3
CPU-visibility adapter (`lib/cpu-visibility.js`, `749eea66…`) and asserted in every container.

## 4. Procedure

### 4.1 Identical to v3 (Host A)

Same artifact set (`ARTIFACTS.sha256`, `9a7829fe…`, 161 entries; same circuits, Groth16 and PLONK keys, vkeys), depths
d = 5 … 15, the 22 primary configurations, rounds 0 … 10 (round 0 a discarded warm-up; rounds 1–5 all configurations,
rounds 6–10 Groth16 only, hence **Groth16 R = 10, PLONK R = 5**), diagnostic rounds 1–5 (8 configurations, key from
path vs in memory), in-process warm-up (Groth16 d5, PLONK d5), file-cache warm-up, seed `zcorp-rerun-v3`, profile
positions and configuration orders, memory 8 GiB, swap 0, V8 heap 4,096 MiB, no CPU quota, no network, repository
read-only, metric definitions and acceptance rules of protocol v3 §3. **The Host-B schedule must be byte-identical to
Host A's** (`schedule.csv` `f7e6de3b…`, `execution_plan.csv` `99fb360c…`); `make_schedule.js` refuses otherwise. Verified
off-host with the prepared kit (engineering test 2, §7). Same pinned base image index digest
(`node:18.20.8-bookworm-slim@sha256:f9ab18e3…830e`; the `linux/amd64` manifest digest is recorded) and the same
dependency lock (snarkjs 0.7.5, ffjavascript 0.3.1, fastfile 0.0.20, circom2 0.2.16).

### 4.2 Host adaptation (exhaustive; kit `v3-x86`, full diff `KIT-DIFF-vs-v3.txt`)

1. Platform `linux/amd64`; expected Docker architecture `x86_64`, Node `process.arch` `x64`, machine `x86_64`; no CPU
   implementer check (ARM-only field); CPU model asserted (`Intel(R) Xeon(R) Platinum 8173M CPU @ 2.00GHz`).
2. Containers are started with the `docker run` equivalent of each compose profile plus `--cpuset-mems 0` (compose has
   no cpuset-mems key); `cpuset.mems.effective = 0` is asserted in every container.
3. The macOS P9 checks (AC power, Low Power Mode, `caffeinate`, `pmset`) are replaced by the Linux host conditions of
   §5 (`hostb_quiet.py`) and a `systemd-inhibit` sleep inhibitor held by the runner.
4. Host B has no Git repository: a tree identity hash (kit, input generator, both manifests) replaces the Git commit and
   status in the campaign identity and in the resume refusal checks.
5. Synthetic corpus (§4.3): the expected public root is the synthetic corpus root; the committed V1 proofs are still
   verified in P7 against their own committed public files; the corpus manifest is checked by the runner, P7 and each
   container.
6. The 11 PLONK proving keys (not carried in the V2 tree) are regenerated on Host B in the untimed `setup` step
   (deterministic from the R1CS and `pot16_final.ptau`; D1 confirmed byte-identical regeneration of d10 / d11) and must
   equal `ARTIFACTS.sha256`; P7 regenerates them again as in v3. Setup duration is never evidence.
7. Campaign gate: `ZCORP_ALLOW_FULL_CAMPAIGN=1` **and** an owner-declared window identifier `ZCORP_D2_WINDOW`; output
   directory `results/V2-PRV-D2-01`.
8. `validate_round.js --host-violation` records a round whose host conditions were violated during a container as
   failed; `host_samples.csv` carries Linux telemetry columns.
9. `setup_plonk_zkeys.js` added to the image (Dockerfile `COPY`); `test-resume.sh` uses `docker run` and a tree-identity
   tamper instead of a Git-commit tamper.
Unchanged byte for byte: `lib/cpu-visibility.js`, `lib/validate.js`, `campaign_state.js`, `summarize_prover.js`,
`record_controls.js`, `package.json`, `package-lock.json`, the input generator (`scripts/setup/generate_input_depth.js`
`4d3f34f7…`, `paths.js` `004b6e77…`).

### 4.3 Synthetic corpus (V2-D-18: synthetic records only)

Host A's input stage read the V1 credential corpus, which V2 must not copy. `synthetic-corpus/d2_synthetic_corpus.js`
(seed `V2-D2-synthetic-corpus-2026-10-04`) writes `processed_diplomas_<2^d>.json` and `merkle_tree_data_depth_<d>.json`
for d = 5 … 15 in the schema read by the unchanged generator (fields, types, full proof lists, `JSON.stringify(·, null, 2)`);
the committed inputs `data/inputs/input_depth_<d>_index_0.json` are written by the unchanged generator. Only the schema
and file sizes of the V1 corpus were read, never its values. File sizes match the V1 corpus within 0.35 % (depth 15
tree: +0.006 %), so the input stage parses the same amount of JSON. Manifest `SYNTHETIC-CORPUS.sha256` (`c7203a12…`,
33 files). Off-host check: valid proofs whose public root equals the corpus root for Groth16 d5 / d8 / d10 / d11 / d13 /
d15 and PLONK d10 / d11 (`synthetic-corpus/CORPUS-ENGINEERING-CHECK.json`).
**Comparability:** witness, prove and verify use identical circuits, keys and inputs of identical structure; the input
stage uses the same generator on files of the same size but different values and is reported with this note; `wall`
includes the input stage.

## 5. Host conditions and acceptance (blocking)

### 5.1 Dedicated quiet window (key acceptance criterion)

Timed rounds run only in a window the owner declares dedicated (`ZCORP_D2_WINDOW`). **No timed round is accepted while an
unrelated CPU-heavy workload or any other container is active.** Operationally (`hostb_quiet.py`, frozen thresholds):

| When | Condition |
|---|---|
| session start and 2 s before every container | 0 running containers; load1 ≤ 2.0; each allocated CPU and each SMT sibling busy ≤ 10 %; all other logical CPUs together ≤ 1.0 CPU-equivalent; frozen state (§5.2) unchanged; sleep inhibitor held |
| during every container (start → end, from `/proc/stat`) | 0 running containers before and after; each SMT sibling busy ≤ 5 %; all non-allocated, non-sibling CPUs together ≤ 1.5 CPU-equivalents; frozen state unchanged; inhibitor held |

A violation before a container stops the session and the unit is rerun whole on resume; a violation during a container
records the attempt as failed (`--host-violation`) and stops; attempts are never deleted (v3 §3.2.1). The check reads
only `/proc`, `/sys` and the container count; it never inspects or interferes with other users' processes.
**Amendment rule:** thresholds may be amended once, before the first timed round, only on the basis of the untimed
Host-B dry-run telemetry, as a recorded amendment (`AMD-D2-n`, hashed); never after timing has started.

### 5.2 Frequency and host policy (record as is; never changed)

Frozen state, checked before and during every container: `intel_pstate` active (HWP), governor `powersave` on all CPUs,
`no_turbo = 0` (turbo enabled), `numa_balancing = 1`, THP `madvise`. The study never changes governor, turbo, NUMA,
SMT or THP settings. Recorded per session: energy-performance preference of CPUs 1–8, `hwp_dynamic_boost`, SMT control,
kernel command line, `lscpu`, `numactl -H`. Telemetry per container (before / during): load, busy fractions, current
MHz of the allocated CPUs, package temperature, core and package throttle counters.

## 6. Outputs and analysis (descriptive; no pass / fail thresholds)

Per host separately, with the estimators of V2-PRV-D3-01 (script v1.1, `94c3ad06…`): per (allocation, backend, stage,
depth) median, IQR, CV and 95 % percentile-bootstrap interval of the median (B = 10,000; seeds
`int(sha256("20261004|D2|<key>")[:16], 16)`); PLONK n = 5 intervals labelled coarse; within-round PLONK / Groth16
ratios; within-round allocation speedups cpu2→cpu4, cpu4→cpu8, cpu2→cpu8; the PLONK d = 10 → 11 step; zkey-loading
diagnostic (path − mem; no read-time rows, DEV-D3-2). Host A values are the V2-PRV-D3-01 outputs. `d2_analysis.py`
(the D3 computations with Host-B paths and an input manifest of the frozen Host-B evidence; nothing else changed) is
hash-frozen before the first timed round. Side-by-side A / B tables state the allocation semantics in the header.
Never pooled with D1 or D3.

## 7. State and checklist

**Prepared (this task, no workstation use):** this text (frozen); kit `v3-x86` (candidate, hashed); synthetic corpus
(frozen); off-host engineering tests: (1) synthetic-corpus proofs 8 / 8; (2) Host-B schedule and execution plan
byte-identical to Host A; (3) pipeline with the synthetic corpus: proof valid, root and committed input match (Groth16
d5 / d8 / d13 / d15); (4) host-condition self-tests 9 / 9; (5) new container assertions report correctly; Host-B
payload and relay jobs prepared outside `jobs/` (not queued).

**Awaiting Host-B dry run** (needs owner authorization when the workstation is free; jobs in
`outputs/workstation-relay/prepared/d2/`):
1. transfer and unpack the payload; verify payload, corpus and artifact manifests (light);
2. `setup`: image pull / build and PLONK key regeneration (heavy; untimed) → `ARTIFACTS.sha256` 161 / 161;
3. `preflight` (P7, container assertions incl. `cpuset.mems`, adapter controls, host conditions);
4. `dryrun` and `test-resume.sh` (untimed; timings not interpreted);
5. review of the dry-run host telemetry; threshold amendment only if needed (§5.1);
6. final kit freeze (`v3-x86` hash recorded in the decision log) and freeze of `d2_analysis.py`.

**Awaiting dedicated window:** the owner declares the window id and that no unrelated workload or container will run;
then `campaign` (one session expected; resume if stopped). Host A took 1 h 40 min for the same schedule; Host B is
expected to need longer (estimate 2–5 h) plus 1–2 h for steps 2–4.
