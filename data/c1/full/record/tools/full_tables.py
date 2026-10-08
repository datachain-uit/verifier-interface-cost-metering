#!/usr/bin/env python3
"""V2-M5 report tables: renders the FROZEN scorer outputs (pilot + FULL registered evidence). No verdict is recomputed;
every PASS/FAIL/MATCH below is copied from the scorer's CSV files. usage: full_tables.py <scoring_dir> <predictions_dir> <out_md> <out_csv_dir>"""
import csv, json, os, sys, collections
S, PD, OUT, OC = sys.argv[1:5]; os.makedirs(OC, exist_ok=True)
rd = lambda d, n: list(csv.DictReader(open(os.path.join(d, n)))) if os.path.exists(os.path.join(d, n)) else []
CTX = {1: 'c1_k01', 2: 'c1_ctx_k02', 4: 'c1_ctx_k04', 6: 'c1_ctx_k06', 8: 'c1_ctx_k08', 12: 'c1_ctx_k12', 16: 'c1_ctx_k16', 24: 'c1_ctx_k24', 32: 'c1_ctx_k32', 64: 'c1_ctx_k64'}
UNSEEN = (6, 8, 12, 24); L = []; w = L.append
def t(rows, cols, hdr=None):
    w('| ' + ' | '.join(hdr or cols) + ' |'); w('|' + '---|' * len(cols))
    for r in rows: w('| ' + ' | '.join(str(r.get(c, '')) for c in cols) + ' |')
    w('')
def wcsv(name, rows):
    if rows: f = open(os.path.join(OC, name), 'w', newline=''); x = csv.DictWriter(f, fieldnames=list(rows[0].keys())); x.writeheader(); x.writerows(rows)
fmt = lambda v: f"{float(v):,.0f}"; pct = lambda v: f"{100 * float(v):+.4f}"
summ = json.load(open(os.path.join(S, 'summary.json')))
CS = {(r['env'], r['backend'], r['circuit'], r['metric']): r for r in rd(S, 'CELL_summary.csv')}
PS = {r['cell']: r for r in rd(S, 'P_scoring.csv')}; PC = {r['cell']: r for r in rd(PD, 'predictions_cells.csv')}
RS = {(r['env'], r['backend'], r['metric'], int(r['k'])): r for r in rd(S, 'R_scoring.csv')}
SG = {(r['env'], r['metric'], int(r['k'])): r for r in rd(S, 'SG_signs.csv')}
ZC = collections.defaultdict(list)
for r in rd(S, 'ZC_scoring.csv'): ZC[(r['backend'], int(r['k']), r['relation'])].append(r)
# ---------- strict-unseen (EVM Osaka, EraVM v29): P and R side by side ----------
su = []
for env in ('evm-osaka', 'eravm-29'):
    for b in ('groth16', 'plonk'):
        for k in UNSEEN:
            for m in ('dir', 'app'):
                cid = f"{env}|{b}|{CTX[k]}|Y_{m}"; p = PS.get(cid, {}); pc = PC.get(cid, {}); cs = CS.get((env, b, CTX[k], 'Y_' + m))
                rk = ('Ync_' if env.startswith('evm') else 'Y_') + m; rr = RS.get((env, b, rk, k), {}); sg = SG.get((env, 'Y_dir', k), {})
                row = dict(env=env, backend=b, k=k, metric='Y_' + m, P_pred=pc.get('pred'), P_lo=pc.get('lo'), P_hi=pc.get('hi'), P_tau_rel=pc.get('tau_rel'),
                           observed_mean=cs and round(float(cs['mean']), 2), proof_min=cs and int(float(cs['min'])), proof_max=cs and int(float(cs['max'])), n=cs and cs['n'],
                           P_abs_err=cs and pc and round(float(cs['mean']) - float(pc['pred']), 2), P_rel_err=p.get('err_rel'), P_verdict=p.get('status', 'MISSING'),
                           R_metric=rk, R_pred=rr.get('pred'), R_measured=rr.get('measured'), R_abs_err=rr and round(float(rr['measured']) - float(rr['pred']), 2), R_rel_err=rr.get('err_rel'), R_tau=rr.get('tau'), R_verdict=rr.get('status', 'MISSING'),
                           rank_pred=sg.get('predicted_sign') if m == 'dir' else '', rank_measured=sg.get('measured_class') if m == 'dir' else '', rank_verdict=(sg.get('sign_verdict') if m == 'dir' else ''))
                su.append(row)
