#!/usr/bin/env python3
"""V2-C2 scoring (stage 4; after the registered FFLONK cells). Separate from C1 / H8; never merged with any C1 score.
usage: c2_score.py <stage-2 dir with C2-STAGE2-PREDICTIONS.json + SHA256SUMS> <fflonk-structural.jsonl> <pilot/full/fflonk records ...> --out <dir>
Checks: stage-2 SHA256SUMS; consistency gate (the registered EVM-Osaka trace of every FFLONK proof has the same opcode counts,
precompile counts, keccak sizes and copies as its stage-2 structural record; a mismatch makes that proof NOT COMPARABLE and
is reported as a deviation). Scores: C2-PRIMARY (every comparable proof |e| <= tau; any proof outside -> FAIL; any proof not
comparable or missing -> NOT EVALUABLE for the claim), C2-EXACT (r = 0 for every proof), C2-RANK and C2-XOVER (determinate
predictions only). C2_ENGINEERING_TEST=1 scores an engineering-test prediction file (non-FFLONK) for pipeline tests only."""
import csv, hashlib, json, os, statistics, sys
args = sys.argv[1:]; OUT = args[args.index('--out') + 1]; args = args[:args.index('--out')]; S2, STR, RECS = args[0], args[1], args[2:]
os.makedirs(OUT, exist_ok=True); ENG = os.environ.get('C2_ENGINEERING_TEST') == '1'
for l in open(os.path.join(S2, 'SHA256SUMS')):
    h, f = l.split(maxsplit=1); f = f.strip().lstrip('*')
    if hashlib.sha256(open(os.path.join(S2, f), 'rb').read()).hexdigest() != h: raise SystemExit(f'stage-2 file changed after freeze: {f}')
P = json.load(open(os.path.join(S2, 'C2-STAGE2-PREDICTIONS.json'))); TAU = P['tau']
if not ENG and not P['label'].startswith('V2-C2 STAGE-2'): raise SystemExit('not a stage-2 prediction file')
struct = {json.loads(l)['proof_id']: json.loads(l) for l in open(STR) if l.strip()}
nat, evm, comp = {}, {}, {}
for f in RECS:
    for l in open(f):
        if not l.strip(): continue
        r = json.loads(l)
        if r.get('op') != 'verify_proof_direct' or r.get('role') != 'measurement': continue
        if r['env'] == 'zkos-v32' and r['regime'].get('npg') == 100 and not int(r['regime'].get('priority_fee') or 0):
            nat.setdefault(r['proof_id'], r['zkos']['computational_native'])
            if r['backend'] in ('groth16', 'plonk') and r.get('relation') == 'ctx': comp.setdefault((r['backend'], r['k']), {})[r['proof_id']] = r['zkos']['computational_native']
        if r['env'] == 'evm-osaka': evm.setdefault(r['proof_id'], r['evm_trace'])
rows = []
for p in P['per_proof']:
    pid = p['proof_id']; s = struct[pid]; fz = evm.get(pid)
    same = fz is not None and {k: v['n'] for k, v in fz['ops'].items()} == s['ops'] and fz['keccak_sizes'] == s['keccak_sizes'] and [list(x) for x in fz['copies']] == s['copies'] \
        and sorted((a, v['n']) for a, v in fz['precompiles'].items()) == sorted((a, sum(1 for c in s['precompile_calls'] if c['addr'] == a)) for a in {c['addr'] for c in s['precompile_calls']})
    n = nat.get(pid); r = None if n is None else n - p['N_hat']
    rows.append(dict(proof_id=pid, k=p['k'], N_hat=p['N_hat'], N_measured=n, residual=r, rel=None if r is None else r / p['N_hat'], within_tau=None if r is None else abs(r) <= TAU * p['N_hat'],
                     exact=None if r is None else r == 0, structural_consistent=same))
comparable = [x for x in rows if x['N_measured'] is not None and x['structural_consistent']]
primary = 'NOT EVALUABLE' if len(comparable) != len(rows) else ('PASS' if all(x['within_tau'] for x in rows) else 'FAIL')
if len(comparable) != len(rows) and any(x['within_tau'] is False for x in comparable): primary = 'FAIL'
exact = 'NOT EVALUABLE' if len(comparable) != len(rows) else ('PASS' if all(x['exact'] for x in rows) else 'FAIL')
rank = []
for q in P['ranking']:
    if q.get('predicted_sign') in (None, 'INDETERMINATE'): rank.append(dict(q, measured_sign=None, result='NOT SCORED')); continue
    fm = [x['N_measured'] for x in rows if x['k'] == q['k'] and x['N_measured'] is not None]; xm = list(comp.get((q['versus'], q['k']), {}).values())
    if not fm or not xm: rank.append(dict(q, measured_sign=None, result='NOT EVALUABLE')); continue
    ms = 'FFLONK lower' if statistics.fmean(fm) < statistics.fmean(xm) else 'FFLONK higher'
    rank.append(dict(q, measured_sign=ms, result='MATCH' if ms == q['predicted_sign'] else 'FALSIFIED'))
xover = {X: ('MATCH' if all(r['result'] == 'MATCH' for r in rank if r['versus'] == X and r['result'] in ('MATCH', 'FALSIFIED')) else 'FALSIFIED') for X in ('groth16', 'plonk')}
res = dict(label=('ENGINEERING TEST — ' if ENG else '') + 'V2-C2 scores (separate from C1 / H8)', tau=TAU, C2_PRIMARY=primary, C2_EXACT=exact,
           proofs=len(rows), comparable=len(comparable), max_abs_rel=max((abs(x['rel']) for x in comparable), default=None), residual_values=sorted({x['residual'] for x in comparable}),
           C2_RANK=rank, C2_XOVER=xover, per_proof=rows)
json.dump(res, open(os.path.join(OUT, 'C2-SCORES.json'), 'w'), indent=1); print(json.dumps({k: v for k, v in res.items() if k not in ('per_proof', 'C2_RANK')}, indent=1))
