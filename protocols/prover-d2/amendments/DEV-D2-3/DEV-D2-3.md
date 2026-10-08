# DEV-D2-3 — Host-B resume-test oracle correction (`check_resume_test.js`)

Recorded pre-timing deviation of V2-PRV-D2-01, outside the frozen preregistration package `../../prover-D2/`
(`SHA256SUMS` `97a05eca76af2083b304eb443f2067ffbaaac2398a2c94a1f25a7fd5765c72b4`, unchanged). Owner decision
2026-10-05: "APPROVE DEV-D2-3" (V2-A31; recorded V2-D-65). Classification: **NON-SCIENTIFIC RESUME-TEST ORACLE /
GENERATED-STATE DEFECT** — not a resume-semantics failure; **not a threshold amendment** (AMD-D2-1 remains the only
threshold amendment; the slot stays consumed).

## 1. Defect

`check_resume_test.js` (kit v3-x86, adapted from v3 only at L52) reads the `detail` column of `sessions.csv` in the v3
format (`resume`, `STOPPED (…)`). The v3-x86 runner writes every detail as `window ${ZCORP_D2_WINDOW:-none}; <detail>`
(`run-campaign.sh` `session_event`, KIT-DIFF-vs-v3 L526). Two history predicates therefore evaluate false on every Host-B
test-resume although the sessions and the planned stop are correct:

| Check | Line | Frozen predicate | Recorded state (`dryrun-resumetest-20261005T130639Z`) |
|---|---|---|---|
| `three_sessions_with_new_ids` | L21–22 | `… && starts[1].detail === 'resume' && starts[2].detail === 'resume'` | 3 starts, 3 distinct ids; details `window none; resume` |
| `session1_clean_planned_stop` | L26–27 | `endS1 && /^STOPPED/.test(endS1.detail)` | `window none; STOPPED (1 accepted, 3 remaining)` |

Latent since kit v3-x86 (V2-D-42); untouched by DEV-D2-1, AMD-D2-1 and DEV-D2-2; not covered by the off-host
engineering tests (test-resume runs only on Host B). Audit: `notes/V2-D2-r4-resumetest-audit.md`; V2-X-34; V2-D-64.

## 2. Change (exactly the audited candidate; nothing else)

```diff
 const [s1, s2, s3] = starts.map((s) => s.session_id);
+const det = (s) => String((s && s.detail) || '').replace(/^window [^;]*; /, ''); // v3-x86: runner prefixes "window <id>; " (DEV-D2-3)
 check('three_sessions_with_new_ids', starts.length === 3 && new Set([s1, s2, s3]).size === 3
-  && starts[1].detail === 'resume' && starts[2].detail === 'resume', …);
+  && det(starts[1]) === 'resume' && det(starts[2]) === 'resume', …);
-check('session1_clean_planned_stop', endS1 && /^STOPPED/.test(endS1.detail), endS1 && endS1.detail);
+check('session1_clean_planned_stop', endS1 && /^STOPPED/.test(det(endS1)), endS1 && endS1.detail);
```

`check_resume_test.js` r4 `3a80711d9b6b6e2d7d961747312d4d26ec6e4c3aa6f547509417c7dbeca1c88d` → r5
`b0f83a6431fbaa28b80dd293b42d403923ee08c8d5763da4fe3b59bcbc9ea849` (full diff `check_resume_test.js.diff`, byte-identical
to the audited candidate `notes/V2-D2-r4-resumetest-oracle-replay/check_resume_test.DEV-D2-3-candidate.diff`). The detail
strings printed in the check output, every other predicate and every other kit file are unchanged.

## 3. Resume semantics passed (r4 evidence, unchanged)

In `dryrun-resumetest-20261005T130639Z` (r4): session 1 accepted primary 0 and stopped as planned (exit 0); session 2
resumed with matching identity and was interrupted as simulated (exit 3); session 3 resumed, preserved primary 1 attempt 1
as `incomplete`, reran primary 1 whole as attempt 2 and accepted it, accepted primary 2 and diag 1, final validation
14 / 14 with 4 / 4 rounds (exit 0); the accepted-round rerun was refused without new rows (65 → 65); altered schedule and
altered tree identity were refused. All 10 substantive checks PASS.

## 4. The r4 result is retained

The recorded r4 test-resume result stays **permanently FAIL 10 / 12 (exit 9)** and is never relabelled, re-scored or
reused. Evidence `research/results/v2/V2-PRV-D2-01/owner-local-dryrun-20261005T123643Z-resumetest-20261005T130639Z/`
(`SHA256SUMS` `783e4b32e1927b594c1f1e16df66f81ce065d06bfb0f1f0a014ef3a7057a2a77`), unchanged.

## 5. Engineering test (copies only; `../DEV-D2-3-engineering-test/`)

Frozen r4 oracle on the record: 10 / 12, exit 9, identical to the recorded `resume-test.json`. Frozen r4 oracle on the
legacy v3 detail format: 12 / 12. r5 oracle — positives: current x86 format `window none; …` 12 / 12; legacy v3 format
12 / 12; declared window id `window W-TEST-1; …` 12 / 12 (all exit 0). Negatives (all exit 9, targeted predicate FAIL):
session-1 end `window none; PASS`; session-1 end `window none; FAIL: …`; session-1 end row missing; session-2 start `new`;
session-3 start `new`; only two starts; session 3 reusing the session-2 id; `window none; not resume`. For every input,
all checks other than the two corrected predicates are identical between the frozen r4 and the r5 oracle. ALL AS
EXPECTED.

## 6. Consequences

Kit `v3-x86-r5` = r4 + DEV-D2-3 only (file list `KIT-v3-x86-r5.filelist.sha256`); `check_resume_test.js` is copied into
the image (Dockerfile step 7), so the image changes in that file only; fresh `prover/d2-r5/`, untimed setup, image
comparison; a fresh owner-local test-resume on r5 is required. `dryrun` and `campaign` never execute this checker; the
r4 dry run `dryrun-20261005T123643Z` remains the dry-run readiness evidence (owner adjudication) provided the r4 → r5 image
comparison shows DEV-D2-3 as the only content difference. Runner, `test-resume.sh`, validator, `record_controls.js`,
`hostb_quiet.py`, thresholds, host policy and every scientific / prover path unchanged.
