#!/usr/bin/env python3
"""DEV-D2-2 off-host engineering test (node, no container, no Docker, untimed). Copies of the preserved r3 dry-run
campaign directory are validated with the r3 (frozen) and r4 (DEV-D2-2) summarize_prover.js; the evidence itself is only
read. Negative cases modify the integrity record of a copy.
usage: validator_test.py <v2-root> <scratch-dir> <out.json>"""
import json, os, shutil, subprocess, sys
V2, SCR, OUT = sys.argv[1:4]
AM = f'{V2}/research/csi/protocols/v2/prover-D2-amendments'
KITS = {'r3': f'{AM}/kit-v3-x86-r3/summarize_prover.js', 'r4': f'{AM}/kit-v3-x86-r4/summarize_prover.js'}
SRC = f'{V2}/research/results/v2/V2-PRV-D2-01/owner-local-dryrun-20261005T094307Z/repo/build/campaigns/dryrun-20261005T094307Z'
SID = 'S20261005T094307Z'; INTEG = f'environment/integrity-{SID}.json'
REC = json.load(open(f'{SRC}/derived/validation.json'))
def run(kit, name, mutate=None):
    d = os.path.join(SCR, f'{name}-{kit}'); shutil.copytree(SRC, d)
    if mutate: mutate(d)
    vf = os.path.join(d, 'derived', 'validation.json')
    if os.path.exists(vf): os.remove(vf)   # copy only: ensures the result read below is this run's own output
    p = subprocess.run(['node', KITS[kit]], env=dict(os.environ, ZCORP_RESULTS=d, ZCORP_SESSION_ID=SID), capture_output=True, text=True)
    v = json.load(open(vf)) if os.path.exists(vf) else None
    chk = {c['name']: c['passed'] for c in v['checks']} if v else None
    det = {c['name']: c['detail'] for c in v['checks']} if v else None
    return {'exit': p.returncode, 'passed': v['passed'] if v else None, 'n_pass': sum(chk.values()) if chk else None, 'n': len(chk) if chk else None,
            'checks': chk, 'details': det, 'accepted_rounds': v.get('accepted_rounds') if v else None, 'stderr_tail': p.stderr.strip()[-300:]}
def setk(k, val):
    def f(d):
        p = os.path.join(d, INTEG); j = json.load(open(p)); j[k] = val; json.dump(j, open(p, 'w'), indent=2)
    return f
def delk(k):
    def f(d):
        p = os.path.join(d, INTEG); j = json.load(open(p)); j.pop(k); json.dump(j, open(p, 'w'), indent=2)
    return f
def rm(d):
    for n in (INTEG, 'environment/integrity.json'):
        p = os.path.join(d, n)
        if os.path.exists(p): os.remove(p)
def malformed(d): open(os.path.join(d, INTEG), 'w').write('{"session_id": "S20261005T094307Z", "manifest_before_ok": tru')
res = {'source': SRC, 'recorded_validation': {c['name']: c['passed'] for c in REC['checks']}}
def at_validation_time(d):
    # copy only: the runner validates before it appends this session's 'end' row to sessions.csv (it is written by
    # fail()/session_event after summarize_prover.js returns); remove that row to replay the state at validation time
    p = os.path.join(d, 'environment', 'sessions.csv'); L = open(p).read().split('\n')
    open(p, 'w').write('\n'.join(l for l in L if not (f',{SID},end,' in l)))
res['positive'] = {k: run(k, 'positive', at_validation_time) for k in ('r3', 'r4')}
res['positive_as_preserved'] = {k: run(k, 'preserved') for k in ('r3', 'r4')}
rec_det = {c['name']: c['detail'] for c in REC['checks']}
r3, r4 = res['positive']['r3'], res['positive']['r4']
ok = True
res['r3_reproduces_recorded'] = r3['checks'] == res['recorded_validation'] and all(r3['details'][n] == rec_det[n] for n in rec_det)
res['r4_14_of_14'] = r4['passed'] is True and r4['n_pass'] == 14 and r4['n'] == 14 and r4['exit'] == 0
res['r4_accepted_rounds'] = r4['accepted_rounds']
res['r4_other_checks_identical'] = all(r4['checks'][n] == r3['checks'][n] and r4['details'][n] == r3['details'][n] for n in r3['checks'] if n != 'repository_unchanged')
rp = res['positive_as_preserved']
res['as_preserved'] = {'r3': f"{rp['r3']['n_pass']}/{rp['r3']['n']}", 'r4': f"{rp['r4']['n_pass']}/{rp['r4']['n']}", 'r4_passed': rp['r4']['passed'],
                       'note': "sessions.csv as preserved (with the later 'end' row): the session is listed twice in the r3 detail; verdicts identical"}
ok &= res['r3_reproduces_recorded'] and res['r4_14_of_14'] and res['r4_accepted_rounds'] == 3 and res['r4_other_checks_identical'] and rp['r4']['passed'] is True and rp['r4']['n_pass'] == 14
NEG = [('manifest_after_ok = false', setk('manifest_after_ok', False)), ('corpus_after_ok = false', setk('corpus_after_ok', False)),
       ('tree_unchanged = false', setk('tree_unchanged', False)), ('manifest_before_ok = false', setk('manifest_before_ok', False)),
       ('missing integrity record', rm), ('tree_unchanged field missing', delk('tree_unchanged')), ('corpus_after_ok field missing', delk('corpus_after_ok')),
       ('manifest_after_ok field missing', delk('manifest_after_ok')), ('malformed integrity JSON', malformed)]
res['negative'] = []
for i, (name, m) in enumerate(NEG):
    r = run('r4', f'neg{i}', m)
    rep = r['checks']['repository_unchanged'] if r['checks'] else None
    others_same = r['checks'] is not None and all(r['checks'][n] == r4['checks'][n] for n in r4['checks'] if n != 'repository_unchanged')
    fail_closed = (rep is False and r['passed'] is False and r['exit'] != 0) or (r['checks'] is None and r['exit'] != 0)
    res['negative'].append({'case': name, 'exit': r['exit'], 'repository_unchanged': rep, 'validation_passed': r['passed'], 'other_checks_unchanged': others_same if r['checks'] else None, 'fail_closed': fail_closed, 'stderr_tail': r['stderr_tail'] if r['checks'] is None else ''})
    ok &= fail_closed
res['all_as_expected'] = ok
json.dump(res, open(OUT, 'w'), indent=1)
print('as preserved:', res['as_preserved'])
print('recorded r3 validation reproduced by frozen r3 validator:', res['r3_reproduces_recorded'], f"(r3 {r3['n_pass']}/{r3['n']}, exit {r3['exit']})")
print(f"r4 positive: {r4['n_pass']}/{r4['n']} passed={r4['passed']} exit={r4['exit']} accepted_rounds={r4['accepted_rounds']} repository_unchanged={r4['checks']['repository_unchanged']} detail='{r4['details']['repository_unchanged']}' other checks identical={res['r4_other_checks_identical']}")
for n in res['negative']: print(f"NEG {n['case']:30s} exit={n['exit']} repository_unchanged={n['repository_unchanged']} validation_passed={n['validation_passed']} others_unchanged={n['other_checks_unchanged']} fail_closed={n['fail_closed']} {n['stderr_tail'][-120:]}")
print('ALL AS EXPECTED' if ok else 'NOT AS EXPECTED'); sys.exit(0 if ok else 1)
