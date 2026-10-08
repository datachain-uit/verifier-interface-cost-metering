#!/usr/bin/env python3
"""DEV-D2-1 off-host engineering test: runs the unchanged v3-x86 record_controls.js and the r2 record_controls.js (node,
no container, no Docker) on fixture control directories and records each verdict (exit 0 = PASS, 3 = FAIL).
Recorded cases reuse copies of the preserved Host-A and Host-B control files (the evidence itself is only read).
usage: oracle_test.py <v2-root> <scratch-dir> <out.json>"""
import json, os, shutil, subprocess, sys
V2, SCR, OUT = sys.argv[1:4]
KITS = {'v3-x86': f'{V2}/research/csi/protocols/v2/prover-D2/kit-v3-x86', 'v3-x86-r2': f'{V2}/research/csi/protocols/v2/prover-D2-amendments/kit-v3-x86-r2'}
REC = {'Host A recorded (S20260925T060607Z)': f'{V2}/research/results/postcorr-20260925/environment/preflight/S20260925T060607Z',
       'Host B recorded (S20261005T074450Z)': f'{V2}/research/results/v2/V2-PRV-D2-01/owner-local-preflight-20261005T074450Z/repo/build/campaigns/preflight-20261005T074450Z/environment/preflight/S20261005T074450Z'}
def synth(os_cpus, pool, mx=97, qx=97, nx=0, size=2):
    return {'controls-exit.txt': f'size {size}\nno-adapter {nx}\nmismatch {mx}\nquota-only {qx}\n',
            'control-no-adapter.out': 'ZCORP_PREFLIGHT_JSON ' + json.dumps({'mode': 'probe', 'environment': {'os_cpus_length': os_cpus, 'available_parallelism': size}, 'ffjs_concurrency': pool}) + '\n',
            'control-mismatch.err': '[cpu-visibility] ABORT: (fixture)\n', 'control-quota-only.err': '[cpu-visibility] ABORT: (fixture)\n'}
CASES = [('Host A recorded (S20260925T060607Z)', None, 'PASS', 'PASS'), ('Host B recorded (S20261005T074450Z)', None, 'FAIL', 'PASS'),
         ('pool constrained to the allocation (os 112, pool 2)', synth(112, 2), 'FAIL', 'FAIL'),
         ('uncapped pool (os 112, pool 112)', synth(112, 112), 'PASS', 'FAIL'),
         ('arbitrary off-rule pool (os 112, pool 10)', synth(112, 10), 'FAIL', 'FAIL'),
         ('mismatch not refused (exit 0)', synth(112, 64, mx=0), 'FAIL', 'FAIL'),
         ('quota-only not refused (exit 0)', synth(112, 64, qx=0), 'FAIL', 'FAIL'),
         ('no-adapter probe failed (exit 1)', synth(112, 64, nx=1), 'FAIL', 'FAIL'),
         ('edge: exactly 64 CPUs (os 64, pool 64)', synth(64, 64), 'PASS', 'PASS')]
rows, ok = [], True
for i, (name, files, exp_old, exp_new) in enumerate(CASES):
    row = {'case': name, 'expected_old': exp_old, 'expected_new': exp_new}
    for kit, kd in KITS.items():
        res = os.path.join(SCR, f'case{i:02d}-{kit}'); sd = os.path.join(res, 'environment', 'preflight', 'STEST')
        os.makedirs(sd, exist_ok=True)
        if files is None:
            for f in ('controls-exit.txt', 'control-no-adapter.out', 'control-mismatch.err', 'control-quota-only.err'):
                shutil.copyfile(os.path.join(REC[name], f), os.path.join(sd, f))
        else:
            for f, t in files.items(): open(os.path.join(sd, f), 'w').write(t)
        p = subprocess.run(['node', os.path.join(kd, 'record_controls.js')], env=dict(os.environ, ZCORP_RESULTS=res, ZCORP_SESSION_ID='STEST'), capture_output=True, text=True)
        verdict = {0: 'PASS', 3: 'FAIL'}.get(p.returncode, f'ERROR rc={p.returncode}')
        row[kit] = verdict; row[kit + '_stdout'] = p.stdout.strip()
    row['match'] = row['v3-x86'] == exp_old and row['v3-x86-r2'] == exp_new; ok &= row['match']; rows.append(row)
json.dump({'test': 'DEV-D2-1 oracle engineering test (off-host, no container, untimed)', 'node': subprocess.run(['node', '--version'], capture_output=True, text=True).stdout.strip(),
           'all_match': ok, 'rows': rows}, open(OUT, 'w'), indent=1)
for r in rows: print(f"{r['case']:52s} v3-x86={r['v3-x86']:4s} r2={r['v3-x86-r2']:4s} expected {r['expected_old']}/{r['expected_new']} {'OK' if r['match'] else 'MISMATCH'}")
print('ALL MATCH' if ok else 'MISMATCH'); sys.exit(0 if ok else 1)
