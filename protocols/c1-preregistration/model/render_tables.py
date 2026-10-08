#!/usr/bin/env python3
# Renders 10-crossover-intervals.md, 11-zksync-os-switch-intervals.md, 09-numeric-predictions.md (summary) and 13-tolerances.csv from the frozen CSV/JSON.
import csv, json, os, sys
PKG = sys.argv[1]; D = os.path.join(PKG, '09-numeric-predictions'); rd = lambda n: list(csv.DictReader(open(os.path.join(D, n))))
xo = rd('crossover_intervals.csv'); sg = rd('predictions_signs.csv'); sw = rd('zkos_switch_intervals.csv'); lv = rd('zkos_npg_levels.csv'); npg = rd('zkos_npg_predictions.csv'); eb = rd('equality_bands.csv')
F = json.load(open(os.path.join(D, 'fitted_parameters_and_tolerances.json')))
H = '**Generated** by `model/render_tables.py` from `09-numeric-predictions/` (frozen). Do not edit by hand.\n\n'
with open(os.path.join(PKG, '10-crossover-intervals.md'), 'w') as f:
    f.write('# 10 — Predicted crossover intervals (V2-C1, frozen)\n\n' + H)
    f.write('k\\* = k at which mean PLONK cost equals mean Groth16 cost (linear interpolation between modelled integer k). Interval from the\nprediction intervals of both templates (`13-criteria.md` §4). Source CSV: `09-numeric-predictions/crossover_intervals.csv`.\n\n')
    f.write('| Regime | Metric | k\\* point | k\\* interval | Sign at k = 1 | Class |\n|---|---|---|---|---|---|\n')
    cls = {'evm-osaka': 'CORE', 'eravm-29': 'CORE', 'zkos-v32': 'CORE (native)', 'zkos-v32@npg100': 'CORE (gas, default npg)', 'eravm-27': 'VALIDATION', 'evm-petersburg': 'SUPPORTING'}
    for r in xo: f.write(f"| {r['env']} | {r['metric']} | {r['kstar_point']} | [{r['kstar_lo']}, {r['kstar_hi']}] | {r['sign_at_k1']} | {cls.get(r['env'], '')} |\n")
    f.write('\n## Predicted sign per grid point (Y_dir; ZKsync OS native and default-npg gas)\n\n| Regime | ' + ' | '.join(f'k={k}' for k in (1, 2, 4, 6, 8, 12, 16, 24, 32)) + ' |\n|---|' + '---|' * 9 + '\n')
    ab = {'PLONK_COSTLIER': 'G<P', 'PLONK_CHEAPER': 'P<G', 'INDETERMINATE': '≈'}
    for env, m in [('evm-osaka', 'dir'), ('eravm-29', 'dir'), ('zkos-v32@npg100', 'dir'), ('eravm-27', 'dir'), ('evm-petersburg', 'dir')]:
        S = {int(r['k']): r for r in sg if r['env'] == env and r['metric'] == m}
        f.write(f'| {env} | ' + ' | '.join((ab[S[k]['predicted_sign']] + f" ({float(S[k]['ratio_plonk_over_g16']):.3f})") if k in S else '—' for k in (1, 2, 4, 6, 8, 12, 16, 24, 32)) + ' |\n')
    f.write('\n"G<P": Groth16 cheaper (PLONK/Groth16 ratio interval above 1); "P<G": PLONK cheaper; "≈": interval contains 1 (not sign-scored). Value in parentheses: predicted ratio.\n')
