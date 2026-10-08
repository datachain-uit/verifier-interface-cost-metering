#!/usr/bin/env python3
"""V2-C1 frozen scoring procedure (pre-registered analysis code; see 19-scoring-plan.md).

usage: score_c1.py <predictions_dir> <out_dir> <evidence.jsonl> [more.jsonl ...]
Reads registered evidence records (schema v2-c1-evidence/1, 18-evidence-schema.md), never P0 data.
Sections: AC accounting checks | CELL summaries | P a-priori prediction scoring | R registered-calibration procedure |
ZC ZKsync OS trace-conditional test | SG signs | XO crossovers | NPG intervention | SEM semantic invariance | V verdicts.
No record is dropped: records flagged by a deviation are scored and also reported separately (20-deviations-policy.md).
"""
import json, sys, os, csv, math, collections, statistics
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'model'))
from c1_model import *
import zkos_native_trace_model as ZT
VM = os.environ.get('C1_TEST_VM', '0.4.0')   # registered scoring uses 0.4.0; C1_TEST_VM exists only for the code test on P0 v31 data
PRED, OUT, FILES = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(OUT, exist_ok=True)
rd = lambda name: list(csv.DictReader(open(os.path.join(PRED, name))))
TOL = json.load(open(os.path.join(PRED, 'fitted_parameters_and_tolerances.json')))['tolerances']
EPS = {r['env']: float(r['epsilon']) for r in rd('equality_bands.csv')}
PC = {r['cell']: r for r in rd('predictions_cells.csv')}
V31 = {b: TOL[f'zkos-v32|{b}|native']['tau_cond'] for b in ('groth16', 'plonk', 'fflonk')}   # tau_cond (ZC), frozen in 13-criteria.md
recs = [json.loads(l) for f in FILES for l in open(f) if l.strip()]
report = collections.OrderedDict(); W = lambda name, rows: rows and (lambda f: (lambda w: (w.writeheader(), w.writerows(rows)))(csv.DictWriter(f, fieldnames=list(rows[0].keys()))))(open(os.path.join(OUT, name), 'w', newline=''))
def envlabel(r):
    if r['env'] != 'zkos-v32': return r['env']
    g = r['regime']; return f"zkos-v32@npg{g['npg']}" + (f"+prio{g['priority_fee']}" if int(g.get('priority_fee') or 0) else '')
def y(r, metric):
    if metric == 'N': return r['zkos']['computational_native']
    if r['env'].startswith('eravm'): return r['eravm']['computational_gas']
    return r['gas_used']
def ync(r):  # EVM calldata-normalised execution gas
    nz = 68 if r['env'] == 'evm-petersburg' else 16
    return r['gas_used'] - nz * (r['calldata_bytes'] - r['calldata_zero']) - 4 * r['calldata_zero']
meas = [r for r in recs if r['role'] == 'measurement' and r['op'] in ('verify_proof_direct', 'verify_credential')]
M = 'dir'; mm = {'verify_proof_direct': 'dir', 'verify_credential': 'app'}
# ---------------- AC: accounting and structural checks ----------------
ac = []; TEMPLATE = {'groth16': lambda k: (k, k, 4), 'plonk': lambda k: (18, 18, 2), 'fflonk': lambda k: (5, 7, 2)}
for r in recs:
    if r['role'] != 'measurement' or r['op'] != 'verify_proof_direct': continue
    if r['env'].startswith('evm') and r.get('evm_trace'):
        t = r['evm_trace']; ok = t['gas'] == r['gas_used']
        pc = t['precompiles']; cnt = (pc.get('0x7', {}).get('n', 0), pc.get('0x6', {}).get('n', 0))
        exp = TEMPLATE[r['backend']](r['k']); ok2 = cnt == exp[:2] and pc.get('0x8', {}).get('n', 0) == 1
        ac.append(dict(check='AC-EVM-trace-closure', proof=r['proof_id'], env=r['env'], ok=ok)); ac.append(dict(check='AC-STRUCT-EVM-precompile-counts', proof=r['proof_id'], env=r['env'], ok=ok2))
        rounds = sum(math.ceil((n + 1) / 136) for n in t.get('keccak_sizes', []))
        ac.append(dict(check='AC-STRUCT-EVM-transcript-rounds', proof=r['proof_id'], env=r['env'], ok=rounds == rho(r['backend'], r['k'])))
    if r['env'].startswith('eravm') and r.get('eravm', {}).get('frames'):
        fr = r['eravm']['frames']; tot = fr['outside'] + fr['self'] + sum(v[1] for v in fr['precompiles'].values())
        exp = TEMPLATE[r['backend']](r['k'])
        ac.append(dict(check='AC-ERAVM-frame-closure', proof=r['proof_id'], env=r['env'], ok=tot == r['eravm']['computational_gas']))
        ac.append(dict(check='AC-STRUCT-ERAVM-precompile-counts', proof=r['proof_id'], env=r['env'], ok=(fr['precompiles'].get('0007', [0])[0], fr['precompiles'].get('0006', [0])[0], fr['precompiles'].get('0008', [0])[0]) == (exp[0], exp[1], 1)))
