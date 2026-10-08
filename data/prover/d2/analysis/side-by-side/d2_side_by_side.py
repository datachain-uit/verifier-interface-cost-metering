#!/usr/bin/env python3
"""V2-PRV-D2-01 side-by-side tables (presentation only; no new estimator): joins the frozen Host-A outputs (V2-PRV-D3-01,
D3-*.csv) and the frozen Host-B outputs (d2_analysis.py run, D2-*.csv) row by row. Every value is copied from those
tables. Allocation semantics (header of every table): cpu2 / cpu4 / cpu8 are resource ALLOCATIONS on ONE host each —
Host A: Apple M5 MacBook Pro, Docker Desktop VM, linux/arm64, VM-vCPU cpusets 1-2 / 1-4 / 1-8; Host B: workstation,
2 x Xeon Platinum 8173M, native Docker Engine, linux/amd64, cpusets 1-2 / 1-4 / 1-8 (one hardware thread per physical core,
NUMA node 0, SMT siblings excluded). Hosts are never pooled; no architecture or population claim. PLONK n = 5 (coarse).
usage: d2_side_by_side.py <D3 out dir> <D2 run dir> <out dir>"""
import csv, os, sys
A_DIR, B_DIR, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
HDR = ('# allocations on one host each (Host A: Apple M5, Docker Desktop VM, arm64; Host B: 2x Xeon 8173M, native Docker, amd64; '
       'cpusets 1-2/1-4/1-8); side by side, never pooled; values copied from the frozen D3 / D2 outputs; PLONK n = 5 coarse\n')
def rd(p): return list(csv.DictReader(open(p, newline='')))
def write(name, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        f.write(HDR); w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
def join(fa, fb, key, keep, name):
    A = {key(r): r for r in rd(os.path.join(A_DIR, fa))}; B = {key(r): r for r in rd(os.path.join(B_DIR, fb))}
    assert set(A) == set(B), (name, len(set(A) ^ set(B)))
    rows = []
    for k in sorted(A, key=lambda x: tuple(str(v).zfill(3) if str(v).isdigit() else str(v) for v in x)):
        row = dict(zip(key.names, k))
        for c in keep: row[f'hostA_{c}'] = A[k][c]; row[f'hostB_{c}'] = B[k][c]
        rows.append(row)
    write(name, rows); return len(rows)
class K:
    def __init__(self, *names): self.names = names
    def __call__(self, r): return tuple(r[n] for n in self.names)
n = {}
n['side-by-side-cell-stats.csv'] = join('D3-cell-stats.csv', 'D2-cell-stats.csv', K('allocation_profile', 'backend', 'depth', 'rounds', 'stage'),
    ['n', 'median', 'q1', 'q3', 'iqr', 'cv', 'min', 'max', 'boot_median_lo95', 'boot_median_hi95', 'precision'], 'side-by-side-cell-stats.csv')
n['side-by-side-backend-ratios.csv'] = join('D3-backend-ratios.csv', 'D2-backend-ratios.csv', K('allocation_profile', 'depth', 'stage'),
    ['median', 'min', 'max', 'cv', 'boot_median_lo95', 'boot_median_hi95'], 'side-by-side-backend-ratios.csv')
n['side-by-side-allocation-speedups.csv'] = join('D3-allocation-speedups.csv', 'D2-allocation-speedups.csv', K('backend', 'stage', 'depth', 'allocation_from', 'allocation_to'),
    ['median', 'min', 'max', 'boot_median_lo95', 'boot_median_hi95'], 'side-by-side-allocation-speedups.csv')
n['side-by-side-zkey-diagnostic.csv'] = join('D3-zkey-diagnostic.csv', 'D2-zkey-diagnostic.csv', K('allocation_profile', 'backend', 'depth', 'quantity'),
    ['n', 'median', 'iqr', 'cv', 'boot_median_lo95', 'boot_median_hi95'], 'side-by-side-zkey-diagnostic.csv')
print(n)
