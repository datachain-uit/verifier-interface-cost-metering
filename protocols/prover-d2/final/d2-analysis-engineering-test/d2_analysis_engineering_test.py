#!/usr/bin/env python3
"""Engineering test of d2_analysis.py (V2-PRV-D2-01) — off-host, on COPIES of the frozen Host-A campaign (V1
campaign-20260925T060607Z, the D3 input); never on Host-B data (no Host-B timing exists). Stdlib only.
  T1 equivalence: d2_analysis load_raw / reconcile / stats with the D3 seed function -> outputs byte-identical to the frozen
     V2-PRV-D3-01 outputs (the computations are unchanged).
  T2 D2 seeds: same inputs, D2 seed namespace -> every non-bootstrap column identical to D3; bootstrap seeds equal
     int(sha256("20261004|D2|<key>")[:16], 16).
  T3 CLI positive: Host-A copy whose CAMPAIGN.json carries kit v3-x86 (identity otherwise Host A) + manifest -> check and run
     exit 0; run outputs identical to T2.
  T4 CLI negatives: tampered input, input missing from the manifest, original Host-A record (no kit), mode dryrun,
     other schedule, incomplete campaign -> abort before any statistics."""
import csv, filecmp, hashlib, importlib.util, json, os, shutil, subprocess, sys
ROOT, D2, D3OUT, WORK = sys.argv[1:5]
SRC = os.path.join(ROOT, 'research/results/postcorr-20260925')
spec = importlib.util.spec_from_file_location('d2a', D2); d2a = importlib.util.module_from_spec(spec); spec.loader.exec_module(d2a)
res = {'d2_analysis_sha256': d2a.sha(D2), 'tests': {}}
def mk(name, mutate_campaign=None, mutate_files=None, manifest_skip=()):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True); c = os.path.join(d, 'campaign')
    for rel in d2a.INPUTS:
        os.makedirs(os.path.dirname(os.path.join(c, rel)), exist_ok=True); shutil.copy(os.path.join(SRC, rel), os.path.join(c, rel))
    if mutate_campaign:
        j = json.load(open(os.path.join(c, 'CAMPAIGN.json'))); mutate_campaign(j); json.dump(j, open(os.path.join(c, 'CAMPAIGN.json'), 'w'), indent=2)
    if mutate_files: mutate_files(c)
    with open(os.path.join(d, 'SHA256SUMS'), 'w') as f:
        for rel in d2a.INPUTS:
            if rel not in manifest_skip: f.write(f"{d2a.sha(os.path.join(c, rel))}  ./campaign/{rel}\n")
    return d, c
def cli(d, c, mode, out):
    r = subprocess.run([sys.executable, D2, '--campaign', c, '--manifest', os.path.join(d, 'SHA256SUMS'), '--out', out, '--mode', mode], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] if (r.stdout + r.stderr).strip() else []
names = ['cell-stats', 'backend-ratios', 'allocation-speedups', 'zkey-diagnostic']
# T1
d, c = mk('t1'); o1 = os.path.join(WORK, 't1-out'); os.makedirs(o1, exist_ok=True)
seed_d2 = d2a.seed_for; d2a.seed_for = lambda key: int(hashlib.sha256(f'{d2a.BASE_SEED}|{key}'.encode()).hexdigest()[:16], 16)
rows, diag, acc = d2a.load_raw(c); rec = d2a.reconcile(c, rows, diag); outn = d2a.stats(rows, diag, o1); d2a.seed_for = seed_d2
d3rec = json.load(open(os.path.join(D3OUT, 'D3-reconciliation.json')))
same = {n: filecmp.cmp(os.path.join(o1, f'D2-{n}.csv'), os.path.join(D3OUT, f'D3-{n}.csv'), shallow=False) for n in names}
res['tests']['T1_equivalence_with_D3_seed'] = dict(rows=len(rows), diag=len(diag), outputs=outn, files_byte_identical_to_D3=same,
    reconciliation=dict(d2={k: rec[k] for k in ('prover_summary', 'prover_diag')}, d3={k: d3rec[k] for k in ('prover_summary', 'prover_diag')}, mismatches=len(rec['mismatches'])),
    ok=all(same.values()) and len(rows) == 495 and len(diag) == 240 and {k: rec[k] for k in ('prover_summary', 'prover_diag')} == {k: d3rec[k] for k in ('prover_summary', 'prover_diag')} and not rec['mismatches'])