with open(os.path.join(PKG, '11-zksync-os-switch-intervals.md'), 'w') as f:
    f.write('# 11 — ZKsync OS v32.0: `native_per_gas` switch intervals and intervention levels (V2-C1, frozen)\n\n' + H)
    f.write('npg\\*(b, k) = N_b(k) / G_evm,b(k): below it the transaction is native-bound, above it EVM-gas-bound. Interval from the native and\nEVM-gas prediction intervals. CSVs: `zkos_switch_intervals.csv`, `zkos_npg_levels.csv`, `zkos_npg_predictions.csv`.\n\n')
    f.write('| Template | k | native (pred) | EVM gas (pred) | npg\\* | interval |\n|---|---|---|---|---|---|\n')
    for r in sw: f.write(f"| {r['backend']} | {r['k']} | {int(r['native_pred']):,} | {int(r['evm_gas_pred']):,} | {r['npg_switch']} | [{r['npg_switch_lo']}, {r['npg_switch_hi']}] |\n")
    f.write('\n## Pre-registered intervention levels and predictions\n\nLevels: 100 and 300 (away), each template\'s predicted switch × (1 ± 2 × relative half-width of its interval), rounded outward (around), and the midpoint of the two switches (between).\n\n')
    f.write('| k | npg | purpose | G16 meter | G16 gas [lo, hi] | PLONK meter | PLONK gas [lo, hi] | PLONK/G16 ratio [lo, hi] → class |\n|---|---|---|---|---|---|---|---|\n')
    P = {(int(r['k']), int(r['npg']), r['backend']): r for r in npg}
    for r in lv:
        k, n = int(r['k']), int(r['npg']); g, p, q = P[(k, n, 'groth16')], P[(k, n, 'plonk')], P[(k, n, 'ratio')]
        f.write(f"| {k} | {n} | {r['purpose']} | {g['binding_meter']} | {int(g['G_pred']):,} [{int(g['G_lo']):,}, {int(g['G_hi']):,}] | {p['binding_meter']} | {int(p['G_pred']):,} [{int(p['G_lo']):,}, {int(p['G_hi']):,}] | {q['G_pred']} [{q['G_lo']}, {q['G_hi']}] → {q['binding_meter']} |\n")
with open(os.path.join(PKG, '13-tolerances.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'tau_noise', 'tau_struct', 'tau_total', 'tau_cond', 'basis_noise', 'basis_struct'])
    for k, t in F['tolerances'].items(): w.writerow([k, f"{t['tau_noise']:.6f}", f"{t['tau_struct']:.6f}", f"{t['tau_noise'] + t['tau_struct']:.6f}", f"{t['tau_cond']:.6f}" if 'tau_cond' in t else '', t.get('basis_noise', ''), t.get('basis_struct', '')])
    for r in eb: w.writerow([f"equality_band|{r['env']}", r['h_groth16'], r['h_plonk'], r['epsilon'], '', r['basis'], ''])
print('rendered')
# ---- 09-numeric-predictions.md ----
pc = rd('predictions_cells.csv'); chk = rd('p0_model_check.csv')
with open(os.path.join(PKG, '09-numeric-predictions.md'), 'w') as f:
    f.write('# 09 — Numeric predictions, set P (V2-C1, frozen; immutable before the pilot)\n\n' + H)
    f.write('Generator: `model/c1_predict.py` (calibration sources in its header and in `07-parameter-ledger.csv`). Files in `09-numeric-predictions/`:\n\n')
    f.write('| File | Content |\n|---|---|\n| `predictions_cells.csv` | one row per (regime, template, circuit, metric): point prediction, [lo, hi], τ, calldata gas added (EVM), role |\n| `predictions_signs.csv` | predicted PLONK/Groth16 ratio, ratio interval and predicted class per (regime, k) |\n| `crossover_intervals.csv` | k\\* point and interval per regime (`10-…`) |\n| `zkos_switch_intervals.csv`, `zkos_npg_levels.csv`, `zkos_npg_predictions.csv` | ZKsync OS switch points, intervention levels and per-level predictions (`11-…`) |\n| `equality_bands.csv` | ε per regime |\n| `fitted_parameters_and_tolerances.json` | A, B, base, c and every τ with its basis |\n| `p0_model_check.csv` | residuals of the calibrated models at P0 seen-not-fitted k (the only use of those P0 cells: τ_struct) |\n\n')
    f.write('## Pilot cells (direct verifier call, a-priori)\n\n| Regime | Template | k | prediction | [lo, hi] | role |\n|---|---|---|---|---|---|\n')
    for r in pc:
        if r['relation'] == 'ctx' and int(r['k']) in (1, 2, 4, 16) and r['metric'] in ('Y_dir', 'N_dir', 'G_dir') and r['env'] in ('evm-osaka', 'eravm-29', 'zkos-v32', 'zkos-v32@npg100') and r['backend'] in ('groth16', 'plonk'):
            f.write(f"| {r['env']} ({r['metric']}, {r['unit']}) | {r['backend']} | {r['k']} | {int(r['pred']):,} | [{int(r['lo']):,}, {int(r['hi']):,}] | {r['role']} |\n")
    f.write('\n## P0 model check used for τ_struct\n\n| Model | Template | Metric | k | model | P0 | e (%) |\n|---|---|---|---|---|---|---|\n')
    for r in chk: f.write(f"| {r['env']} | {r['backend']} | {r['metric']} | {r['k']} | {r['model']} | {r['p0_mean']} | {r['err_pct']} |\n")
print('rendered 09')
