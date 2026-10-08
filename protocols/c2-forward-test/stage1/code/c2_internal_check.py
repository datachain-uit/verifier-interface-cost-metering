#!/usr/bin/env python3
"""V2-C2 internal check (before any FFLONK artifact): apply the frozen C2 model with the calibrated C_env to the 190
registered Groth16 / PLONK ZKsync OS proofs NOT used for calibration (j1..j7 of the 9 context-tag cells; all 8 proofs of
c1_ctx_k06, c1_a4, c1_a8, c1_disc_k04). Descriptive for the calibration templates; not a C2 test (C2 tests FFLONK).
usage: c2_internal_check.py <check-structural.jsonl> <pilot records> <full records> <C2-CALIBRATION.json> <out.json>"""
import json, os, sys, collections
STR, PREC, FREC, CAL, OUT = sys.argv[1:6]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import c2_model as M
C_env = json.load(open(CAL))['C_env']; assert C_env is not None
reg = {}
for f in (PREC, FREC):
    for l in open(f):
        if not l.strip(): continue
        r = json.loads(l)
        if r.get('op') == 'verify_proof_direct' and r.get('role') == 'measurement' and r['env'] == 'zkos-v32' and r['regime'].get('npg') == 100 and not int(r['regime'].get('priority_fee') or 0):
            reg.setdefault(r['proof_id'], r['zkos']['computational_native'])
rows = []
for l in open(STR):
    s = json.loads(l); t = M.terms(s, C_env); n = reg[s['proof_id']]
    rows.append(dict(proof_id=s['proof_id'], backend=s['backend'], k=s['k'], N_registered=n, N_hat=t['N_hat'], residual=n - t['N_hat'], rel=(n - t['N_hat']) / t['N_hat'], unknown=t['unknown'], verified=s['returns_true']))
by = collections.Counter((r['backend'], r['residual']) for r in rows)
res = dict(label='V2-C2 internal check on non-calibration Groth16 / PLONK proofs (descriptive)', proofs=len(rows), C_env=C_env,
           residual_values_by_backend={f'{b}': sorted({r['residual'] for r in rows if r['backend'] == b}) for b in ('groth16', 'plonk')},
           max_abs_residual=max(abs(r['residual']) for r in rows), all_verified=all(r['verified'] for r in rows), any_unknown_term=any(r['unknown'] for r in rows), rows=rows)
json.dump(res, open(OUT, 'w'), indent=1); print(json.dumps({k: v for k, v in res.items() if k != 'rows'}, indent=1))