# T2
o2 = os.path.join(WORK, 't2-out'); os.makedirs(o2, exist_ok=True); d2a.stats(rows, diag, o2)
BOOT = {'boot_median_lo95', 'boot_median_hi95', 'bootstrap_seed'}; t2 = {}
for n in names:
    a = list(csv.DictReader(open(os.path.join(o2, f'D2-{n}.csv')))); b = list(csv.DictReader(open(os.path.join(D3OUT, f'D3-{n}.csv'))))
    det_same = len(a) == len(b) and all({k: v for k, v in x.items() if k not in BOOT} == {k: v for k, v in y.items() if k not in BOOT} for x, y in zip(a, b))
    t2[n] = dict(rows=len(a), deterministic_columns_identical=det_same, bootstrap_columns_differ=any(x['boot_median_lo95'] != y['boot_median_lo95'] for x, y in zip(a, b)))
cell0 = next(csv.DictReader(open(os.path.join(o2, 'D2-cell-stats.csv'))))
key0 = f"cell|{cell0['allocation_profile']}|{cell0['backend']}|{cell0['depth']}|{cell0['rounds']}|{cell0['stage']}"
seed_ok = int(cell0['bootstrap_seed']) == int(hashlib.sha256(f'20261004|D2|{key0}'.encode()).hexdigest()[:16], 16)
res['tests']['T2_D2_seed_namespace'] = dict(files=t2, first_seed_matches_prereg_formula=seed_ok, ok=seed_ok and all(v['deterministic_columns_identical'] for v in t2.values()))
# T3
kit = lambda j: j.update(kit='v3-x86')
d, c = mk('t3', kit); o3 = os.path.join(WORK, 't3-out')
rc_check, last_check = cli(d, c, 'check', o3); rc_run, last_run = cli(d, c, 'run', o3)
same3 = {n: filecmp.cmp(os.path.join(o3, f'D2-{n}.csv'), os.path.join(o2, f'D2-{n}.csv'), shallow=False) for n in names}
rr = json.load(open(os.path.join(o3, 'D2-RUN-RECORD.json')))
res['tests']['T3_cli_positive'] = dict(check_exit=rc_check, run_exit=rc_run, run_outputs=rr.get('outputs'), script_sha256_in_record=rr['script_sha256'], outputs_identical_to_T2=same3,
    ok=rc_check == 0 and rc_run == 0 and all(same3.values()) and rr['script_sha256'] == res['d2_analysis_sha256'])
# T4
neg = {}
d, c = mk('t4a', kit); p = os.path.join(c, 'prover/cpu4/runs.csv'); open(p, 'a').write('\n')   # changed after the manifest was written
neg['tampered_input_after_manifest'] = cli(d, c, 'check', os.path.join(WORK, 't4a-out'))
d, c = mk('t4b', kit, manifest_skip=('prover/cpu8/diag.csv',)); neg['input_missing_from_manifest'] = cli(d, c, 'check', os.path.join(WORK, 't4b-out'))
d, c = mk('t4c'); neg['host_a_record_without_kit'] = cli(d, c, 'check', os.path.join(WORK, 't4c-out'))
d, c = mk('t4d', lambda j: j.update(kit='v3-x86', mode='dryrun')); neg['mode_dryrun'] = cli(d, c, 'check', os.path.join(WORK, 't4d-out'))
d, c = mk('t4e', lambda j: j.update(kit='v3-x86', schedule_sha256='0' * 64)); neg['other_schedule'] = cli(d, c, 'check', os.path.join(WORK, 't4e-out'))
def drop_round(c):
    p = os.path.join(c, 'prover/cpu8/runs.csv'); rows_ = list(csv.DictReader(open(p, newline=''))); keep = [r for r in rows_ if not (r['kind'] == 'primary' and r['round'] == '3')]
    with open(p, 'w', newline='') as f: w = csv.DictWriter(f, fieldnames=list(rows_[0].keys())); w.writeheader(); w.writerows(keep)
d, c = mk('t4f', kit, drop_round); neg['incomplete_campaign'] = cli(d, c, 'run', os.path.join(WORK, 't4f-out'))
expect = dict(tampered_input_after_manifest=3, input_missing_from_manifest=3, host_a_record_without_kit=4, mode_dryrun=4, other_schedule=4, incomplete_campaign=1)
stats_written = {k: any(os.path.exists(os.path.join(WORK, f't4{x}-out', f'D2-{n}.csv')) for n in names) for k, x in zip(expect, 'abcdef')}
res['tests']['T4_cli_negatives'] = dict(results={k: dict(exit=v[0], last_line=v[1], expected_exit=expect[k], statistics_written=stats_written[k]) for k, v in neg.items()},
    ok=all(neg[k][0] == expect[k] and not stats_written[k] for k in expect))
res['all_ok'] = all(t['ok'] for t in res['tests'].values())
json.dump(res, open(os.path.join(WORK, 'd2-analysis-engineering-test-results.json'), 'w'), indent=1, default=str)
for k, t in res['tests'].items(): print(k, 'OK' if t['ok'] else 'FAIL')
print('ALL OK' if res['all_ok'] else 'NOT ALL OK')