edr = {(r['proof_id'], r['op']): r['gas_used'] for r in meas if r['env'] == 'evm-osaka'}
for r in meas:
    if r['env'] != 'zkos-v32': continue
    g = r['regime']; price = int(str(g['native_price']), 0); egp = int(str(r['zkos']['effective_gas_price']), 0)
    nb = r['zkos']['native_used'] * price // egp; ge = edr.get((r['proof_id'], r['op']))
    if ge is None: ac.append(dict(check='AC-ZK-gas-rule', proof=r['proof_id'], env=envlabel(r), ok='NO-EDR-PAIR')); continue
    exp = max(ge, nb); ac.append(dict(check='AC-ZK-gas-rule', proof=r['proof_id'], env=envlabel(r), ok=abs(r['gas_used'] - exp) <= 1))
for r in recs:
    if r['role'] in ('control', 'replay'):
        c = r.get('control') or 'replay'
        if c in ('valid', 'cross_regime_identity'): ok = r.get('returned') == 'true'
        elif c == 'replay': ok = r['status'] == 1
        elif c == 'unknown_root_tx': ok = r['status'] == 0
        else: ok = r.get('returned') != 'true'
        ac.append(dict(check='AC-CTRL-' + ('perturb_pub' if c.startswith('perturb_pub') else c), proof=r.get('proof_id'), env=envlabel(r), ok=ok))
W('AC_checks.csv', ac); report['AC'] = dict(total=len(ac), failed=sum(1 for a in ac if a['ok'] is not True))
# ---------------- CELL summaries ----------------
cells = collections.defaultdict(list)
for r in meas:
    m = mm[r['op']]; cells[(envlabel(r), r['backend'], r['circuit'], 'Y_' + m)].append(y(r, 'Y'))
    if r['env'].startswith('evm'): cells[(envlabel(r), r['backend'], r['circuit'], 'Ync_' + m)].append(ync(r))
    if r['env'] == 'zkos-v32' and m == 'dir': cells[(envlabel(r), r['backend'], r['circuit'], 'N_dir')].append(y(r, 'N'))
K = {r['circuit']: r['k'] for r in meas}; REL = {r['circuit']: r.get('relation', 'ctx') for r in meas}
summ = [dict(env=e, backend=b, circuit=c, k=K[c], metric=m, n=len(v), mean=statistics.mean(v), min=min(v), max=max(v), half_range_rel=(max(v) - min(v)) / 2 / statistics.mean(v)) for (e, b, c, m), v in sorted(cells.items())]
W('CELL_summary.csv', summ); C = {(s['env'], s['backend'], s['circuit'], s['metric']): s for s in summ}
# ---------------- P: a-priori numeric predictions ----------------
ps = []
for cid, p in PC.items():
    env, b, circ, metric = cid.split('|'); envk = 'zkos-v32@npg100' if env.startswith('zkos-v32') else env
    metr = {'Y_dir': 'Y_dir', 'Y_app': 'Y_app', 'N_dir': 'N_dir', 'G_dir': 'Y_dir'}[metric]
    s = C.get((envk, b, circ, metr))
    if not s: ps.append(dict(cell=cid, role=p['role'], status='MISSING')); continue
    inb = int(p['lo']) <= s['mean'] <= int(p['hi'])
    ps.append(dict(cell=cid, role=p['role'], pred=p['pred'], lo=p['lo'], hi=p['hi'], measured_mean=round(s['mean'], 2), err_rel=round((s['mean'] - float(p['pred'])) / float(p['pred']), 6),
                   status=('TRANSFER-CHECK ' if p['role'].startswith('CALIBRATION') else 'DESCRIPTIVE ' if p['role'].startswith('LIMIT') else '') + ('PASS' if inb else 'FAIL')))
