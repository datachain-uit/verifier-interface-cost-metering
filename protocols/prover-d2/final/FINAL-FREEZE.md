# V2-PRV-D2-01 — final pre-timing freeze (kit v3-x86-r5 and d2_analysis.py)

Prereg §7 items 5–6 (dry-run review, final kit freeze, freeze of `d2_analysis.py`), recorded V2-D-68. Frozen before any
timed D2 round; **no timed D2 data exist**. Timing requires the owner's explicit chat line
`AUTHORIZE D2 TIMED WINDOW: <window-id>`; this freeze does not imply it.

## 1. Protocol and accepted changes

| Item | Identity |
|---|---|
| Preregistration package `../prover-D2/` (unchanged) | `SHA256SUMS` `97a05eca76af2083b304eb443f2067ffbaaac2398a2c94a1f25a7fd5765c72b4`; `D2-PREREGISTRATION.md` `a4a4e2f4…fa91` |
| DEV-D2-1 (control oracle, `record_controls.js`) | `../prover-D2-amendments/DEV-D2-1/SHA256SUMS` `00142f18…1e25` (V2-D-52) |
| AMD-D2-1 (load1 record-only, `hostb_quiet.py`) — **the only threshold amendment; slot consumed** | `../prover-D2-amendments/AMD-D2-1/SHA256SUMS` `27189f29…98a0` (V2-D-55) |
| DEV-D2-2 (validator `repository_unchanged`, `summarize_prover.js`) | `../prover-D2-amendments/DEV-D2-2/SHA256SUMS` `730be99e…98bc` (V2-D-59) |
| DEV-D2-3 (resume-test oracle, `check_resume_test.js`) | `../prover-D2-amendments/DEV-D2-3/SHA256SUMS` `7bf6ed01…8f26` (V2-D-65) |
| Amendments folder listing | `../prover-D2-amendments/SHA256SUMS` `e5158ee65b29dddda9d7fe030c70ca6b3fbb74b443d47cd85230fc208ae18ac3` |

Final kit vs the frozen `kit-v3-x86`: exactly four files differ (`record_controls.js`, `hostb_quiet.py`,
`summarize_prover.js`, `check_resume_test.js`), one per accepted change; quiet-window thresholds otherwise as frozen
(`PRE_CPU_MAX` 0.10, `PRE_OTHER_MAX` 1.0, `DURING_SIB_MAX` 0.05, `DURING_OTHER_MAX` 1.5; load1 recorded only).

## 2. Final kit, payload, Host-B tree and image

| Item | Identity |
|---|---|
| Final kit | `kit-v3-x86-r5` (`../prover-D2-amendments/kit-v3-x86-r5/`), file list `KIT-v3-x86-r5.filelist.sha256` → `5352f80142e364baec65082c39aa59e94f4625dff448989e2cbb8f729f8c1197` (24 files) |
| Payload r5 | `d2-hostb-payload-r5.tgz` `537a6590a297ecb77499fdd101c5860d84e2defb3250042d16707982e2f212fa`; `PAYLOAD-MANIFEST.sha256` `8605d96c7d96b7cc5fab6f6bb7bf22c8fa780d0c6fba15bae40e191c3ca68b2b`; `ARTIFACTS.sha256` `9a7829fe…3be` (161); `SYNTHETIC-CORPUS.sha256` `c7203a12…cc23` (33) |
| Host-B tree (bench, scripts/setup, manifests) | C `5bbe78a6f2ab6ba0a202aa3a39662bb482afa3c8075eb2feb121951387d7d4b2`; en_US.UTF-8 `de21eff6a57e7272761a296f8943ece0ac75c8137eecfcb5a8564352bc967e9f` (observed in the r5 test-resume) |
| Image | `sha256:9024dbc83b8168363c07d710dcc5e55d6831294a3e7970c28108e31b0b0bfcd7` (linux/amd64; 10 layers; base `node:18.20.8-bookworm-slim@sha256:f9ab18e3…` local id `101e0128c8ea…`) — `IMAGE-r5.json` |
| r4 → r5 image | only content difference `opt/zcorp/check_resume_test.js` (V2-D-66) |
| Host-B location | `~/Workspace/Z-CORP-V2-workstation/prover/d2-r5/repo`; campaign output `results/V2-PRV-D2-01` (campaign id `V2-PRV-D2-01-run1`) — `PAYLOAD-AND-TREE-r5.json` |
| Host-A reference | schedule `f7e6de3b…b95`, execution plan `99fb360c…c94` (campaign-20260925T060607Z); Host A statistics = V2-PRV-D3-01 (`SHA256SUMS` `026e249b…b83a`; script `94c3ad06…`) |

