# AMD-D2-1 — the single preregistered Host-B quiet-window threshold amendment (V2-PRV-D2-01)

Recorded: 2026-10-05T09:07:11Z. Owner approval: 2026-10-05 ("APPROVE AMD-D2-1 substantively as proposed", with the bounded wording
below); adoption decision V2-D-55; issue V2-X-28. Basis: D2-PREREGISTRATION.md §5.1 amendment rule — "thresholds may be
amended once, before the first timed round, only on the basis of the untimed Host-B dry-run telemetry, as a recorded
amendment (`AMD-D2-n`, hashed); never after timing has started."

**This amendment consumes the single preregistered Host-B threshold-amendment slot. No further Host-B threshold
amendment is permitted.** The frozen preregistration package `research/csi/protocols/v2/prover-D2/` (`SHA256SUMS`
`97a05eca76af2083b304eb443f2067ffbaaac2398a2c94a1f25a7fd5765c72b4`) is not modified. DEV-D2-1 (control oracle) is a
separate class and is unchanged.

**Classification (owner).** LOAD1-ONLY THRESHOLD SENSITIVITY.

## Exact change (`hostb_quiet.py` only; host-side; not part of the Docker image)

- L19: `LOAD1_MAX = 2.0` → `LOAD1_MAX = float('inf') # AMD-D2-1: load1 recorded, not an acceptance condition`
- L11 (docstring): `load1 <= LOAD1_MAX;` → `load1 recorded (AMD-D2-1; not an acceptance condition);`
- L169 (self-test): `('high load rejected', mk({}, load='5.0 4.0 3.0 1/900 1'), 'pre', False)` →
  `('high load1 alone recorded, not rejected (AMD-D2-1)', mk({}, load='5.0 4.0 3.0 1/900 1'), 'pre', True)`

Unified diff `hostb_quiet.py.diff` (sha256 `fb46909646a063531929a3633f02badf15cef655a1e4f62f2cee2dda7753f837`).
File: `932a8986bf1aa6a376426ef6bfc69ec90f2a1815918e566fc4b1b0c2b5efcbe3` (v3-x86 = v3-x86-r2) →
`3e74157e789ba2933c308a08d0b16fdc6c16382876e27fd5b02fa10f921e924d` (v3-x86-r3). load1 is still computed and written into
every check record (`loadavg`) and every `host_samples.csv` row.

Unchanged, exactly: 0 running containers before a container and before / after it (during); PRE_CPU_MAX 0.10 for each
allocated CPU and each SMT sibling; PRE_OTHER_MAX 1.0 CPU-equivalent; DURING_SIB_MAX 0.05; DURING_OTHER_MAX 1.5
CPU-equivalents; sleep-inhibitor requirement; frozen governor / turbo / NUMA / SMT / THP state; 2-s direct sampling
window; runner, harness, image contents, allocations, CPU IDs, NUMA placement, schedule, metrics, synthetic corpus,
artifacts, analysis definitions.

## Empirical basis: the r2 owner-local dry run `dryrun-20261005T084400Z` (preserved unchanged)

Evidence `research/results/v2/V2-PRV-D2-01/owner-local-dryrun-20261005T084400Z/` (`SHA256SUMS`
`d9afac1d228cdc30d0d75154b9e7e92a491977d5953fbcfc91751771debf371f`; transfer tgz
`59c507ae9aa5e682f63279884110d07228e758a781fe9ffbe556e54ec6f522b7`); key files: `c0001-pre.json` `34031c74…d3326`,
`c0001-pre-a.json` `621f9385…c326`, `c0001-pre-b.json` `f49a00c7…be70`, `session-check.json` `1f14864a…008c`,
`session-a.json` `bf08e816…7ad6`, `session-b.json` `e0375771…a311`, `host_samples.csv` `204c48a1…ef98`,
`RESULT.txt` `dfb52e1f…7dd1`, `round_ledger.csv` (header only) `6622af56…2130`. Audit:
`notes/V2-D2-dryrun-telemetry-review.md` (`8b2f7188…d6bc`).

1. The r2 dry run aborted before container 1 (`ABORT: host conditions not met before container 1 (load1 2.04 > 2.0)`).
2. No proof or timing measurement and no round outcome existed (no run snapshot, no `during` sample, ledger header only).
3. The sole violated condition was load1 2.04 > 2.0.
4. All direct CPU-busy measures were well within the frozen limits:

| Quantity | Session start (08:44:02–05Z) | Before container 1 (08:54:48–50Z) | Frozen pre limit |
|---|---|---|---|
| loadavg 1 / 5 / 15 | 1.90 / 2.01 / 1.37 | 2.04 / 1.82 / 1.57 | load1 ≤ 2.0 (until this amendment) |
| running containers | 0 | 0 | 0 |
| allocated CPUs 1–8, max busy | 0.0097 | 0.0481 | ≤ 0.10 |
| SMT siblings 57–64, max busy | 0.0144 | 0.0190 | ≤ 0.10 |
| other CPUs, CPU-equivalents | 0.38 | 0.335 | ≤ 1.0 |
| all 112 CPUs, CPU-equivalents (2 s) | 0.408 | 0.440 | — |
| package temperature; throttle counters | 47 °C; 0 / 0 | 49 °C; 0 / 0 | recorded |
| sleep inhibitor; frozen state | held; unchanged | held; unchanged | required |

5. Host A (v3, campaign-20260925T060607Z; `research/results/postcorr-20260925/prover/host_samples.csv`
   `538f9c9b051a60f0a8a0861d4020a26043830ff0234975bc2f8e530a9f2383e8`) recorded load averages of 2.17–4.47 (median 3.12)
   before all 48 accepted containers; there load average was telemetry, not an acceptance gate (macOS host load average
   with the Docker VM included; an analogy of semantics, not a like-for-like number).
6. The Host-B load1 gate therefore adds a brittle proxy that is not matched to Host-A acceptance semantics.
7. The direct per-CPU, SMT-sibling and other-CPU busy measurements more directly implement the intended quiet-window
   condition (no unrelated CPU load contaminating timing).
8. load1 remains recorded descriptively, preserving observability of lagging runnable / I/O-wait activity.

**Interpretation (bounded).** The elevated load1 is consistent with lagging self-load from the immediately preceding
untimed D2 work, while the direct CPU-busy measurements provide no evidence of unrelated CPU activity sufficient to
violate the quiet-window intent. The evidence supports that interpretation; it is not a direct causal attribution.

## Residual limitation

load1 also reflects uninterruptible tasks / I/O wait. After AMD-D2-1 this signal is descriptive rather than blocking. The
safeguards are: the owner-declared dedicated window, the zero-container rule, the direct CPU-busy gates (pre and during),
and the recorded load1.

## Downstream (filled by the r3 records)

Kit `v3-x86-r3` = `v3-x86-r2` + AMD-D2-1 only; payload r3 into a fresh `prover/d2-r3/` (`prover/d2/` and
`prover/d2-r2/` untouched); image expected unchanged (`hostb_quiet.py` is not copied into the image). The next untimed
action is a fresh owner-local dry run, not a resume of r2.
