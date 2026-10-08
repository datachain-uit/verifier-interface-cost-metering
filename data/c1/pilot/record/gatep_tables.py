#!/usr/bin/env python3
"""Gate-P report tables: renders the FROZEN scorer outputs for the pilot cells (no recomputation of any verdict).
usage: gatep_tables.py <scoring_dir> <predictions_dir> <evidence_root> <out_md>"""
import csv, json, os, sys, collections
S, PD, ER, OUT = sys.argv[1:5]
rd = lambda d, n: list(csv.DictReader(open(os.path.join(d, n))))
PILOT = {'c1_k01': 1, 'c1_ctx_k02': 2, 'c1_ctx_k04': 4, 'c1_ctx_k16': 16}
L = []; w = L.append
def t(rows, cols, hdr=None):
    w('| ' + ' | '.join(hdr or cols) + ' |'); w('|' + '---|' * len(cols))
    for r in rows: w('| ' + ' | '.join(str(r.get(c, '')) for c in cols) + ' |')
    w('')
summ = json.load(open(os.path.join(S, 'summary.json')))
# ---- accounting ----
ac = rd(S, 'AC_checks.csv'); g = collections.defaultdict(lambda: [0, 0])
for a in ac: g[(a['check'], a['env'])][0] += 1; g[(a['check'], a['env'])][1] += a['ok'] != 'True'
w('### A1. Accounting identities and controls (scorer section AC)\n')
t([dict(check=k[0], env=k[1], n=v[0], failed=v[1]) for k, v in sorted(g.items())], ['check', 'env', 'n', 'failed'])
# ---- cell summaries ----
cs = [r for r in rd(S, 'CELL_summary.csv') if r['circuit'] in PILOT and r['metric'] in ('Y_dir', 'Y_app', 'N_dir')]
for r in cs: r['mean'] = f"{float(r['mean']):,.1f}"; r['range'] = f"{int(float(r['min'])):,} – {int(float(r['max'])):,}"; r['half_range_%'] = f"{100 * float(r['half_range_rel']):.4f}"
w('### A2. Registered cell summaries (8 proofs per cell)\n')
t(sorted(cs, key=lambda r: (r['env'], r['metric'], r['backend'], int(r['k']))), ['env', 'backend', 'k', 'metric', 'n', 'mean', 'range', 'half_range_%'])
# ---- P: a-priori predictions, pilot cells ----
ps = []
for r in rd(S, 'P_scoring.csv'):
    env, b, circ, metric = r['cell'].split('|')
    if circ not in PILOT or r['status'] == 'MISSING': continue
    r.update(env=env, backend=b, k=PILOT[circ], metric=metric); r['err_%'] = f"{100 * float(r['err_rel']):+.4f}"
    r['pred'] = f"{int(r['pred']):,}"; r['interval'] = f"[{int(r['lo']):,}, {int(r['hi']):,}]"; r['measured'] = f"{float(r['measured_mean']):,.1f}"; ps.append(r)
P_tau = {r['cell']: r['tau_rel'] for r in rd(PD, 'predictions_cells.csv')}
for r in ps: r['tau_%'] = (f"{100 * float(P_tau[r['cell']]):.4f}" if P_tau.get(r['cell']) else 'max(EVM, N/npg)')
w('### P1. A-priori numeric predictions (set P) vs registered means — pilot cells\n')
t(sorted(ps, key=lambda r: (r['env'], r['metric'], r['backend'], r['k'])), ['env', 'backend', 'k', 'metric', 'role', 'pred', 'interval', 'measured', 'err_%', 'tau_%', 'status'])
# ---- R ----
rs = rd(S, 'R_scoring.csv')
for r in rs: r['err_%'] = f"{100 * float(r['err_rel']):+.4f}"; r['tau_%'] = f"{100 * float(r['tau']):.4f}"
w('### P2. Registered-calibration procedure R (A, B from registered k = 1, 4; held-out k = 2, 16 are seen-in-P0)\n')
t(rs, ['env', 'backend', 'metric', 'k', 'pred', 'measured', 'err_%', 'tau_%', 'heldout', 'status'])
# ---- ZC ----
zc = rd(S, 'ZC_scoring.csv'); zg = collections.defaultdict(list)
for r in zc: zg[(r['backend'], int(r['k']))].append(r)
w('### P3. ZKsync OS conditional model (base, c from registered k = 1 Groth16 + PLONK; per-proof prediction from the same proof\'s EDR trace)\n')
w(f"Constants fitted by the scorer: {json.dumps(summ.get('ZC_constants'))}\n")
t([dict(backend=b, k=k, n=len(v), max_abs_err_pct=f"{100 * max(abs(float(x['err_rel'])) for x in v):.4f}", mean_err_pct=f"{100 * sum(float(x['err_rel']) for x in v) / len(v):+.4f}",
        tau_cond_pct=f"{100 * float(v[0]['tau_cond']):.4f}", passed=sum(x['status'] == 'PASS' for x in v), failed=sum(x['status'] != 'PASS' for x in v)) for (b, k), v in sorted(zg.items())],
  ['backend', 'k', 'n', 'mean_err_pct', 'max_abs_err_pct', 'tau_cond_pct', 'passed', 'failed'])
# ---- SG / MONO / XO ----
sg = rd(S, 'SG_signs.csv')
w('### E1. Signs and ratio intervals (equality band ε from P0)\n')
t(sg, ['env', 'metric', 'k', 'ratio', 'measured_class', 'all_vs_all', 'predicted_sign', 'sign_verdict', 'ratio_in_interval'])
w('### E2. Monotonicity of the PLONK/Groth16 ratio\n'); t(rd(S, 'SG_monotonicity.csv'), ['env', 'metric', 'n_k', 'violations', 'verdict'])
w('### E3. Crossover location (frozen rule: linear interpolation between the bracketing grid points)\n'); t(rd(S, 'XO_crossovers.csv'), ['env', 'metric', 'kstar_measured', 'measured_interval', 'predicted', 'verdict'])
# ---- NPG ----
npg = rd(S, 'NPG_scoring.csv')
w('### P4. `native_per_gas` intervention at k = 1: binding meter and gas\n')
pn = {(int(r['k']), int(r['npg']), r['backend']): r for r in rd(PD, 'zkos_npg_predictions.csv')}
for r in npg: p = pn[(int(r['k']), int(r['npg']), r['backend'])]; r['pred_gas_interval'] = f"{int(p['G_pred']):,} [{int(p['G_lo']):,}, {int(p['G_hi']):,}]"
t(sorted(npg, key=lambda r: (int(r['npg']), r['backend'])), ['k', 'npg', 'backend', 'predicted_meter', 'measured_meter', 'meter_verdict', 'pred_gas_interval', 'measured_gas', 'gas_in_interval'])
w('### P5. Ranking per `native_per_gas` level (k = 1)\n'); t(sorted(rd(S, 'NPG_ranking.csv'), key=lambda r: int(r['npg'])), ['k', 'npg', 'ratio', 'measured_class', 'predicted_class', 'ratio_in_interval', 'verdict'])
w('### Scorer summary (counts as emitted by `summary.json`)\n'); w('```'); w(json.dumps(summ, indent=1)); w('```')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('tables', len(L))
