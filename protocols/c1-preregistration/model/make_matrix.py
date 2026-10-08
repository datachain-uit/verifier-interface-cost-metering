#!/usr/bin/env python3
# Builds 08-calibration-heldout-matrix.csv: one row per (design cell, metric) with its frozen role.
import csv, os, sys
PKG = sys.argv[1]; cells = list(csv.DictReader(open(os.path.join(PKG, 'configs', 'design-cells.csv')))); rows = []
SEEN = {2, 16, 32}; UNSEEN = {6, 8, 12, 24}
for c in cells:
    k = int(c['k']); env = c['env']; b = c['backend']; cls = c['design_class']
    def add(metric, role, test, uses):
        rows.append(dict(cell_id=c['cell_id'], metric=metric, design_class=cls, campaign=c['campaign'], k=k, role=role, scored_by=test, calibration_inputs_allowed=uses))
    if cls == 'SUPPORTING':
        add('Y_dir', 'SUPPORTING-CONTROL', 'L1-PETERSBURG (accounting); descriptive crossover', 'own k=1,4 cells'); continue
    if b == 'fflonk':
        add('N_dir' if env == 'zkos-v32' else 'Y_dir', 'HELD-OUT-BACKEND' if env == 'zkos-v32' else 'DESCRIPTIVE (FFLONK rank)', 'H8 / ZC' if env == 'zkos-v32' else 'descriptive', 'none from FFLONK; base,c from G16+PLONK k=1'); continue
    if c['relation'] != 'ctx':
        for m in (['Y_dir', 'N_dir'] if env == 'zkos-v32' else ['Y_dir', 'Y_app']): add(m, 'SEMANTIC', 'H6 (SEM) + P/R/ZC as held-out', 'none (compared with ctx at same k)')
        continue
    if cls.startswith('CORE-INTERVENTION') or cls.startswith('CORE-ROBUSTNESS'):
        add('Y_dir', 'HELD-OUT-REGIME/INTERVENTION', 'H5 (NPG): binding meter, gas interval, ranking', 'native from npg100 cells is NOT used; prediction from frozen files'); add('N_dir', 'INVARIANCE-CHECK', 'native independent of npg (equal to npg100 cell per proof)', '-'); continue
    if k == 64:
        for m in (['Y_dir', 'N_dir'] if env == 'zkos-v32' else ['Y_dir', 'Y_app']): add(m, 'LIMIT-CHECK', 'descriptive only', '-')
        continue
    if env == 'eravm-27':
        add('Y_dir', 'CALIBRATION' if k == 1 else 'HELD-OUT-REGIME', 'H7 (R v27 transfer, XO, SG)', 'v27 k=1 cell + v29 B + frame difference'); add('Y_app', 'CALIBRATION' if k == 1 else 'HELD-OUT-REGIME', 'secondary', 'same'); continue
    if env == 'zkos-v32':
        add('N_dir', 'CALIBRATION (base, c)' if k == 1 else 'HELD-OUT-k', 'H4 (ZC conditional) + P', 'k=1 G16+PLONK only')
        add('Y_dir', 'CALIBRATION' if k == 1 else 'HELD-OUT-k', 'H2 (SG, XO at npg100), P', 'via N and EVM gas'); continue
    for m in ('Y_dir', 'Y_app'):
        role = 'CALIBRATION' if k in (1, 4) else ('HELD-OUT-k/seen-in-P0' if k in SEEN else 'HELD-OUT-k/strictly-unseen')
        add(m, role, ('H1-H3 (R, SG, XO), P' if m == 'Y_dir' else 'secondary (R, P)'), 'own k=1,4 cells')
w = csv.DictWriter(open(os.path.join(PKG, '08-calibration-heldout-matrix.csv'), 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import collections; print(len(rows), dict(collections.Counter(r['role'] for r in rows)))