W('P_scoring.csv', ps)
# ---------------- R: registered-calibration procedure ----------------
rs = []; Rpar = {}
CTX = {1: 'c1_k01', 2: 'c1_ctx_k02', 4: 'c1_ctx_k04', 6: 'c1_ctx_k06', 8: 'c1_ctx_k08', 12: 'c1_ctx_k12', 16: 'c1_ctx_k16', 24: 'c1_ctx_k24', 32: 'c1_ctx_k32', 64: 'c1_ctx_k64'}
for env in ('evm-osaka', 'eravm-29', 'evm-petersburg'):
    for b in ('groth16', 'plonk'):
        for m in ('dir', 'app'):
            mk = ('Ync_' if env.startswith('evm') else 'Y_') + m; c1, c4 = C.get((env, b, CTX[1], mk)), C.get((env, b, CTX[4], mk))
            if not (c1 and c4): continue
            A, B = fit(c1['mean'], c4['mean'], env, b); Rpar[(env, b, m)] = (A, B); t = TOL[f'{env}|{b}|{m}']; tau = t['tau_noise'] + t['tau_struct']
            for k, circ in CTX.items():
                s = C.get((env, b, circ, mk))
                if not s or k in CAL_K: continue
                p = kmodel(A, B, env, b, k); e = (s['mean'] - p) / p
                rs.append(dict(env=env, backend=b, metric=mk, k=k, pred=round(p), measured=round(s['mean'], 2), err_rel=round(e, 6), tau=round(tau, 6), status=('DESCRIPTIVE ' if k in LIMIT else '') + ('PASS' if abs(e) <= tau else 'FAIL'), heldout=('seen-in-P0' if k in SEEN_NOT_FITTED else 'limit' if k in LIMIT else 'strictly-unseen')))
# EraVM v27 transfer with registered frames at k = 1
fr = {}
for r in meas:
    if r['env'].startswith('eravm') and r['k'] == 1 and r['op'] == 'verify_proof_direct' and r['backend'] == 'groth16' and r.get('eravm', {}).get('frames'):
        P_ = r['eravm']['frames']['precompiles']; fr.setdefault(r['env'], []).append(P_.get('0006', [1, 0])[1] / max(P_.get('0006', [1])[0], 1) + P_.get('0007', [1, 0])[1] / max(P_.get('0007', [1])[0], 1))
for b in ('groth16', 'plonk'):
    for m in ('dir', 'app'):
        c1 = C.get(('eravm-27', b, CTX[1], 'Y_' + m))
        if not (c1 and ('eravm-29', b, m) in Rpar and 'eravm-27' in fr and 'eravm-29' in fr): continue
        B = Rpar[('eravm-29', b, m)][1] + (statistics.mean(fr['eravm-27']) - statistics.mean(fr['eravm-29'])) * (b == 'groth16'); A = c1['mean']
        t = TOL[f'eravm-27|{b}|{m}']; tau = t['tau_noise'] + t['tau_struct']; Rpar[('eravm-27', b, m)] = (A, B)
        for k in (4, 6, 8, 16):
            s = C.get(('eravm-27', b, CTX[k], 'Y_' + m))
            if not s: continue
            p = kmodel(A, B, 'eravm-27', b, k); e = (s['mean'] - p) / p
            rs.append(dict(env='eravm-27', backend=b, metric='Y_' + m, k=k, pred=round(p), measured=round(s['mean'], 2), err_rel=round(e, 6), tau=round(tau, 6), status='PASS' if abs(e) <= tau else 'FAIL', heldout='held-out-regime'))
W('R_scoring.csv', rs)
# ---------------- ZC: ZKsync OS trace-conditional (Level 4) ----------------
zc = []; trace = {r['proof_id']: r['evm_trace'] for r in meas if r['env'] == 'evm-osaka' and r['op'] == 'verify_proof_direct' and r.get('evm_trace')}
zk = [r for r in meas if r['env'] == 'zkos-v32' and r['op'] == 'verify_proof_direct' and envlabel(r) == 'zkos-v32@npg100']
cal = []
for b in ('groth16', 'plonk'):
    res = [r['zkos']['computational_native'] - ZT.components(trace[r['proof_id']], b, VM)['sum'] for r in zk if r['backend'] == b and r['circuit'] == CTX[1] and r['proof_id'] in trace]
    if res: cal.append((b, 1, 0.0, statistics.mean(res)))