wcsv('strict-unseen-EVM-EraVM.csv', su)
w('### S1. Strictly unseen k ∈ {6, 8, 12, 24} — EVM Osaka and EraVM v29 (prediction set P and registered-calibration procedure R side by side)\n')
w('P: frozen a-priori prediction and interval (PASS iff the 8-proof mean lies in [lo, hi]). R: A, B refitted on registered k = 1, 4; PASS iff |e| ≤ τ (EVM on calldata-normalised gas). Errors e = (measured − predicted) / predicted. Ranking (direct call only): frozen predicted class vs measured class at the same k.\n')
t([dict(r, P_pred=fmt(r['P_pred']), P_int=f"[{fmt(r['P_lo'])}, {fmt(r['P_hi'])}]", P_tau=f"{100 * float(r['P_tau_rel']):.3f} %", obs=f"{r['observed_mean']:,.1f}", rng=f"{r['proof_min']:,} – {r['proof_max']:,}",
       Pabs=f"{r['P_abs_err']:+,.1f}", Prel=pct(r['P_rel_err']), Rp=fmt(r['R_pred']) if r['R_pred'] else '', Rabs=(f"{r['R_abs_err']:+,.1f}" if r['R_abs_err'] != {} and r['R_abs_err'] is not None else ''), Rrel=pct(r['R_rel_err']) if r['R_rel_err'] else '', Rtau=(f"{100 * float(r['R_tau']):.3f} %" if r['R_tau'] else '')) for r in su if r['observed_mean']],
  ['env', 'backend', 'k', 'metric', 'P_pred', 'P_int', 'P_tau', 'obs', 'rng', 'Pabs', 'Prel', 'P_verdict', 'R_metric', 'Rp', 'Rabs', 'Rrel', 'Rtau', 'R_verdict', 'rank_pred', 'rank_measured', 'rank_verdict'],
  ['regime', 'backend', 'k', 'metric', 'P pred', 'P interval', 'P ±', 'observed mean', 'proof range', 'P abs err', 'P rel err %', 'P verdict', 'R metric', 'R pred', 'R abs err', 'R rel err %', 'R τ', 'R verdict', 'predicted rank', 'measured rank', 'rank verdict'])
# ---------- strict-unseen ZKsync OS ----------
zs = []
for b in ('groth16', 'plonk'):
    for k in UNSEEN:
        cid = f"zkos-v32|{b}|{CTX[k]}|N_dir"; p = PS.get(cid, {}); pc = PC.get(cid, {}); cs = CS.get(('zkos-v32@npg100', b, CTX[k], 'N_dir'))
        gid = f"zkos-v32@npg100|{b}|{CTX[k]}|G_dir"; pg = PS.get(gid, {}); pgc = PC.get(gid, {}); cg = CS.get(('zkos-v32@npg100', b, CTX[k], 'Y_dir'))
        z = ZC.get((b, k, 'ctx'), []); sn = SG.get(('zkos-v32@npg100', 'N_dir', k), {}); sgg = SG.get(('zkos-v32@npg100', 'Y_dir', k), {})
        zs.append(dict(backend=b, k=k, N_pred=pc.get('pred'), N_lo=pc.get('lo'), N_hi=pc.get('hi'), N_tau_rel=pc.get('tau_rel'), N_mean=cs and round(float(cs['mean']), 1), N_min=cs and int(float(cs['min'])), N_max=cs and int(float(cs['max'])),
                       N_abs_err=cs and pc and round(float(cs['mean']) - float(pc['pred']), 1), N_rel_err=p.get('err_rel'), N_P_verdict=p.get('status', 'MISSING'),
                       ZC_n=len(z), ZC_pass=sum(x['status'] == 'PASS' for x in z), ZC_max_abs_err=(max(abs(float(x['err_rel'])) for x in z) if z else None), ZC_mean_err=(sum(float(x['err_rel']) for x in z) / len(z) if z else None), tau_cond=(z[0]['tau_cond'] if z else None),
                       ZC_verdict=('PASS' if z and all(x['status'] == 'PASS' for x in z) else ('FAIL' if z else 'MISSING')),
                       G_pred=pgc.get('pred'), G_lo=pgc.get('lo'), G_hi=pgc.get('hi'), G_mean=cg and round(float(cg['mean']), 1), G_min=cg and int(float(cg['min'])), G_max=cg and int(float(cg['max'])), G_rel_err=pg.get('err_rel'), G_P_verdict=pg.get('status', 'MISSING'),
                       rank_pred_native=sn.get('predicted_sign'), rank_meas_native=sn.get('measured_class'), rank_verdict_native=sn.get('sign_verdict'), rank_pred_gas=sgg.get('predicted_sign'), rank_meas_gas=sgg.get('measured_class'), rank_verdict_gas=sgg.get('sign_verdict')))
