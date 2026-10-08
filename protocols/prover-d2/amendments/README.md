# prover-D2-amendments — recorded pre-timing changes to the D2 candidate kit (outside the frozen prereg package)

The frozen D2 preregistration package `../prover-D2/` (`SHA256SUMS` `97a05eca76af2083b304eb443f2067ffbaaac2398a2c94a1f25a7fd5765c72b4`)
is never edited. Owner-approved pre-timing changes are recorded here.

| Item | Content |
|---|---|
| `DEV-D2-1/` | control-oracle portability correction (`record_controls.js` L27), owner-approved V2-A28, adopted V2-D-52; own `SHA256SUMS`, `RECORDED-UTC.txt` |
| `DEV-D2-1-engineering-test/` | off-host oracle test (node, no container): old vs r2 `record_controls.js` on the recorded Host-A / Host-B controls and synthetic negative cases; all 9 cases as expected |
| `kit-v3-x86-r2/` | amended **candidate** kit = `../prover-D2/kit-v3-x86/` with DEV-D2-1 only (24 files; 23 byte-identical) |
| `KIT-v3-x86-r2.filelist.sha256` | per-file sha256 of `kit-v3-x86-r2/` (LC_ALL=C order); its sha256 is the r2 kit file-list hash |
| `KIT-DIFF-r2-supplement.txt` | the only hunk of r2 vs v3-x86 and vs v3 (supplements `../prover-D2/KIT-DIFF-vs-v3.txt`) |
| `AMD-D2-1/` | the single preregistered Host-B quiet-window threshold amendment (`hostb_quiet.py`: load1 recorded, not an acceptance condition), owner-approved 2026-10-05, adopted V2-D-55; **consumes the slot**; own `SHA256SUMS`, `RECORDED-UTC.txt` |
| `AMD-D2-1-engineering-test/` | off-host self-tests (r2 and r3 gates) and replay of the preserved r2 dry-run snapshots, plus perturbed copies; all as expected |
| `kit-v3-x86-r3/` | amended **candidate** kit = `kit-v3-x86-r2/` + AMD-D2-1 only (`hostb_quiet.py`) |
| `KIT-v3-x86-r3.filelist.sha256`, `KIT-DIFF-r3-supplement.txt` | r3 per-file hashes; the only hunk of r3 vs r2 |
| `SHA256SUMS.r2-freeze-20261005T081606Z` | the folder listing as frozen for r2 (kept) |
| `DEV-D2-2/` | Host-B validator correction (`summarize_prover.js` `repository_unchanged`: Git fields → `corpus_after_ok && tree_unchanged`), owner-approved V2-A29, adopted V2-D-59; not a threshold amendment; own `SHA256SUMS`, `RECORDED-UTC.txt` |
| `DEV-D2-2-engineering-test/` | off-host validator test on copies of the r3 dry-run evidence: frozen r3 validator reproduces the recorded 13 / 14; r4 gives 14 / 14 with every other check identical; 9 negative integrity cases fail closed |
| `kit-v3-x86-r4/` | amended **candidate** kit = `kit-v3-x86-r3/` + DEV-D2-2 only (`summarize_prover.js`) |
| `KIT-v3-x86-r4.filelist.sha256`, `KIT-DIFF-r4-supplement.txt` | r4 per-file hashes; the only hunk of r4 vs r3 |
| `SHA256SUMS.r3-freeze-20261005T090805Z` | the folder listing as frozen for r3 (kept; its `.DS_Store` entry is Finder metadata, V2-X-30) |
| `DEV-D2-3/` | Host-B resume-test oracle correction (`check_resume_test.js`: helper `det()` strips the runner's `window <id>; ` detail prefix in `three_sessions_with_new_ids` and `session1_clean_planned_stop`), owner-approved V2-A31, adopted V2-D-65; not a threshold amendment; own `SHA256SUMS`, `RECORDED-UTC.txt` |
| `DEV-D2-3-engineering-test/` | off-host oracle test on copies of the r4 test-resume evidence: frozen r4 oracle reproduces the recorded 10 / 12; r5 oracle 12 / 12 on the current x86, legacy v3 and declared-window formats; 8 negative cases fail closed; every other check identical |
| `kit-v3-x86-r5/` | amended **candidate** kit = `kit-v3-x86-r4/` + DEV-D2-3 only (`check_resume_test.js`) |
| `KIT-v3-x86-r5.filelist.sha256`, `KIT-DIFF-r5-supplement.txt` | r5 per-file hashes; the only hunk of r5 vs r4 |
| `SHA256SUMS.r4-freeze-20261005T102639Z` | the folder listing as frozen for r4 (kept) |

The kit stays a candidate: its final freeze follows the Host-B dry-run review (prereg §7). The single quiet-window
threshold amendment (`AMD-D2-n`, prereg §5.1) has been **used** by AMD-D2-1; no further threshold amendment is permitted.
