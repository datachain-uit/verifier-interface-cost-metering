# DEV-D2-1 — pre-timing control-oracle portability correction (V2-PRV-D2-01, Host B)

Recorded: 2026-10-05T08:13:51Z. Owner approval: V2-A28 (approved exactly as proposed in `notes/V2-D2-control-oracle-audit.md`,
sha256 `a75f6fb980479c1a48e6e61b11ea36a90792a175c589f4e5c0da5578b19a5f2e`); adoption decision V2-D-52; issue V2-X-27.

**Class.** Recorded deviation from D2-PREREGISTRATION.md §4.2 ("Unchanged byte for byte: … `record_controls.js` …").
It is **not** a quiet-window threshold amendment (`AMD-D2-n`, §5.1): `hostb_quiet.py` and its thresholds are untouched
and the single preregistered threshold-amendment slot remains **unused**. The frozen preregistration package
`research/csi/protocols/v2/prover-D2/` (`SHA256SUMS` `97a05eca76af2083b304eb443f2067ffbaaac2398a2c94a1f25a7fd5765c72b4`)
is not modified; this record and the amended candidate kit live outside it.

**Scientific classification (owner).** CONTROL-ORACLE PORTABILITY DEFECT — not a resource-control failure, not a Host-B
experiment incompatibility, not a quiet-window threshold problem, not a scientific timing failure.

**Chronology.** Adopted after the failed owner-local preflight `preflight-20261005T074450Z` (V2-D-51) and before any
dry run or timed round: **no D2 dry-run or timing data existed when this correction was adopted.** The failed session
is preserved unchanged (workstation `~/Workspace/Z-CORP-V2-workstation/prover/d2/`, untouched; Mac copy
`research/results/v2/V2-PRV-D2-01/owner-local-preflight-20261005T074450Z/`, `SHA256SUMS`
`d7372eab7b2b9932c417af5e12dbf6b0d48dd70563cc0a138e0eac8ac46655b9`; its `controls.json` sha256
`22df33d438165804ce69fff95158c344c3085bca65264df77cd17b88cce8e159`).

## Exact change (one expression; `record_controls.js` line 27)

- before: `out.no_adapter_ffjs_concurrency === out.no_adapter_os_cpus`
- after:  `out.no_adapter_ffjs_concurrency === Math.min(out.no_adapter_os_cpus, 64)`
- retained unchanged: `out.no_adapter_ffjs_concurrency > out.control_cpuset_size`, `mismatch_exit === 97`,
  `quota_only_exit === 97`, `no_adapter_exit === 0`; every other line of the file.

Unified diff: `record_controls.js.diff` (sha256 `2429af23b71df19089d898efc75bc13f6135b9c86b9325ce412e3f4d4695896a`).
File hash: `acf81fe1cc308352e0c43ded8285ea15ee2101b4fbf2a52a9d9788f02797172e` (v3 / kit v3-x86) →
`bd82f6e36fb4101639ce3261f999cba84b414190dd12474ac50bd77b5ddda684` (kit v3-x86-r2); 2,207 → 2,221 bytes; only line 27 differs.

## Rationale

The no-adapter control exists to show that, without the CPU-visibility adapter, ffjavascript sizes its worker pool from
the CPUs the kernel lists rather than from the allocation (v3 `RERUN-PROTOCOL.md` L112 risk table; §4.3 control). The
pinned ffjavascript 0.3.1 sizes the pool as `min(os.cpus().length, 64)` (`src/threadman.js` L110, L117–L118;
`build/main.cjs` L4476, L4483–L4484; tarball sha512 = the lock's integrity), and the frozen v3 protocol states this
rule (`RERUN-PROTOCOL.md` L197), written 2026-09-25, before any Host-B run. The old oracle encoded only the special
case `os.cpus().length ≤ 64` (Host A: 10 vCPUs). The corrected oracle is the **library-accurate rule**; it is not a
loosening to accommodate the observed value: it is stricter than the old oracle for an uncapped pool (os 112 → pool 112
now FAILS, previously PASSED), and it still requires the pool to be unconstrained by the allocation (> cpuset size).

## Oracle test table (adopted matrix; reproduced by the engineering test of the r2 kit)

| Case | os.cpus | pool | cpuset | mismatch exit | quota-only exit | no-adapter exit | old oracle | corrected oracle |
|---|---|---|---|---|---|---|---|---|
| Host A recorded (S20260925T060607Z) | 10 | 10 | 2 | 97 | 97 | 0 | PASS | PASS |
| Host B recorded (S20261005T074450Z) | 112 | 64 | 2 | 97 | 97 | 0 | FAIL | PASS |
| pool constrained to the allocation | 112 | 2 | 2 | 97 | 97 | 0 | FAIL | FAIL |
| uncapped pool | 112 | 112 | 2 | 97 | 97 | 0 | PASS | FAIL |
| arbitrary off-rule pool | 112 | 10 | 2 | 97 | 97 | 0 | FAIL | FAIL |
| mismatch not refused | 112 | 64 | 2 | 0 | 97 | 0 | FAIL | FAIL |
| quota-only not refused | 112 | 64 | 2 | 97 | 0 | 0 | FAIL | FAIL |
| no-adapter probe failed | 112 | 64 | 2 | 97 | 97 | 1 | FAIL | FAIL |

## Effects (stated before deployment)

- Measured variables, metrics, timing behaviour: none. `record_controls.js` runs only in the untimed `tools`
  container after the profile preflights; it is not loaded by `harness.js`, `preflight.js` or `lib/`; it sets the
  `passed` flag of `controls.json` (session gate: runner abort; `summarize_prover.js` L89–L90).
- cpu2 / cpu4 / cpu8 containers: unchanged code paths, CPU IDs, NUMA allocation, limits and semantics. The Docker image
  ID changes because the file is copied into the image (`Dockerfile` L10); its hash enters each new `CAMPAIGN.json`
  (`make_schedule.js` L119).
- Host-A comparability: unaffected (Host A evidence unchanged; the corrected oracle gives Host A's recorded controls the
  same verdict; procedure, schedule, plan, profiles, metrics unchanged).
- Not changed: `cpu-visibility.js`, `preflight.js`, `harness.js`, `run-campaign.sh`, `hostb_quiet.py`, schedule /
  plan, synthetic corpus, artifacts, metrics, D2 analysis, thresholds, inhibitor semantics, host configuration;
  tree-hash collation is deliberately **not** touched (separate observation, V2-D-51).

## Hashes that change downstream (filled by the r2 kit / payload / setup records)

`record_controls.js` (above); kit file-list hash (`f1dfc537…` → r2); Host-B payload (`e9670c6a…` → r2) and
`PAYLOAD-MANIFEST.sha256` (`886b3182…` → r2; one line); Host-B tree hash (both collations); Docker image ID
(`sha256:0548907538d7…` → r2).