wcsv('strict-unseen-ZKsyncOS.csv', zs)
w('### S2. Strictly unseen k ∈ {6, 8, 12, 24} — ZKsync OS v32.0 @ npg 100 (computational native N, final gas G; conditional Level-4 test ZC per proof)\n')
t([dict(r, Np=fmt(r['N_pred']), Ni=f"[{fmt(r['N_lo'])}, {fmt(r['N_hi'])}]", Nt=f"{100 * float(r['N_tau_rel']):.3f} %", Nm=f"{r['N_mean']:,.1f}", Nr=f"{r['N_min']:,} – {r['N_max']:,}", Na=f"{r['N_abs_err']:+,.1f}", Nrel=pct(r['N_rel_err']),
       zc=f"{r['ZC_pass']} / {r['ZC_n']}", zcm=f"{100 * r['ZC_max_abs_err']:.4f}", zce=f"{100 * r['ZC_mean_err']:+.4f}", tc=f"{100 * float(r['tau_cond']):.4f}",
       Gp=f"{fmt(r['G_pred'])} [{fmt(r['G_lo'])}, {fmt(r['G_hi'])}]", Gm=f"{r['G_mean']:,.1f}", Gr=f"{r['G_min']:,} – {r['G_max']:,}", Grel=pct(r['G_rel_err'])) for r in zs if r['N_mean']],
  ['backend', 'k', 'Np', 'Ni', 'Nt', 'Nm', 'Nr', 'Na', 'Nrel', 'N_P_verdict', 'zc', 'zce', 'zcm', 'tc', 'ZC_verdict', 'Gp', 'Gm', 'Gr', 'Grel', 'G_P_verdict', 'rank_pred_native', 'rank_meas_native', 'rank_verdict_native', 'rank_verdict_gas'],
  ['backend', 'k', 'N pred', 'N interval', 'N ±', 'N observed mean', 'N proof range', 'N abs err', 'N rel err %', 'P verdict (N)', 'ZC pass', 'ZC mean err %', 'ZC max abs err %', 'τ_cond %', 'ZC verdict', 'G pred [interval]', 'G observed', 'G proof range', 'G rel err %', 'P verdict (G)', 'predicted rank', 'measured rank (N)', 'rank verdict (N)', 'rank verdict (G)'])
# ---------- all held-out R rows by class ----------
R = rd(S, 'R_scoring.csv')
for cls, title in (('seen-in-P0', 'R1. Held-out k seen in P0 (k ∈ {2, 16, 32}; weak test)'), ('limit', 'R2. Limit check k = 64 (descriptive)'), ('held-out-regime', 'R3. EraVM v27 transfer (H7)')):
    rows = [dict(r, err=pct(r['err_rel']), tau_=f"{100 * float(r['tau']):.3f}") for r in R if r['heldout'] == cls]
    w(f'### {title}\n'); t(rows, ['env', 'backend', 'metric', 'k', 'pred', 'measured', 'err', 'tau_', 'status'], ['regime', 'backend', 'metric', 'k', 'R pred', 'measured', 'err %', 'τ %', 'verdict'])
