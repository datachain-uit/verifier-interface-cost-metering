#!/usr/bin/env python3
"""V2-C1 frozen a-priori prediction generator (prediction set P).

Calibration sources (declared in 07-parameter-ledger.csv):
  * P0 feasibility cells at k in CAL_K = {1, 4} only (EVM Osaka, EVM Petersburg, EraVM v29); EraVM v27 at k = 1 only;
  * the ZKsync OS v32.0 / VM v0.4.0 version-selection smoke cells at k = 1 (G16, PLONK; proof j0) for the two shared constants;
  * published constants: ZKsync OS VM v0.4.0 source (commit 69bc4305) applied to P0 EDR opcode traces;
  * the frozen V2-C1 corpus (exact calldata of every registered transaction).
P0 cells at k not in CAL_K enter ONLY the structural tolerance tau_struct (residual of the calibrated model at seen,
not-fitted k <= 32). No registered measurement exists when this runs.
"""
import json, glob, os, sys, csv, math
HOME = os.path.expanduser('~'); OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HOME, 'c1/pkg/predictions')
sys.path.insert(0, os.path.join(HOME, 'c1/model'))
import zkos_native_trace_model as ZT
from c1_model import *
mean = lambda xs: sum(xs) / len(xs)
def rel_range(xs): return (max(xs) - min(xs)) / mean(xs)
def ctx_name(k): return 'v1_d11' if k == 1 else f'ctx_d11_k{k}'
REG = {1: 'c1_k01', 2: 'c1_ctx_k02', 4: 'c1_ctx_k04', 6: 'c1_ctx_k06', 8: 'c1_ctx_k08', 12: 'c1_ctx_k12', 16: 'c1_ctx_k16', 24: 'c1_ctx_k24', 32: 'c1_ctx_k32', 64: 'c1_ctx_k64'}
REG_SEM = {('a4', 4): 'c1_a4', ('a8', 8): 'c1_a8', ('disc', 4): 'c1_disc_k04'}
def p0_cells():
    cells = {}
    for f in glob.glob(os.path.join(HOME, 'p0/out/sweep-*.json')):
        d = json.load(open(f)); base = os.path.basename(f)
        if 'mini_' in base or 'petersburg-bytecode' in base: continue
        env = {'evm': 'evm-' + str(d.get('regime') or 'osaka'), 'eravm': 'eravm-' + str(d.get('regime') or 29)}[d['arm']]
        fld = 'gasUsed' if d['arm'] == 'evm' else 'computational_gas'
        def ys(op):
            nz = 68 if env == 'evm-petersburg' else 16   # calldata price per non-zero byte: 68 before Istanbul (EIP-2028), 16 after; 4 per zero byte
            return [(r[fld] - nz * (r['calldata_bytes'] - r['calldata_zero']) - 4 * r['calldata_zero']) if d['arm'] == 'evm' else r[fld] for r in d['rows'] if r['op'] == op]
        cells[(env, d['circuit'], d['backend'])] = dict(k=d['k'], dir=ys('verify_proof_direct'), app=ys('verify_credential'))
    return cells
def corpus_cd():
    f = os.environ.get('C1_CALLDATA') or os.path.join(HOME, 'c1/corpus/corpus-calldata.json'); cd = json.load(open(f)); out = {}
    for pid, r in cd.items():
        for m in ('dir', 'app'): out.setdefault((r['circuit'], r['backend'], m), []).append((r[m]['bytes'], r[m]['zero']))
    return {k: (mean([x[0] for x in v]), mean([x[1] for x in v])) for k, v in out.items()}
def cd_gas(CD, key, env):
    nbytes, nzero = CD[key]; nz = 68 if env == 'evm-petersburg' else 16
    return nz * (nbytes - nzero) + 4 * nzero
