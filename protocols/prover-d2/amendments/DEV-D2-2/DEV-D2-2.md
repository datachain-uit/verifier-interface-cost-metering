# DEV-D2-2 — pre-timing Host-B validator correction (`summarize_prover.js`, `repository_unchanged`) (V2-PRV-D2-01)

Recorded: 2026-10-05T10:25:16Z. Owner approval: V2-A29 ("APPROVE DEV-D2-2", exactly in scope); adoption decision V2-D-59; issue V2-X-31;
audit `notes/V2-D2-r3-dryrun-validation-audit.md` (sha256 `b418091bd84374afc205f1e8b86da074cf7c63dbdd8049b5b665940f89cb46f1`).

**Classification (owner).** NON-SCIENTIFIC / GENERATED-STATE VALIDATOR DEFECT OR SCOPE ISSUE.
**Class.** Recorded deviation from D2-PREREGISTRATION.md §4.2 ("Unchanged byte for byte: … `summarize_prover.js` …"). It is
**not** an `AMD-D2-n` threshold amendment: no host-condition threshold changes; AMD-D2-1 is unchanged; the single
Host-B threshold-amendment slot remains consumed. The frozen preregistration package `research/csi/protocols/v2/prover-D2/`
(`SHA256SUMS` `97a05eca76af2083b304eb443f2067ffbaaac2398a2c94a1f25a7fd5765c72b4`) is not modified.

## 1. Exact defect

`summarize_prover.js` (byte-identical to v3) evaluates `repository_unchanged` at two sites (L98: every ended session;
L104: the current session) as `j.manifest_before_ok && j.manifest_after_ok && j.git_status_unchanged && j.git_head_unchanged`
on `environment/integrity-<session>.json`. The Host-B runner writes no Git fields, so the expression is `undefined` →
`repository_unchanged` false for every Host-B session that reaches validation, whatever the repository state.

## 2. Why it existed since the original v3-x86 adaptation

Host B has no Git repository (prereg §4.2 item 4). The v3-x86 runner (`run-campaign.sh` L176–L184; `KIT-DIFF-vs-v3.txt`
L680–L697) therefore replaced the v3 integrity fields `git_head_*` / `git_status_*` by `corpus_after_ok`,
`tree_sha256_before`, `tree_sha256_after`, `tree_unchanged` when kit v3-x86 was prepared (2026-10-04, V2-D-42), while
`summarize_prover.js` was kept byte-identical to v3 (prereg §4.2). No file of the kit writes the Git fields; only the
validator reads them. DEV-D2-1 and AMD-D2-1 did not touch either side. The D2 preparation engineering tests did not run
end-of-session validation on a Host-B integrity record, so the mismatch first surfaced in the first Host-B session that
reached validation.

## 3. Exact diff (`summarize_prover.js` only; three lines)

- L98 and L104: `j.git_status_unchanged && j.git_head_unchanged` → `j.corpus_after_ok && j.tree_unchanged`
  (`j.manifest_before_ok && j.manifest_after_ok` retained; `!j` → problem retained).
- L106 detail text: `manifest, git HEAD and git status unchanged in every finished session` →
  `manifest, corpus and tree identity unchanged in every finished session`.

Unified diff `summarize_prover.js.diff` (sha256 `d2bead29a3d7fd0c7afa643ddf7bb3dc086d871ca3edd6365635e3db1a650d5f`).
File `3fde442f455f8fb2cef48c03cca53d1717f8efc71761df46a0f365a08cf42a19` (v3 = v3-x86 = r2 = r3) →
`10d0fd6219dbe52a7edee906d675817f76af39b9c2b17524eab81e69a988fae0` (r4). No other validator logic changes.

## 4. Evidence that exposed it (preserved unchanged; never revalidated in place)

r3 dry run `dryrun-20261005T094307Z` (session S20261005T094307Z): 9 / 9 containers, 3 / 3 round units accepted, 18 / 18
host samples accepted; validation 13 / 14, sole FAIL `repository_unchanged` → `RESULT.txt` FAIL. Its integrity record
`integrity-S20261005T094307Z.json` (sha256 `4a05035fff8dd0588551a8cb50137e2693885218b72e5f222cf4515bf44bcb0a`) has
`manifest_before_ok` true, `manifest_after_ok` true, `corpus_after_ok` true, `manifest_entries_ok_after` 161,
`tree_sha256_before` = `tree_sha256_after` = `46574d5796ddbdaaeba722cf5e876534b0bbfb2cb3842a848e40b881ab696e00`,
`tree_unchanged` true, and no Git fields. Evidence `research/results/v2/V2-PRV-D2-01/owner-local-dryrun-20261005T094307Z/`
(`SHA256SUMS` `f8bdb02ffc65c9ad8958679d7ccc36781a308859f3ce788bc4fad8593fccffab`; `validation.json`
`0824b3b12814d7bfe8f4ad2bca43f3cf4d59d2ea5695a2910f3e5993336e64c1`). That session remains historically "3 / 3 rounds accepted;
formal validator FAIL 13 / 14 due to the DEV-D2-2 defect"; it is not turned into a PASS.

## 5. Why it is non-scientific

The check is an administrative integrity gate on the repository state around a session. It reads only the integrity
record; it does not read, transform or summarise any measured row, and it does not influence container execution,
round acceptance (`validate_round.js`), timing paths or summaries.

## 6. Why the replacement matches the preregistered Git-free model

Prereg §4.2 item 4: "Host B has no Git repository: a tree identity hash (kit, input generator, both manifests) replaces
the Git commit and status in the campaign identity and in the resume refusal checks"; item 5: the corpus manifest is
checked by the runner. The v3-x86 runner already records exactly these: `manifest_before_ok` / `manifest_after_ok`
(161 artifacts), `corpus_after_ok` (synthetic corpus), `tree_unchanged` (tree identity before = after). DEV-D2-2 applies
the same substitution to the validator. The Host-A meaning ("repository unchanged during the session") is preserved.

## 7. Unchanged

No measured variable, timing path, metric, threshold, schedule, execution plan, allocation, CPU IDs, NUMA placement,
corpus, artifact, runner, harness, adapter, quiet-window gate, inhibitor rule or host policy changes. `summarize_prover.js`
is copied into the Docker image (`Dockerfile` L10), so the image ID changes; that difference is attributable to this
file only (recorded with the r4 setup).

## 8. Not a threshold amendment

DEV-D2-2 is not `AMD-D2-n`. AMD-D2-1 is unchanged and remains the only Host-B threshold amendment; the slot stays consumed.