if len(cal) == 2:
    base, cpc = ZT.calibrate(cal); report['ZC_constants'] = dict(base=base, per_call=cpc)
    for r in zk:
        if r['circuit'] == CTX[1] and r['backend'] in ('groth16', 'plonk') or r['proof_id'] not in trace: continue
        comp = ZT.components(trace[r['proof_id']], r['backend'], VM); p = ZT.predict(comp, r['backend'], r['k'], base, cpc); m_ = r['zkos']['computational_native']; e = (m_ - p) / p
        zc.append(dict(proof=r['proof_id'], backend=r['backend'], k=r['k'], relation=REL.get(r['circuit']), pred=round(p), measured=m_, err_rel=round(e, 6), tau_cond=V31[r['backend']], status=('DESCRIPTIVE ' if r['k'] in LIMIT else '') + ('PASS' if abs(e) <= V31[r['backend']] and not comp['unknown'] else 'FAIL'), unknown_ops=';'.join(comp['unknown'])))
W('ZC_scoring.csv', zc)
# ---------------- SG / XO: signs and crossovers (measured means, Y_dir; ZKsync OS native and gas at npg 100) ----------------
sg = []; xo = []; PS = {(r['env'], r['metric'], int(r['k'])): r for r in rd('predictions_signs.csv')}; PX = {(r['env'], r['metric']): r for r in rd('crossover_intervals.csv')}
for env, mk, pm in [('evm-osaka', 'Y_dir', 'dir'), ('eravm-29', 'Y_dir', 'dir'), ('eravm-27', 'Y_dir', 'dir'), ('evm-petersburg', 'Y_dir', 'dir'), ('zkos-v32@npg100', 'N_dir', 'native'), ('zkos-v32@npg100', 'Y_dir', 'dir')]:
    penv = 'zkos-v32' if (env.startswith('zkos') and mk == 'N_dir') else env; eps = EPS['zkos-v32' if env.startswith('zkos') else env]
    ks = [k for k, c in CTX.items() if C.get((env, 'groth16', c, mk)) and C.get((env, 'plonk', c, mk))]
    d = []
    for k in ks:
        g, p = C[(env, 'groth16', CTX[k], mk)], C[(env, 'plonk', CTX[k], mk)]; r_ = p['mean'] / g['mean']
        cls = 'IN-BAND' if abs(r_ - 1) <= eps else ('PLONK_COSTLIER' if r_ > 1 else 'PLONK_CHEAPER')
        sep = 'separated' if (p['min'] > g['max'] or p['max'] < g['min']) else 'overlapping'
        pr = PS.get((penv, pm, k)); pred = pr['predicted_sign'] if pr else 'n/a'
        ratio_ok = (float(pr['ratio_lo']) <= r_ <= float(pr['ratio_hi'])) if pr else None
        verdict = 'NOT-SCORED' if pred in ('INDETERMINATE', 'n/a') else ('MATCH' if cls == pred else ('FALSIFIED' if cls != 'IN-BAND' else 'IN-BAND-MISS'))
        sg.append(dict(env=env, metric=mk, k=k, ratio=round(r_, 6), measured_class=cls, all_vs_all=sep, predicted_sign=pred, sign_verdict=verdict, ratio_in_interval=ratio_ok)); d.append(p['mean'] - g['mean'])
    if len(ks) >= 2:
        kx = crossing(ks, d); inb = [s['k'] for s in sg if s['env'] == env and s['metric'] == mk and s['measured_class'] == 'IN-BAND']
        lo_m = min([kx] + inb) if kx is not None else (min(inb) if inb else None); hi_m = max([kx] + inb) if kx is not None else (max(inb) if inb else None)
        px = PX.get((penv, pm)); ok = None
        if px:
            def num(v, side): return 1.0 if v == '<=1' else (1e9 if str(v).startswith('>') else float(v))
            plo, phi = num(px['kstar_lo'], 'lo'), num(px['kstar_hi'], 'hi')
            if kx is None and not inb: ok = ('PASS' if (d[0] < 0 and plo <= 1) or (d[0] > 0 and phi > ks[-1]) else 'FAIL')
            else: ok = 'PASS' if (lo_m <= phi and hi_m >= plo) else 'FAIL'
        xo.append(dict(env=env, metric=mk, kstar_measured=None if kx is None else round(kx, 3), measured_interval=f'[{lo_m},{hi_m}]', predicted=(f"{px['kstar_point']} [{px['kstar_lo']},{px['kstar_hi']}]" if px else 'n/a'), verdict=ok))
