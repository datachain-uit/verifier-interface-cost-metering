#!/usr/bin/env python3
# Generates configs/design-cells.csv from the frozen design (03-factors-and-configurations.md) and the npg levels file.
import csv, os, collections, sys
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRID = [1, 2, 4, 6, 8, 12, 16, 24, 32]; CTX = {1: 'c1_k01', **{k: f'c1_ctx_k{k:02d}' for k in GRID[1:] + [64]}}; PILOTK = {1, 2, 4, 16}
REG = {'evm-osaka': 'hardfork=osaka', 'eravm-29': 'protocol=29'}; rows = []
def add(cls, env, regime, b, circ, k, rel, role, camp):
    rows.append(dict(cell_id=f'{env}{"@" + regime if env == "zkos-v32" else ""}|{b}|{circ}', design_class=cls, campaign=camp, env=env, regime=regime, backend=b, circuit=circ, k=k, relation=rel, proofs='j0..j7', role=role))
for env in ('evm-osaka', 'eravm-29', 'zkos-v32'):
    for b in ('groth16', 'plonk'):
        for k in GRID + [64]:
            role = 'LIMIT-CHECK' if k == 64 else ('CALIBRATION' if (k in (1, 4) and env != 'zkos-v32') or (k == 1 and env == 'zkos-v32') else 'HELD-OUT-k')
            add('CORE', env, REG.get(env, 'npg100'), b, CTX[k], k, 'ctx', role, 'PILOT' if k in PILOTK else 'FULL')
for r in csv.DictReader(open(os.path.join(PKG, '09-numeric-predictions', 'zkos_npg_levels.csv'))):
    k, npg = int(r['k']), int(r['npg'])
    if npg == 100: continue
    for b in ('groth16', 'plonk'): add('CORE-INTERVENTION', 'zkos-v32', f'npg{npg}', b, CTX[k], k, 'ctx', 'INTERVENTION (' + r['purpose'] + ')', 'PILOT' if k == 1 else 'FULL')
for b in ('groth16', 'plonk'): add('CORE-ROBUSTNESS', 'zkos-v32', 'npg100+priority_fee=1e8wei', b, 'c1_k01', 1, 'ctx', 'ROBUSTNESS (tx-gas-price route)', 'FULL')
for b in ('groth16', 'plonk'):
    for k in (1, 4, 6, 8, 16): add('VALIDATION', 'eravm-27', 'protocol=27', b, CTX[k], k, 'ctx', 'CALIBRATION' if k == 1 else 'HELD-OUT-REGIME', 'FULL')
    for env in ('evm-osaka', 'eravm-29', 'zkos-v32'):
        for circ, k, rel in (('c1_a4', 4, 'a4'), ('c1_a8', 8, 'a8'), ('c1_disc_k04', 4, 'disc')): add('VALIDATION', env, REG.get(env, 'npg100'), b, circ, k, rel, 'SEMANTIC', 'FULL')
for env in ('evm-osaka', 'eravm-29', 'zkos-v32'):
    for k in (1, 4, 16, 32): add('VALIDATION-CONDITIONAL', env, REG.get(env, 'npg100'), 'fflonk', f'c1_ff_k{k:02d}', k, 'ctx', 'HELD-OUT-BACKEND', 'FULL-IF-FFLONK-GATE-PASSES')
for b in ('groth16', 'plonk'):
    for k in (1, 4, 16): add('SUPPORTING', 'evm-petersburg', 'hardfork=petersburg', b, CTX[k], k, 'ctx', 'CONTROL (specified; not scheduled)', 'NOT-SCHEDULED')
w = csv.DictWriter(open(os.path.join(PKG, 'configs', 'design-cells.csv'), 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), dict(collections.Counter((r['design_class'], r['campaign']) for r in rows)))
