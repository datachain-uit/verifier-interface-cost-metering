#!/usr/bin/env python3
"""AMD-D2-1 off-host engineering test (no runner, no container, no Docker, untimed).
1. self-tests of the r2 (pre-amendment) and r3 (amended) hostb_quiet.py;
2. replay of the preserved r2 dry-run snapshot pairs (session start; pre-container 1) through both gates with the runner's
   exact arguments (--mode pre --alloc 1-8 --frozen <FROZEN_STATE of run-campaign.sh>);
3. perturbed copies of the container-1 pair (direct CPU, sibling, other-CPU, container, frozen-state, inhibitor
   violations; during-mode checks) must still be rejected by the amended gate.
The preserved evidence is only read; perturbed copies are written to a scratch directory.
usage: gate_replay_test.py <v2-root> <scratch-dir> <out.json>"""
import copy, json, os, subprocess, sys
V2, SCR, OUT = sys.argv[1:4]
AM = f'{V2}/research/csi/protocols/v2/prover-D2-amendments'
GATES = {'r2 (load1 <= 2.0)': f'{AM}/kit-v3-x86-r2/hostb_quiet.py', 'r3 (AMD-D2-1)': f'{AM}/kit-v3-x86-r3/hostb_quiet.py'}
Q = f'{V2}/research/results/v2/V2-PRV-D2-01/owner-local-dryrun-20261005T084400Z/repo/build/campaigns/dryrun-20261005T084400Z/environment/quiet/S20261005T084400Z'
FROZEN = 'intel_pstate=active governor=powersave no_turbo=0 numa_balancing=1 thp=madvise'
os.makedirs(SCR, exist_ok=True)
res = {'selftest': {}, 'cases': []}; ok = True
for g, f in GATES.items():
    p = subprocess.run(['python3', f, 'selftest'], capture_output=True, text=True)
    res['selftest'][g] = {'exit': p.returncode, 'output': p.stdout.strip().split('\n')}
    ok &= p.returncode == 0
def run(gate, a, b, mode='pre', alloc='1-8'):
    p = subprocess.run(['python3', GATES[gate], 'check', a, b, '--mode', mode, '--alloc', alloc, '--frozen', FROZEN], capture_output=True, text=True)
    r = json.loads(p.stdout); return p.returncode, r
def busy_set(b, a, cpu, u):
    dt = b['stat'][cpu]['total'] - a['stat'][cpu]['total']
    if dt <= 0: dt = 200
    b['stat'][cpu] = {'total': a['stat'][cpu]['total'] + dt, 'idle': a['stat'][cpu]['idle'] + int(round(dt * (1 - u)))}
A1, B1 = json.load(open(f'{Q}/c0001-pre-a.json')), json.load(open(f'{Q}/c0001-pre-b.json'))
def variant(name, fn):
    a, b = copy.deepcopy(A1), copy.deepcopy(B1); fn(a, b)
    pa, pb = os.path.join(SCR, name + '-a.json'), os.path.join(SCR, name + '-b.json')
    json.dump(a, open(pa, 'w')); json.dump(b, open(pb, 'w')); return pa, pb
CASES = [
 ('recorded session start (S20261005T084400Z)', f'{Q}/session-a.json', f'{Q}/session-b.json', 'pre', True, True),
 ('recorded pre-container 1 (c0001)', f'{Q}/c0001-pre-a.json', f'{Q}/c0001-pre-b.json', 'pre', False, True),
 ('c0001 + allocated CPU 3 busy 0.50', *variant('alloc3', lambda a, b: busy_set(b, a, '3', 0.5)), 'pre', False, False),
 ('c0001 + SMT sibling 60 busy 0.50', *variant('sib60', lambda a, b: busy_set(b, a, '60', 0.5)), 'pre', False, False),
 ('c0001 + other CPUs 20-29 busy 0.15 each', *variant('other', lambda a, b: [busy_set(b, a, str(c), 0.15) for c in range(20, 30)]), 'pre', False, False),
 ('c0001 + 1 running container', *variant('cont', lambda a, b: b.__setitem__('running_containers', 1)), 'pre', False, False),
 ('c0001 + governor performance', *variant('gov', lambda a, b: b['state'].__setitem__('governor', 'performance')), 'pre', False, False),
 ('c0001 + no_turbo 1', *variant('turbo', lambda a, b: b['state'].__setitem__('no_turbo', '1')), 'pre', False, False),
 ('c0001 + THP always', *variant('thp', lambda a, b: b['state'].__setitem__('thp', 'always')), 'pre', False, False),
 ('c0001 + inhibitor not held', *variant('inh', lambda a, b: b.__setitem__('inhibit', 0)), 'pre', False, False),
 ('during: c0001 + SMT sibling 57 busy 0.10', *variant('dsib', lambda a, b: busy_set(b, a, '57', 0.10)), 'during', False, False),
 ('during: c0001 + other CPUs 20-39 busy 0.10 each', *variant('doth', lambda a, b: [busy_set(b, a, str(c), 0.10) for c in range(20, 40)]), 'during', False, False),
 ('during: c0001 + allocated CPUs 1-8 busy 1.0 (own container)', *variant('dalloc', lambda a, b: [busy_set(b, a, str(c), 1.0) for c in range(1, 9)]), 'during', True, True),
]
for name, pa, pb, mode, exp_old, exp_new in CASES:
    row = {'case': name, 'mode': mode, 'expected': {'r2 (load1 <= 2.0)': exp_old, 'r3 (AMD-D2-1)': exp_new}}
    for g in GATES:
        rc, r = run(g, pa, pb, mode)
        row[g] = {'accepted': r['accepted'], 'exit': rc, 'violations': r['violations'], 'loadavg_recorded': r['loadavg'],
                  'busy_alloc_max': r['busy_alloc_max'], 'busy_siblings_max': r['busy_siblings_max'], 'busy_other_cpu_equiv': r['busy_other_cpu_equiv']}
        ok &= r['accepted'] == row['expected'][g] and (rc == 0) == r['accepted']
    res['cases'].append(row)
c1 = res['cases'][1]
res['c0001_old_rejected_only_for_load1'] = c1['r2 (load1 <= 2.0)']['violations'] == ['load1 2.04 > 2.0']
res['c0001_new_accepted_no_violations_load_recorded'] = c1['r3 (AMD-D2-1)']['violations'] == [] and c1['r3 (AMD-D2-1)']['loadavg_recorded'].startswith('2.04')
ok &= res['c0001_old_rejected_only_for_load1'] and res['c0001_new_accepted_no_violations_load_recorded']
res['all_as_expected'] = ok
json.dump(res, open(OUT, 'w'), indent=1)
for g, s in res['selftest'].items(): print(f"selftest {g}: exit {s['exit']}; " + '; '.join(s['output']))
for r in res['cases']:
    print(f"{r['case']:58s} r2={'ACCEPT' if r['r2 (load1 <= 2.0)']['accepted'] else 'REJECT'} {r['r2 (load1 <= 2.0)']['violations']} | r3={'ACCEPT' if r['r3 (AMD-D2-1)']['accepted'] else 'REJECT'} {r['r3 (AMD-D2-1)']['violations']}")
print('c0001 old rejected only for load1:', res['c0001_old_rejected_only_for_load1'], '| new accepted, load recorded:', res['c0001_new_accepted_no_violations_load_recorded'])
print('ALL AS EXPECTED' if ok else 'NOT AS EXPECTED'); sys.exit(0 if ok else 1)