mono = []
for env in sorted(set(x['env'] for x in sg)):
    for mk in sorted(set(x['metric'] for x in sg if x['env'] == env)):
        S_ = sorted([x for x in sg if x['env'] == env and x['metric'] == mk and x['k'] <= 32], key=lambda x: x['k']); eps = EPS['zkos-v32' if env.startswith('zkos') else env]
        viol = [(a['k'], b_['k']) for i, a in enumerate(S_) for b_ in S_[i + 1:] if b_['ratio'] > a['ratio'] + eps]
        mono.append(dict(env=env, metric=mk, n_k=len(S_), violations=';'.join(f'{a}->{b_}' for a, b_ in viol), verdict='PASS' if not viol else 'FAIL'))
W('SG_signs.csv', sg); W('XO_crossovers.csv', xo); W('SG_monotonicity.csv', mono)
# ---------------- NPG intervention ----------------
npg = []; PN = {(int(r['k']), int(r['npg']), r['backend']): r for r in rd('zkos_npg_predictions.csv')}
for (e, b, c, mk), s in C.items():
    if not e.startswith('zkos-v32@npg') or '+prio' in e or mk != 'Y_dir': continue
    lv = int(e.split('npg')[1]); k = K[c]; pr = PN.get((k, lv, b))
    if not pr: continue
    nat = C.get((e, b, c, 'N_dir')); evm = C.get(('evm-osaka', b, c, 'Y_dir'))
    meter = 'NATIVE' if nat and abs(s['mean'] - nat['mean'] / lv) <= 1 and (not evm or s['mean'] > evm['mean']) else ('EVM_GAS' if evm and abs(s['mean'] - evm['mean']) <= 1 else 'UNRESOLVED')
    ok = pr['binding_meter'] == 'INDETERMINATE' or pr['binding_meter'] == meter
    npg.append(dict(k=k, npg=lv, backend=b, measured_gas=round(s['mean'], 2), measured_meter=meter, predicted_meter=pr['binding_meter'], meter_verdict='PASS' if ok else 'FAIL', gas_in_interval=int(pr['G_lo']) <= s['mean'] <= int(pr['G_hi'])))
rk = []
for (k, lv, b), pr in PN.items():
    if b != 'ratio': continue
    e_ = f'zkos-v32@npg{lv}'; c = CTX.get(k); G_, P_ = C.get((e_, 'groth16', c, 'Y_dir')), C.get((e_, 'plonk', c, 'Y_dir'))
    if not (G_ and P_): continue
    r_ = P_['mean'] / G_['mean']; eps = EPS['zkos-v32']
    cls = 'IN-BAND' if abs(r_ - 1) <= eps else ('PLONK_COSTLIER' if r_ > 1 else 'PLONK_CHEAPER'); pred = pr['binding_meter']
    rk.append(dict(k=k, npg=lv, ratio=round(r_, 6), measured_class=cls, predicted_class=pred, ratio_in_interval=float(pr['G_lo']) <= r_ <= float(pr['G_hi']),
                   verdict='NOT-SCORED' if pred == 'INDETERMINATE' else ('MATCH' if cls == pred else ('FALSIFIED' if cls != 'IN-BAND' else 'IN-BAND-MISS'))))
W('NPG_scoring.csv', npg); W('NPG_ranking.csv', rk)
# ---------------- SEM: semantic invariance ----------------
sem = []; ANCH = {'c1_a4': 4, 'c1_a8': 8, 'c1_disc_k04': 4}
for (e, b, c, mk), s in C.items():
    if c not in ANCH or mk not in ('Y_dir', 'Ync_dir', 'N_dir') or (e.startswith('evm') and mk == 'Y_dir'): continue
    ref = C.get((e, b, CTX[ANCH[c]], mk))
    if not ref: continue
    dlt = (s['mean'] - ref['mean']) / ref['mean']; eps = EPS['zkos-v32' if e.startswith('zkos') else e]
    sem.append(dict(env=e, backend=b, anchor=c, k=ANCH[c], metric=mk, rel_diff=round(dlt, 6), epsilon=eps, verdict='PASS' if abs(dlt) <= eps else 'FAIL'))
W('SEM_scoring.csv', sem)
# ---------------- summary ----------------
cnt = lambda rows, key='status': dict(collections.Counter(r.get(key) for r in rows))
report.update(P=cnt(ps), R=cnt(rs), ZC=cnt(zc), SG=cnt(sg, 'sign_verdict'), XO=cnt(xo, 'verdict'), NPG=cnt(npg, 'meter_verdict'), NPG_rank=cnt(rk, 'verdict'), MONO=cnt(mono, 'verdict'), SEM=cnt(sem, 'verdict'), n_records=len(recs), n_measurement_records=len(meas))
json.dump(report, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1, default=str); print(json.dumps(report, indent=1, default=str))