# ---------- P summary by role ----------
pr = collections.Counter((PC[c]['role'], s['status']) for c, s in PS.items() if c in PC)
w('### P0. Prediction set P — verdict counts by frozen role (all registered evidence)\n'); t([dict(role=k[0], status=k[1], n=v) for k, v in sorted(pr.items())], ['role', 'status', 'n'])
pf = [dict(cell=c, role=PC[c]['role'], pred=s.get('pred'), lo=s.get('lo'), hi=s.get('hi'), measured=s.get('measured_mean'), err=pct(s['err_rel'])) for c, s in PS.items() if 'FAIL' in s.get('status', '') and c in PC]
w('### P0-F. Every P cell outside its interval\n'); t(pf, ['cell', 'role', 'pred', 'lo', 'hi', 'measured', 'err'], ['cell', 'role', 'pred', 'lo', 'hi', 'measured mean', 'err %'])
# ---------- signs, monotonicity, crossovers ----------
w('### E1. Signs and ratio intervals (all k, all regimes)\n'); t(rd(S, 'SG_signs.csv'), ['env', 'metric', 'k', 'ratio', 'measured_class', 'all_vs_all', 'predicted_sign', 'sign_verdict', 'ratio_in_interval'])
w('### E2. Monotonicity of the PLONK / Groth16 ratio\n'); t(rd(S, 'SG_monotonicity.csv'), ['env', 'metric', 'n_k', 'violations', 'verdict'])
w('### E3. Crossovers\n'); t(rd(S, 'XO_crossovers.csv'), ['env', 'metric', 'kstar_measured', 'measured_interval', 'predicted', 'verdict'])
# ---------- ZC all ----------
w('### Z1. ZKsync OS conditional model per (backend, k, relation) — all held-out proofs\n')
w(f"Constants (scorer, registered k = 1): {json.dumps(summ.get('ZC_constants'))}\n")
t([dict(backend=b, k=k, relation=rel, n=len(v), passed=sum(x['status'].endswith('PASS') for x in v), failed=sum(not x['status'].endswith('PASS') for x in v), mean_err=f"{100 * sum(float(x['err_rel']) for x in v) / len(v):+.4f}",
        min_err=f"{100 * min(float(x['err_rel']) for x in v):+.4f}", max_err=f"{100 * max(float(x['err_rel']) for x in v):+.4f}", tau=f"{100 * float(v[0]['tau_cond']):.4f}", unknown=';'.join(sorted({x['unknown_ops'] for x in v if x['unknown_ops']})) or '—') for (b, k, rel), v in sorted(ZC.items())],
  ['backend', 'k', 'relation', 'n', 'passed', 'failed', 'mean_err', 'min_err', 'max_err', 'tau', 'unknown'], ['backend', 'k', 'relation', 'n', 'pass', 'fail', 'mean err %', 'min err %', 'max err %', 'τ_cond %', 'unpriced opcodes'])
# ---------- NPG ----------
pn = {(int(r['k']), int(r['npg']), r['backend']): r for r in rd(PD, 'zkos_npg_predictions.csv')}
npg = rd(S, 'NPG_scoring.csv')
for r in npg: p = pn[(int(r['k']), int(r['npg']), r['backend'])]; r['pred_gas'] = f"{int(p['G_pred']):,} [{int(p['G_lo']):,}, {int(p['G_hi']):,}]"
w('### N1. `native_per_gas` intervention: binding meter and final gas (k ∈ {1, 4, 16})\n'); t(sorted(npg, key=lambda r: (int(r['k']), int(r['npg']), r['backend'])), ['k', 'npg', 'backend', 'predicted_meter', 'measured_meter', 'meter_verdict', 'pred_gas', 'measured_gas', 'gas_in_interval'])
w('### N2. Ranking per level\n'); t(sorted(rd(S, 'NPG_ranking.csv'), key=lambda r: (int(r['k']), int(r['npg']))), ['k', 'npg', 'ratio', 'measured_class', 'predicted_class', 'ratio_in_interval', 'verdict'])
# ---------- SEM ----------
w('### H6. Semantic anchors vs context-tag cell at the same k\n'); t(rd(S, 'SEM_scoring.csv'), ['env', 'backend', 'anchor', 'k', 'metric', 'rel_diff', 'epsilon', 'verdict'])
# ---------- AC ----------
ac = rd(S, 'AC_checks.csv'); g = collections.defaultdict(lambda: [0, 0, collections.Counter()])
for a in ac: x = g[(a['check'], a['env'])]; x[0] += 1; x[1] += a['ok'] != 'True'; x[2][a['ok']] += 1
w('### A1. Accounting identities and controls\n'); t([dict(check=k[0], env=k[1], n=v[0], not_true=v[1], values=dict(v[2])) for k, v in sorted(g.items())], ['check', 'env', 'n', 'not_true', 'values'])
w('### Scorer summary.json\n'); w('```'); w(json.dumps(summ, indent=1)); w('```')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('lines', len(L))
