#!/usr/bin/env python3
"""V2-C2 stage 2: numeric FFLONK predictions from the stage-2 structural records (no FFLONK cost is read anywhere).
usage: c2_predict.py <fflonk-structural.jsonl> <C2-CALIBRATION.json> <pilot records> <full records> <out dir>
Gates (recorded, never repaired): 32 records = 4 k values x 8 proofs, backend fflonk, circuits c1_ff_k01/k04/k16/k32;
every record status 1 and verifyProof true; no unknown model term (opcode without a source native cost, precompile other
than 0x6/0x7/0x8, pairing input not a multiple of 192). Outputs C2-STAGE2-PREDICTIONS.json / .csv; frozen (SHA256SUMS +
UTC) before any FFLONK measurement. C2_ENGINEERING_TEST=1 relaxes the target gates for pipeline tests on non-FFLONK data
(output labelled ENGINEERING TEST, never a C2 prediction)."""
import csv, json, os, sys, statistics
STR, CAL, PREC, FREC, OUT = sys.argv[1:6]; os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import c2_model as M
TAU = 0.000138                       # C1 13-tolerances.csv, key zkos-v32|groth16|native, tau_cond (06-criteria-and-falsifiers.md)
KS = [1, 4, 16, 32]; CIRC = {1: 'c1_ff_k01', 4: 'c1_ff_k04', 16: 'c1_ff_k16', 32: 'c1_ff_k32'}
ENG = os.environ.get('C2_ENGINEERING_TEST') == '1'
cal = json.load(open(CAL)); C_env = cal['C_env']; assert cal['single_value'] and cal['all_cross_checks_pass'] and C_env == 1669012
recs = [json.loads(l) for l in open(STR) if l.strip()]
gates = []
if not ENG:
    if sorted((r['k'], r['proof_id']) for r in recs) != sorted((k, f'{CIRC[k]}/fflonk/j{j}') for k in KS for j in range(8)): gates.append('target set is not exactly c1_ff_k01/k04/k16/k32 x j0..j7')
    if any(r['backend'] != 'fflonk' for r in recs): gates.append('non-FFLONK record')
reg = {}
for f in (PREC, FREC):
    for l in open(f):
        if not l.strip(): continue
        r = json.loads(l)
        if (r.get('op') == 'verify_proof_direct' and r.get('role') == 'measurement' and r['env'] == 'zkos-v32' and r['regime'].get('npg') == 100
                and not int(r['regime'].get('priority_fee') or 0) and r['backend'] in ('groth16', 'plonk') and r.get('relation') == 'ctx'):
            reg.setdefault((r['backend'], r['k']), {})[r['proof_id']] = r['zkos']['computational_native']
rows = []
for s in sorted(recs, key=lambda r: (r['k'], r['proof_id'])):
    t = M.terms(s, C_env); ok = s['status'] == 1 and s['returns_true'] and not t['unknown']
    if not ok: gates.append(f"{s['proof_id']}: status {s['status']}, returns_true {s['returns_true']}, unknown {t['unknown']}")
    rows.append(dict(proof_id=s['proof_id'], k=s['k'], backend=s['backend'], N_hat=t['N_hat'], lo=t['N_hat'] * (1 - TAU), hi=t['N_hat'] * (1 + TAU),
                     **{x: t[x] for x in ('OPS', 'PRE', 'KEC', 'COP', 'CDT', 'DEC', 'HEAP', 'CALL', 'C_env')}, pairs=t['pairs'], heap_events=s['heap_events'],
                     heap_final_bytes=s['heap_final_bytes'], calldata_bytes=s['calldata_bytes'], verifier_runtime_bytes=s['verifier_runtime_bytes'],
                     precompile_calls=len(s['precompile_calls']), ecmul=sum(c['addr'] == '0x7' for c in s['precompile_calls']), ecadd=sum(c['addr'] == '0x6' for c in s['precompile_calls']),
                     pairing_calls=sum(c['addr'] == '0x8' for c in s['precompile_calls']), structural_sha256=__import__('hashlib').sha256(json.dumps(s, sort_keys=True).encode()).hexdigest()))
cells, rank, xover = [], [], {}
for k in sorted({r['k'] for r in rows}):
    v = [r['N_hat'] for r in rows if r['k'] == k]; m = statistics.fmean(v); cells.append(dict(k=k, n=len(v), N_hat_mean=m, N_hat_min=min(v), N_hat_max=max(v)))
    for X in ('groth16', 'plonk'):
        meas = list(reg.get((X, k), {}).values())
        if not meas: rank.append(dict(k=k, versus=X, status='NO REGISTERED COMPARATOR')); continue
        mx = statistics.fmean(meas); h = (max(meas) - min(meas)) / 2; d = m - mx; band = TAU * m + h
        rank.append(dict(k=k, versus=X, N_hat_fflonk_mean=m, N_registered_mean=mx, predicted_difference=d, band=band,
                         predicted_sign=('FFLONK lower' if d < 0 else 'FFLONK higher') if abs(d) > band else 'INDETERMINATE'))
for X in ('groth16', 'plonk'):
    seq = [(r['k'], r['predicted_sign']) for r in rank if r['versus'] == X and 'predicted_sign' in r]
    det = [(k, s) for k, s in seq if s != 'INDETERMINATE']
    ch = [(a[0], b[0]) for a, b in zip(det, det[1:]) if a[1] != b[1]]
    xover[X] = dict(sign_sequence=seq, predicted_crossover=('none within the determinate k grid' if not ch else [f'k* in ({a}, {b})' for a, b in ch]))
out = dict(label='ENGINEERING TEST (not a C2 prediction)' if ENG else 'V2-C2 STAGE-2 NUMERIC PREDICTIONS (to be frozen before any FFLONK measurement)',
           model='source-augmented ZKsync OS native-cost model (extended transaction-level accounting), C2-SA', C_env=C_env, tau=TAU,
           residual_definition='r = N_measured - N_hat (native); e = r / N_hat', gates_passed=not gates, gate_failures=gates, per_proof=rows, cells=cells, ranking=rank, crossover=xover)
json.dump(out, open(os.path.join(OUT, 'C2-STAGE2-PREDICTIONS.json'), 'w'), indent=1)
w = csv.DictWriter(open(os.path.join(OUT, 'C2-STAGE2-PREDICTIONS.csv'), 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(json.dumps({k: v for k, v in out.items() if k not in ('per_proof',)}, indent=1)[:3000])
sys.exit(0 if not gates else 2)
