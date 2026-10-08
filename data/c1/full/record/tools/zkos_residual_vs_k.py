#!/usr/bin/env python3
"""POST-REGISTERED DESCRIPTIVE ANALYSIS (V2-M5; not part of the frozen scoring plan; labelled post hoc per 19-… rule 5).
ZKsync OS v32.0 conditional-model residuals versus k, Groth16 and PLONK separately, from the FROZEN scorer output
(ZC_scoring.csv: per-proof prediction from the frozen model with base / c from registered k = 1). No new model, no refit,
no change of tolerance. Mechanism columns are descriptive: the frozen v0.4.0 trace-model components of the same proof
(opcodes, precompiles, keccak, copies) and their change relative to k = 1.
usage: zkos_residual_vs_k.py <scoring_dir> <records.jsonl ...> -- <out_dir>"""
import sys, os, csv, json, statistics, collections
a = sys.argv[1:]; i = a.index('--'); S, FILES, OUT = a[0], a[1:i], a[i + 1]; os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.expanduser('~/c1/pkg/model')); import zkos_native_trace_model as ZT
recs = [json.loads(l) for f in FILES for l in open(f) if l.strip()]
meas = [r for r in recs if r['role'] == 'measurement' and r['op'] == 'verify_proof_direct']
trace = {r['proof_id']: r['evm_trace'] for r in meas if r['env'] == 'evm-osaka' and r.get('evm_trace')}
zk = {r['proof_id']: r for r in meas if r['env'] == 'zkos-v32' and r['regime']['npg'] == 100 and not int(r['regime'].get('priority_fee') or 0)}
zc = list(csv.DictReader(open(os.path.join(S, 'ZC_scoring.csv'))))
summ = json.load(open(os.path.join(S, 'summary.json'))); base, cpc = summ['ZC_constants']['base'], summ['ZC_constants']['per_call']
# k = 1 reference components (mean over the 8 proofs) per backend
ref = {}
for b in ('groth16', 'plonk'):
    comps = [ZT.components(trace[p], b, '0.4.0') for p, r in zk.items() if r['backend'] == b and r['k'] == 1 and p in trace]
    ref[b] = {c: statistics.mean(x[c] for x in comps) for c in ('ops', 'pre', 'kec', 'cop', 'sum')}
    ref[b]['measured'] = statistics.mean(zk[p]['zkos']['computational_native'] for p, r in zk.items() if r['backend'] == b and r['k'] == 1)
rows = []; per = collections.defaultdict(list)
for z in zc:
    p = z['proof']; r = zk.get(p); b = z['backend']
    if r is None: continue
    comp = ZT.components(trace[p], b, '0.4.0'); res = int(z['measured']) - int(z['pred'])
    per[(b, int(z['k']), z['relation'])].append(dict(res=res, rel=float(z['err_rel']), status=z['status'], comp=comp, measured=int(z['measured']), pred=int(z['pred'])))
for (b, k, rel), v in sorted(per.items()):
    m = lambda f: statistics.mean(f(x) for x in v)
    rows.append(dict(backend=b, k=k, relation=rel, n=len(v), pass_n=sum(x['status'] == 'PASS' for x in v), fail_n=sum(x['status'] != 'PASS' for x in v),
        mean_residual_native=round(m(lambda x: x['res']), 1), min_residual=min(x['res'] for x in v), max_residual=max(x['res'] for x in v),
        mean_err_rel_pct=round(100 * m(lambda x: x['rel']), 5), min_err_pct=round(100 * min(x['rel'] for x in v), 5), max_err_pct=round(100 * max(x['rel'] for x in v), 5),
        residual_per_extra_input=(round(m(lambda x: x['res']) / (k - 1), 1) if k > 1 else ''),
        measured_minus_k1=round(m(lambda x: x['measured']) - ref[b]['measured'], 1),
        d_ops=round(m(lambda x: x['comp']['ops']) - ref[b]['ops'], 1), d_precompiles=round(m(lambda x: x['comp']['pre']) - ref[b]['pre'], 1),
        d_keccak=round(m(lambda x: x['comp']['kec']) - ref[b]['kec'], 1), d_copies=round(m(lambda x: x['comp']['cop']) - ref[b]['cop'], 1),
        d_ncalls_term=round(cpc * (ZT.ncalls(b, k) - ZT.ncalls(b, 1)), 1)))
w = csv.DictWriter(open(os.path.join(OUT, 'ZKOS-residual-vs-k.csv'), 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# descriptive least-squares line of mean residual on k over the context-tag cells (k <= 32), per backend (no model, no refit)
desc = {}
for b in ('groth16', 'plonk'):
    pts = [(r['k'], r['mean_residual_native']) for r in rows if r['backend'] == b and r['relation'] == 'ctx' and r['k'] <= 32]
    if len(pts) >= 3:
        xs, ys = zip(*pts); mx, my = statistics.mean(xs), statistics.mean(ys); sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in pts)
        sl = sxy / sxx; ic = my - sl * mx; ssr = sum((y - (ic + sl * x)) ** 2 for x, y in pts); sst = sum((y - my) ** 2 for y in ys)
        desc[b] = dict(n_k=len(pts), ks=list(xs), slope_native_per_k=round(sl, 2), intercept=round(ic, 1), r2=round(1 - ssr / sst, 4) if sst else None,
                       max_abs_dev_from_line=round(max(abs(y - (ic + sl * x)) for x, y in pts), 1), first_k_failing=next((r['k'] for r in sorted([r for r in rows if r['backend'] == b and r['relation'] == 'ctx'], key=lambda r: r['k']) if r['fail_n']), None))
json.dump(dict(label='POST-REGISTERED DESCRIPTIVE (not a model, not a refit)', ZC_constants=dict(base=base, per_call=cpc), k1_reference=ref, line=desc), open(os.path.join(OUT, 'ZKOS-residual-vs-k.json'), 'w'), indent=1)
print(json.dumps(desc, indent=1))