## 3. Readiness evidence (all untimed engineering)

| Checkpoint | Evidence |
|---|---|
| Setup | r5 `setup-20261005T140456Z` SETUP PASS, 161 / 161 (`research/results/v2/V2-PRV-D2-01/r5-setup-20261005T140456Z/`, `3e767ea5…5962`) |
| Preflight | `preflight-20261005T111235Z` PASS (r4; carried forward, V2-D-66) |
| Dry run | `dryrun-20261005T123643Z` PASS 14 / 14, 3 / 3 (r4; carried forward by owner adjudication, V2-D-63 / V2-D-66) |
| Resume test | `dryrun-resumetest-20261005T141557Z` (r5) RESUME TEST PASS 12 / 12, validation 14 / 14, 4 / 4 (V2-D-67; `owner-local-resumetest-20261005T141557Z/`, `672685be…baa5`). The r4 test-resume stays FAIL 10 / 12 permanently (V2-D-64) |
| Dry-run telemetry review | quiet-window stops V2-D-57, V2-D-61, V2-D-62 classified host-not-quiet (frozen direct criteria); no further threshold change exists or is needed |

## 4. `d2_analysis.py` (frozen here)

`d2_analysis.py` `3f80cc8f45ce381c9832be6bc809d05f244c79621e5071c86335de6f907d5fa4` = `d3_reanalysis.py` v1.1
(`94c3ad06…`) with Host-B paths and an input manifest of the frozen Host-B evidence (`--campaign`, `--manifest`; 13 inputs
must be listed with matching sha256; campaign identity mode `campaign`, kit `v3-x86`, Host-A schedule and plan), seed
namespace `20261004|D2|<key>` (prereg §6), outputs `D2-*`, no `prover_per_round` reconciliation (V1 manuscript table; no
Host-B counterpart); every estimator, definition, row selection, row-count check and output column unchanged
(`d2_analysis-vs-d3_reanalysis.diff`). Engineering test on copies of the Host-A (D3) inputs, never on Host-B data
(`d2-analysis-engineering-test/`): T1 with the D3 seed function → all four statistics files byte-identical to the frozen
V2-PRV-D3-01 outputs, reconciliation 462 / 462 and 48 / 48; T2 D2 seeds → every non-bootstrap column identical, seeds per
the prereg formula; T3 CLI check / run exit 0, outputs identical to T2; T4 tampered input, unlisted input (exit 3),
Host-A record without kit, mode dryrun, other schedule (exit 4), incomplete campaign (row count) → abort before any
statistics. ALL OK. Python 3.10.12 (test) — Host A outputs were reproduced byte for byte.
Side-by-side Host A / Host B tables are assembled from the frozen V2-PRV-D3-01 outputs and the d2_analysis outputs with
the allocation semantics in the header; no further estimator.

## 5. Scope (unchanged)

SUPPORTING evidence; cross-host replication at cpu2 / cpu4 / cpu8; Host A and Host B analysed side by side, never pooled;
no ARM-vs-x86 population claim; no GPU claim; no > 8-core arm in D2 (a 16 / 32-core Host-B extension would be a separate
experiment).

## 6. Timing gate

Owner-local sequence prepared, not executed: `outputs/workstation-relay/prepared/d2-r5/D2-R5-TIMED-WINDOW-COMMANDS.md`
(`1ee93b20b6d8510f3b398b2a6972f0eb825256c8b3ce03e4aaac1f320d209e6c`). Requires the explicit chat line
`AUTHORIZE D2 TIMED WINDOW: <window-id>` and an owner-declared dedicated quiet window.
