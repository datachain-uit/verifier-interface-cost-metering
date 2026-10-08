#!/usr/bin/env python3
"""Engineering replay (audit only) of check_resume_test.js on COPIES of the preserved resume-test campaign
dryrun-resumetest-20261005T130639Z: frozen r4 oracle vs kit-v3-x86-r5 oracle (DEV-D2-3 applied), plus negative cases. Never touches the evidence."""
import csv, io, json, os, shutil, subprocess, sys, hashlib
SRC, KITLIB, FROZEN, PROPOSED, WORK = sys.argv[1:6]
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def run(oracle, mutate=None, label=''):
    d = os.path.join(WORK, 'case'); shutil.rmtree(d, ignore_errors=True); shutil.copytree(SRC, d)
    rt = os.path.join(d, 'environment', 'resume-test', 'resume-test.json')
    if os.path.exists(rt): os.remove(rt)                      # the oracle rewrites it; start clean
    if mutate:
        p = os.path.join(d, 'environment', 'sessions.csv'); rows = list(csv.reader(open(p, newline='')))
        rows = mutate(rows); f = io.StringIO()
        w = csv.writer(f, lineterminator='\n', quoting=csv.QUOTE_MINIMAL); [w.writerow(r) for r in rows]
        open(p, 'w').write(f.getvalue())
    k = os.path.join(WORK, 'kit'); shutil.rmtree(k, ignore_errors=True); os.makedirs(k)
    shutil.copytree(KITLIB, os.path.join(k, 'lib')); shutil.copy(oracle, os.path.join(k, 'check_resume_test.js'))
    r = subprocess.run(['node', os.path.join(k, 'check_resume_test.js')], env={**os.environ, 'ZCORP_RESULTS': d}, capture_output=True, text=True)
    j = json.load(open(rt)) if os.path.exists(rt) else {}
    res = {c['name']: c['passed'] for c in j.get('checks', [])}
    return {'case': label, 'exit': r.returncode, 'summary': (r.stdout.strip().splitlines() or [''])[-1], 'checks': res, 'stderr': r.stderr.strip()[-300:]}
DET = 15
def setdet(sid, ev, val):
    def m(rows):
        for r in rows[1:]:
            if r[1] == sid and r[2] == ev: r[DET] = val
        return rows
    return m
S1, S2, S3 = 'S20261005T130639Z', 'S20261005T131700Z', 'S20261005T132500Z'
strip = lambda rows: [rows[0]] + [r[:DET] + [r[DET].replace('window none; ', '', 1)] + r[DET + 1:] for r in rows[1:]]
cases = [
 ('frozen oracle, as recorded', FROZEN, None),
 ('frozen oracle, v3 detail format (prefix removed)', FROZEN, strip),
 ('r5 oracle, as recorded', PROPOSED, None),
 ('r5 oracle, v3 detail format (prefix removed)', PROPOSED, strip),
 ('r5 oracle, declared window id "W-TEST-1"', PROPOSED, lambda rows: [rows[0]] + [r[:DET] + [r[DET].replace('window none; ', 'window W-TEST-1; ', 1)] + r[DET + 1:] for r in rows[1:]]),
 ('NEG r5: session-1 end not a planned stop ("window none; PASS")', PROPOSED, setdet(S1, 'end', 'window none; PASS')),
 ('NEG r5: session-1 end "window none; FAIL: ..."', PROPOSED, setdet(S1, 'end', 'window none; FAIL: host conditions not met at session start')),
 ('NEG r5: session-1 end row missing', PROPOSED, lambda rows: [r for r in rows if not (r[1] == S1 and r[2] == 'end')]),
 ('NEG r5: session-2 start marked "new"', PROPOSED, setdet(S2, 'start', 'window none; new')),
 ('NEG r5: session-3 start marked "new"', PROPOSED, setdet(S3, 'start', 'window none; new')),
 ('NEG r5: only two session starts', PROPOSED, lambda rows: [r for r in rows if not (r[1] == S3 and r[2] == 'start')]),
 ('NEG r5: session 3 reuses session-2 id', PROPOSED, lambda rows: [rows[0]] + [r[:1] + [S2 if r[1] == S3 else r[1]] + r[2:] for r in rows[1:]]),
 ('NEG r5: "resume" only inside a longer detail ("window none; not resume")', PROPOSED, setdet(S2, 'start', 'window none; not resume')),
]
out = {'source_campaign': SRC, 'frozen_oracle_sha256': sha(FROZEN), 'r5_oracle_sha256': sha(PROPOSED), 'cases': []}
rec = json.load(open(os.path.join(SRC, 'environment', 'resume-test', 'resume-test.json')))
out['recorded'] = {c['name']: c['passed'] for c in rec['checks']}
TWO = ('three_sessions_with_new_ids', 'session1_clean_planned_stop')
EXPECT = {0: (9, set(TWO)), 1: (0, set()), 2: (0, set()), 3: (0, set()), 4: (0, set())}
for i, (label, oracle, mut) in enumerate(cases):
    r = run(oracle, mut, label)
    if oracle == PROPOSED:      # the same input through the frozen r4 oracle: every other check must be identical
        f = run(FROZEN, mut, label + ' [frozen r4 oracle, same input]')
        r['other_checks_identical_to_frozen'] = all(r['checks'][k] == f['checks'][k] for k in r['checks'] if k not in TWO)
    if i in EXPECT:
        ex, exf = EXPECT[i]; failed = {k for k, v in r['checks'].items() if not v}
        r['as_expected'] = r['exit'] == ex and failed == exf
    else:                       # negative cases: exit 9 and the targeted predicate fails
        target = 'session1_clean_planned_stop' if 'session-1 end' in label else 'three_sessions_with_new_ids'
        r['as_expected'] = r['exit'] == 9 and not r['checks'].get(target, True)
    out['cases'].append(r)
    fails = [k for k, v in r['checks'].items() if not v]
    print(f"{label}: exit {r['exit']}; {r['summary']}; failed={fails}; as_expected={r['as_expected']}" + (f"; other checks identical to frozen={r['other_checks_identical_to_frozen']}" if 'other_checks_identical_to_frozen' in r else '') + (f"; stderr={r['stderr']}" if r['stderr'] else ''))
out['frozen_replay_equals_recorded'] = out['cases'][0]['checks'] == out['recorded']
print('frozen replay identical to the recorded resume-test.json checks:', out['frozen_replay_equals_recorded'])
out['all_as_expected'] = out['frozen_replay_equals_recorded'] and all(c['as_expected'] for c in out['cases']) and all(c.get('other_checks_identical_to_frozen', True) for c in out['cases'])
print('ALL AS EXPECTED' if out['all_as_expected'] else 'NOT ALL AS EXPECTED')
for c in out['cases']: c.pop('stderr', None)
out['source_campaign'] = 'research/results/v2/V2-PRV-D2-01/owner-local-dryrun-20261005T123643Z-resumetest-20261005T130639Z/repo/build/campaigns/dryrun-resumetest-20261005T130639Z (copied per case; never modified)'
json.dump(out, open(os.path.join(WORK, 'dev-d2-3-oracle-test-results.json'), 'w'), indent=1)