def main():
    os.makedirs(OUT, exist_ok=True); cells = p0_cells(); CD = corpus_cd(); par = {}; tol = {}; checks = []
    for env in ('evm-osaka', 'evm-petersburg', 'eravm-29'):
        for b in ('groth16', 'plonk'):
            for m in ('dir', 'app'):
                A, B = fit(mean(cells[(env, ctx_name(1), b)][m]), mean(cells[(env, ctx_name(4), b)][m]), env, b)
                par[(env, b, m)] = dict(A=A, B=B, source='P0 cell means at k=1 (V1 relation) and k=4 (context tags)')
                res = []
                for k in sorted(SEEN_NOT_FITTED | set(LIMIT)):
                    c = cells.get((env, ctx_name(k), b))
                    if not c: continue
                    p = kmodel(A, B, env, b, k); e = (mean(c[m]) - p) / p
                    checks.append(dict(env=env, backend=b, metric='Y_' + m, k=k, model=round(p), p0_mean=round(mean(c[m]), 1), err_pct=round(100 * e, 4), enters_tau=k <= 32))
                    if k <= 32: res.append(abs(e))
                noise = max(rel_range(c[m]) / 2 for (e_, cc, bb), c in cells.items() if e_ == env and bb == b and (cc.startswith(('ctx_', 'v1_'))) and c['k'] <= 32)
                tol[(env, b, m)] = dict(tau_noise=noise, tau_struct=max(res) if res else 0.0, basis_noise='max P0 within-cell half-range (ctx/V1 cells, k<=32)', basis_struct='max |residual| at P0 k in {2,16,32}' if env != 'evm-petersburg' else 'residual at P0 k=16')
    FR = {'eravm-29': {'ecadd': 301, 'ecmul': 5496}, 'eravm-27': {'ecadd': 28415, 'ecmul': 277372}}
    for b in ('groth16', 'plonk'):
        for m in ('dir', 'app'):
            A = mean(cells[('eravm-27', ctx_name(1), b)][m]); B29 = par[('eravm-29', b, m)]['B']
            B = B29 + (sum(FR['eravm-27'].values()) - sum(FR['eravm-29'].values())) * (b == 'groth16')
            par[('eravm-27', b, m)] = dict(A=A, B=B, source='A: P0 v27 k=1; B: B_v29 + per-input precompile frame swap (v27 minus v29 frames per call, measured at k=1)')
            res = []
            for k in (4, 16):
                c = cells[('eravm-27', ctx_name(k), b)]; p = kmodel(A, B, 'eravm-27', b, k); e = (mean(c[m]) - p) / p; res.append(abs(e))
                checks.append(dict(env='eravm-27', backend=b, metric='Y_' + m, k=k, model=round(p), p0_mean=round(mean(c[m]), 1), err_pct=round(100 * e, 4), enters_tau=True))
            noise = max(rel_range(c[m]) / 2 for (e_, cc, bb), c in cells.items() if e_ == 'eravm-27' and bb == b)
            tol[('eravm-27', b, m)] = dict(tau_noise=noise, tau_struct=max(res), basis_noise='max P0 v27 within-cell half-range', basis_struct='max |residual| at P0 v27 k in {4,16}')
    # ZKsync OS v32.0 (VM v0.4.0)
    tr = {}
    for f in glob.glob(os.path.join(HOME, 'p0/out/sweep-evm-osaka-*.json')):
        d = json.load(open(f)); r = [x for x in d['rows'] if x['op'] == 'verify_proof_direct' and x.get('trace')]
        if not r: continue
        t = r[0]['trace']
        if d['backend'] != 'groth16' and not t.get('keccak_sizes'): continue     # P0 trace without keccak/copy profile (capture defect) -> unusable
        tr[(d['circuit'], d['backend'])] = (d['k'], ZT.components(t, d['backend'], '0.4.0'))
    smoke = {b: [x['computational_native'] for x in json.load(open(os.path.join(HOME, f'p0/out/zkos-v32c-v1_d11-{b}-p0.json')))['rows'] if x['op'] == 'verify_proof_direct'] for b in ('groth16', 'plonk')}
    base, cpc = ZT.calibrate([(b, 1, tr[('v1_d11', b)][1]['sum'], smoke[b][0]) for b in ('groth16', 'plonk')])
    par[('zkos-v32', 'shared', 'native')] = dict(base=base, per_call=cpc, source='v32.0 smoke cells k=1, proof j0, G16 and PLONK; same proofs traced in EDR (P0)')
    nat = {key: ZT.predict(c, key[1], k, base, cpc) for key, (k, c) in tr.items()}
    h31 = {}
    for f in glob.glob(os.path.join(HOME, 'p0/out/zkos-t1-*-p0.json')):
        d = json.load(open(f))
        if not (d['circuit'].startswith(('ctx_', 'v1_')) and d['k'] <= 32): continue
        ns = [x['computational_native'] for x in d['rows'] if x['op'] == 'verify_proof_direct']
        h31[d['backend']] = max(h31.get(d['backend'], 0.0), rel_range(ns) / 2)
    # tau_cond: max |held-out error| of the SAME model form on P0 v31 (VM v0.3.2): base, c fitted on v31 k=1 (G16, PLONK) only
    tr31 = {}
    for f in glob.glob(os.path.join(HOME, 'p0/out/sweep-evm-osaka-*.json')):
        d = json.load(open(f)); r = [x for x in d['rows'] if x['op'] == 'verify_proof_direct' and x.get('trace')]
        if r and (d['backend'] == 'groth16' or r[0]['trace'].get('keccak_sizes')): tr31[(d['circuit'], d['backend'])] = (d['k'], ZT.components(r[0]['trace'], d['backend'], '0.3.2'))
    m31 = {}
    for f in glob.glob(os.path.join(HOME, 'p0/out/zkos-t1-*-p0.json')) + glob.glob(os.path.join(HOME, 'p0/out/zkos-t3-mini*-p0.json')):
        d = json.load(open(f)); m31[(d['circuit'], d['backend'])] = [x for x in d['rows'] if x['op'] == 'verify_proof_direct'][0]['computational_native']
    b31, c31 = ZT.calibrate([(b, 1, tr31[('v1_d11', b)][1]['sum'], m31[('v1_d11', b)]) for b in ('groth16', 'plonk')])
    V31 = {}
    for key, (k, comp) in tr31.items():
        if key not in m31 or key[0] == 'v1_d11' or k > 32 or (key[1] == 'groth16' and key[0].startswith('mini')) or (key[1] == 'plonk' and key[0].startswith('mini')): continue
        p31 = ZT.predict(comp, key[1], k, b31, c31); e = (m31[key] - p31) / p31; V31[key[1]] = max(V31.get(key[1], 0.0), abs(e))
        checks.append(dict(env='zkos-v31 P0 (VM v0.3.2) conditional', backend=key[1], metric='N_dir', k=k, model=round(p31), p0_mean=m31[key], err_pct=round(100 * e, 4), enters_tau=True))   # P0 v31 held-out |error| max of the same model form (ctx/anchor cells k<=32; FFLONK mini k<=16)
    for b in ('groth16', 'plonk', 'fflonk'):
        n1, n4 = (nat[('mini_d0_k1', b)], nat[('mini_d0_k4', b)]) if b == 'fflonk' else (nat[('v1_d11', b)], nat[('ctx_d11_k4', b)])
        A, B = fit(n1, n4, 'zkos-v32', b); par[('zkos-v32', b, 'native')] = dict(A=A, B=B, source='k-model fitted on trace-model natives at k=1,4' + (' (FFLONK: depth-0 family traces)' if b == 'fflonk' else ''))
        res = []
        for key, v in nat.items():
            k = tr[key][0]
            if key[1] != b or k in CAL_K or k > 32 or (b != 'fflonk' and not key[0].startswith(('ctx_', 'v1_'))): continue
            e = (v - kmodel(A, B, 'zkos-v32', b, k)) / kmodel(A, B, 'zkos-v32', b, k); res.append(abs(e))
            checks.append(dict(env='zkos-v32 (trace-model natives)', backend=b, metric='N_dir', k=k, model=round(kmodel(A, B, 'zkos-v32', b, k)), p0_mean=round(v), err_pct=round(100 * e, 4), enters_tau=True))
        tol[('zkos-v32', b, 'native')] = dict(tau_noise=max(rel_range(smoke[b]) / 2 if b in smoke else 0.0, h31.get(b, 0.0)), tau_struct=(max(res) if res else 0.0) + V31[b],
                                               basis_noise='max of v32 smoke half-range (k=1) and P0 v31 native half-ranges (ctx/V1, k<=32), transferred', basis_struct='k-model interpolation residual on v0.4.0 trace-model natives + transferred v31 held-out residual', tau_cond=V31[b], basis_cond='max |held-out error| of the conditional model on P0 v31 (base, c from v31 k=1 G16+PLONK; FFLONK = depth-0 family, all k)')
    T = lambda key: tol[key]['tau_noise'] + tol[key]['tau_struct']
    # ---------- per-cell predictions ----------
    rows = []; curves = {}
    def role(env, rel, k, b=None):
        if b == 'fflonk': return 'HELD-OUT-BACKEND'
        if rel != 'ctx': return 'SEMANTIC'
        if k in LIMIT: return 'LIMIT-CHECK'
        if env == 'evm-petersburg': return 'SUPPORTING-CONTROL' + ('/calibration' if k in CAL_K else '/held-out-k')
        if env == 'eravm-27': return 'CALIBRATION' if k == 1 else ('HELD-OUT-REGIME/k-seen-in-P0' if k in (4, 16) else 'HELD-OUT-REGIME/k-unseen')
        if env == 'zkos-v32': return 'CALIBRATION' if k == 1 else ('HELD-OUT-k/seen-in-P0-trace' if k in (2, 4, 16, 32) else 'HELD-OUT-k/strictly-unseen')
        if k in CAL_K: return 'CALIBRATION'
        return 'HELD-OUT-k/seen-in-P0' if k in SEEN_NOT_FITTED else 'HELD-OUT-k/strictly-unseen'
    RELS = [('ctx', k) for k in GRID + LIMIT] + [('a4', 4), ('a8', 8), ('disc', 4)]
    def regname(rel, k): return REG[k] if rel == 'ctx' else REG_SEM[(rel, k)]
    for env in ('evm-osaka', 'eravm-29', 'eravm-27', 'evm-petersburg'):
        for b in ('groth16', 'plonk'):
            for m in ('dir', 'app'):
                A, B = par[(env, b, m)]['A'], par[(env, b, m)]['B']; t = T((env, b, m))
                for rel, k in RELS:
                    if env == 'eravm-27' and (rel != 'ctx' or k not in (1, 4, 6, 8, 16)): continue
                    if env == 'evm-petersburg' and (rel != 'ctx' or k not in (1, 4, 16)): continue
                    y = kmodel(A, B, env, b, k)
                    if env.startswith('evm'):
                        cd = cd_gas(CD, (regname(rel, k), b, m), env); p = y + cd; unit = 'gas'
                    else: cd = 0; p = y; unit = 'eravm_computational_gas'
                    lo, hi = y * (1 - t) + cd, y * (1 + t) + cd
                    rows.append(dict(cell=f'{env}|{b}|{regname(rel, k)}|Y_{m}', env=env, backend=b, circuit=regname(rel, k), relation=rel, k=k, metric='Y_' + m, unit=unit,
                                     pred=round(p), lo=math.floor(lo), hi=math.ceil(hi), tau_rel=round(t, 6), calldata_gas=round(cd, 1), role=role(env, rel, k)))
                    if rel == 'ctx': curves[(env, b, m)] = curves.get((env, b, m), {}) | {k: (p, lo, hi)}
    for b in ('groth16', 'plonk', 'fflonk'):
        A, B = par[('zkos-v32', b, 'native')]['A'], par[('zkos-v32', b, 'native')]['B']; t = T(('zkos-v32', b, 'native'))
        for rel, k in RELS:
            if b == 'fflonk' and (rel != 'ctx' or k not in (1, 4, 16, 32)): continue
            p = kmodel(A, B, 'zkos-v32', b, k); nm = regname(rel, k) if b != 'fflonk' else f'c1_ff_k{k:02d}'
            rows.append(dict(cell=f'zkos-v32|{b}|{nm}|N_dir', env='zkos-v32', backend=b, circuit=nm, relation=rel, k=k, metric='N_dir', unit='computational_native',
                             pred=round(p), lo=math.floor(p * (1 - t)), hi=math.ceil(p * (1 + t)), tau_rel=round(t, 6), calldata_gas='', role=role('zkos-v32', rel, k, b)))
            if rel == 'ctx': curves[('zkos-v32', b, 'native')] = curves.get(('zkos-v32', b, 'native'), {}) | {k: (p, p * (1 - t), p * (1 + t))}
    # ZKsync OS gas at the default operator setting (native_per_gas = 100) and at the intervention levels
    def zk_curve(b, npg):
        out = {}
        for k in GRID + LIMIT:
            n, nlo, nhi = curves[('zkos-v32', b, 'native')][k]; g, glo, ghi = curves[('evm-osaka', b, 'dir')][k]
            out[k] = (max(g, n / npg), max(glo, nlo / npg), max(ghi, nhi / npg), 'NATIVE' if nlo / npg > ghi else ('EVM_GAS' if nhi / npg < glo else 'INDETERMINATE'))
        return out
    for b in ('groth16', 'plonk'):
        for k, (p, lo, hi, bind) in zk_curve(b, 100).items():
            nm = REG[k]; rows.append(dict(cell=f'zkos-v32@npg100|{b}|{nm}|G_dir', env='zkos-v32@npg100', backend=b, circuit=nm, relation='ctx', k=k, metric='G_dir', unit='gas', pred=round(p), lo=math.floor(lo), hi=math.ceil(hi),
                                          tau_rel='', calldata_gas='', role=('CALIBRATION' if k == 1 else 'HELD-OUT-k') + f'/binding={bind}'))
            curves[('zkos-v32@npg100', b, 'dir')] = curves.get(('zkos-v32@npg100', b, 'dir'), {}) | {k: (p, lo, hi)}
    # ---------- ratios, signs, crossovers ----------
    sg = []; xo = []
    for env, m in [('evm-osaka', 'dir'), ('evm-osaka', 'app'), ('eravm-29', 'dir'), ('eravm-29', 'app'), ('eravm-27', 'dir'), ('evm-petersburg', 'dir'), ('zkos-v32', 'native'), ('zkos-v32@npg100', 'dir')]:
        G, P = curves[(env, 'groth16', m)], curves[(env, 'plonk', m)]; ks = sorted(set(G) & set(P))
        for k in ks:
            r = P[k][0] / G[k][0]; rlo = P[k][1] / G[k][2]; rhi = P[k][2] / G[k][1]
            sg.append(dict(env=env, metric=m, k=k, ratio_plonk_over_g16=round(r, 5), ratio_lo=round(rlo, 5), ratio_hi=round(rhi, 5), predicted_sign=sign_class(rlo, rhi)))
        kk = list(range(1, max(ks) + 1)) if env not in ('eravm-27', 'evm-petersburg') else ks
        def dense(C, i):  # evaluate curve on integer k (model-consistent for unseen integers is not needed: use linear interpolation between modelled points)
            pts = sorted(C); vals = []
            for k in kk:
                j = max(x for x in pts if x <= k); j2 = min(x for x in pts if x >= k)
                vals.append(C[j][i] if j == j2 else C[j][i] + (C[j2][i] - C[j][i]) * (k - j) / (j2 - j))
            return vals
        dp = [a - b for a, b in zip(dense(P, 0), dense(G, 0))]
        dlo = [a - b for a, b in zip(dense(P, 1), dense(G, 2))]; dhi = [a - b for a, b in zip(dense(P, 2), dense(G, 1))]
        c0, c1_, c2 = crossing(kk, dp), crossing(kk, dlo), crossing(kk, dhi)
        def fmt(c, d):
            if c is not None: return round(c, 2)
            return '<=1' if d[0] <= 0 else f'>{kk[-1]}'
        xo.append(dict(env=env, metric=m, kstar_point=fmt(c0, dp), kstar_lo=fmt(c1_, dlo), kstar_hi=fmt(c2, dhi), sign_at_k1=('PLONK_COSTLIER' if dp[0] > 0 else 'PLONK_CHEAPER'), evaluated_k_range=f'{kk[0]}..{kk[-1]}'))
    # ---------- ZKsync OS native_per_gas switch intervals and intervention levels ----------
    sw = []; lv = []; npgp = []
    for b in ('groth16', 'plonk'):
        for k in GRID:
            n, nlo, nhi = curves[('zkos-v32', b, 'native')][k]; g, glo, ghi = curves[('evm-osaka', b, 'dir')][k]
            sw.append(dict(backend=b, k=k, native_pred=round(n), evm_gas_pred=round(g), npg_switch=round(n / g, 2), npg_switch_lo=round(nlo / ghi, 2), npg_switch_hi=round(nhi / glo, 2)))
    S = {(r['backend'], r['k']): r for r in sw}
    for k in (1, 4, 16):
        levels = {100, 300}
        for b in ('groth16', 'plonk'):
            r = S[(b, k)]; w = (r['npg_switch_hi'] - r['npg_switch_lo']) / 2 / r['npg_switch']
            levels |= {math.floor(r['npg_switch'] * (1 - 2 * w)), math.ceil(r['npg_switch'] * (1 + 2 * w))}
        lo_s = min(S[('groth16', k)]['npg_switch'], S[('plonk', k)]['npg_switch']); hi_s = max(S[('groth16', k)]['npg_switch'], S[('plonk', k)]['npg_switch'])
        levels.add(round((lo_s + hi_s) / 2))
        for npg in sorted(levels):
            lv.append(dict(k=k, npg=npg, purpose=('away (below both switches)' if npg == 100 else 'away (above both switches)' if npg == 300 else 'between the two switches' if npg == round((lo_s + hi_s) / 2) else 'around a predicted switch')))
            pr = {}
            for b in ('groth16', 'plonk'):
                n, nlo, nhi = curves[('zkos-v32', b, 'native')][k]; g, glo, ghi = curves[('evm-osaka', b, 'dir')][k]
                bind = 'NATIVE' if nlo / npg > ghi else ('EVM_GAS' if nhi / npg < glo else 'INDETERMINATE')
                pr[b] = (max(g, n / npg), max(glo, nlo / npg), max(ghi, nhi / npg), bind)
                npgp.append(dict(k=k, npg=npg, backend=b, binding_meter=bind, G_pred=round(pr[b][0]), G_lo=math.floor(pr[b][1]), G_hi=math.ceil(pr[b][2])))
            rlo = pr['plonk'][1] / pr['groth16'][2]; rhi = pr['plonk'][2] / pr['groth16'][1]
            npgp.append(dict(k=k, npg=npg, backend='ratio', binding_meter=sign_class(rlo, rhi), G_pred=round(pr['plonk'][0] / pr['groth16'][0], 5), G_lo=round(rlo, 5), G_hi=round(rhi, 5)))
    # ---------- equality bands for classifying MEASURED cells (raw metric, P0 within-cell half-ranges) ----------
    eb = []
    for env in ('evm-osaka', 'eravm-29', 'eravm-27', 'evm-petersburg'):
        h = {}
        for b in ('groth16', 'plonk'):
            hs = []
            for f in glob.glob(os.path.join(HOME, f'p0/out/sweep-{env.split("-")[0]}-{env.split("-")[1]}-*-{b}*.json')):
                if 'mini_' in f or 'petersburg-bytecode' in f: continue
                d = json.load(open(f))
                if not (d['circuit'].startswith(('ctx_', 'v1_')) and d['k'] <= 32): continue
                ys = [r['gasUsed'] if d['arm'] == 'evm' else r['computational_gas'] for r in d['rows'] if r['op'] == 'verify_proof_direct']
                hs.append(rel_range(ys) / 2)
            h[b] = max(hs)
        eb.append(dict(env=env, h_groth16=round(h['groth16'], 6), h_plonk=round(h['plonk'], 6), epsilon=round(h['groth16'] + h['plonk'], 6), basis='max P0 raw within-cell half-range per backend (ctx/V1 cells, k<=32), summed'))
    hz = max(rel_range(smoke['plonk']) / 2, h31.get('plonk', 0.0)); hg = max(rel_range(smoke['groth16']) / 2, h31.get('groth16', 0.0))
    eb.append(dict(env='zkos-v32', h_groth16=round(hg, 6), h_plonk=round(hz, 6), epsilon=round(hz + hg, 6), basis='max of v32 smoke half-range (k=1) and P0 v31 native half-ranges (ctx/V1, k<=32), per backend, summed; native-bound gas inherits it; EVM-bound ZKsync OS cells use the evm-osaka band'))
    W = lambda name, data: (lambda f: (lambda w: (w.writeheader(), w.writerows(data)))(csv.DictWriter(f, fieldnames=list(data[0].keys()))))(open(os.path.join(OUT, name), 'w', newline=''))
    W('predictions_cells.csv', rows); W('predictions_signs.csv', sg); W('crossover_intervals.csv', xo); W('zkos_switch_intervals.csv', sw); W('zkos_npg_levels.csv', lv); W('zkos_npg_predictions.csv', npgp); W('p0_model_check.csv', checks); W('equality_bands.csv', eb)
    json.dump(dict(parameters={'|'.join(k): v for k, v in par.items()}, tolerances={'|'.join(k): v for k, v in tol.items()}), open(os.path.join(OUT, 'fitted_parameters_and_tolerances.json'), 'w'), indent=1)
    return xo, sw, lv
if __name__ == '__main__':
    xo, sw, lv = main()
    for r in xo: print(r)
