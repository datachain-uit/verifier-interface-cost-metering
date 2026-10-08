#!/usr/bin/env python3
"""V2-PRV-D1-01 pre-specified analysis (frozen with the protocol; run once after the timed campaign). Descriptive only.

usage: python3 d1_analysis.py <V2-PRV-D1-01 evidence dir> <out dir>
Accepted rows: raw/primary-rXX-aN.csv of the accepted attempt (ledger status complete) for rounds 1..20; round 0 (warm-up)
and the dry run are excluded. Every row must be a valid proof with the matching root; otherwise the script aborts.
Per round r (same container): R_pad,b(r) = prove_ms(b, pad-above) / prove_ms(b, pad-below);
R_anchor,b(r) = prove_ms(b, d11) / prove_ms(b, d10); also for witness_ms and wall_ms.
Reported per backend: per-round values, median, min-max, CV, 95 % percentile-bootstrap interval of the median
(B = 10,000, seed int(sha256("20261004|D1|" + key)[:16], 16)), and the share of the anchor step reproduced by the
padding contrast: (median R_pad - 1) / (median R_anchor - 1). No decision threshold.
Reading guide fixed in advance: if the PLONK step d10 -> d11 is caused by the domain doubling, PLONK R_pad is close to
PLONK R_anchor while Groth16 R_pad stays close to 1 (the Groth16 domain is 2^12 in every cell); if it is caused by the
additional Merkle level, PLONK R_pad stays close to 1.
"""
import csv, glob, hashlib, json, math, os, random, statistics, sys
EV, OUT = sys.argv[1:3]; os.makedirs(OUT, exist_ok=True); B = 10_000
def q(s, p): pos = (len(s) - 1) * p; lo, hi = math.floor(pos), math.ceil(pos); return s[lo] + (s[hi] - s[lo]) * (pos - lo)
def boot(v, key):
    rng = random.Random(int(hashlib.sha256(f'20261004|D1|{key}'.encode()).hexdigest()[:16], 16))
    m = sorted(q(sorted(rng.choice(v) for _ in v), 0.5) for _ in range(B)); return q(m, 0.025), q(m, 0.975)
led = list(csv.DictReader(open(os.path.join(EV, 'ledger.csv'))))
acc = {int(l['round']): int(l['attempt']) for l in led if l['kind'] == 'primary' and l['status'] == 'complete'}
assert all(r in acc for r in range(0, 21)), 'campaign incomplete'
V = {}
for r in range(1, 21):
    rows = list(csv.DictReader(open(os.path.join(EV, 'raw', f'primary-r{r:02d}-a{acc[r]}.csv'))))
    assert len(rows) == 8 and all(x['proof_valid'] == '1' and x['root_matches'] == '1' for x in rows), f'round {r}'
    for x in rows: V[(x['backend'], x['cell'], r)] = {k: float(x[k]) for k in ('witness_ms', 'prove_ms', 'verify_ms', 'wall_ms')}
res = []
for b in ('groth16', 'plonk'):
    for st in ('prove_ms', 'witness_ms', 'wall_ms'):
        for name, hi, lo in (('pad-above/pad-below', 'p1180', 'p1150'), ('d11/d10', 'd11', 'd10'), ('pad-below/d10', 'p1150', 'd10'), ('d11/pad-above', 'd11', 'p1180')):
            v = [V[(b, hi, r)][st] / V[(b, lo, r)][st] for r in range(1, 21)]; s = sorted(v); lo95, hi95 = boot(v, f'{b}|{st}|{name}')
            res.append(dict(backend=b, stage=st, ratio=name, n=len(v), median=q(s, 0.5), min=s[0], max=s[-1], cv=statistics.stdev(v) / statistics.fmean(v), boot_median_lo95=lo95, boot_median_hi95=hi95,
                            **{f'r{r}': x for r, x in zip(range(1, 21), v)}))
with open(os.path.join(OUT, 'D1-ratios.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
cells = []
for b in ('groth16', 'plonk'):
    for c in ('d10', 'p1150', 'p1180', 'd11'):
        for st in ('witness_ms', 'prove_ms', 'verify_ms', 'wall_ms'):
            v = [V[(b, c, r)][st] for r in range(1, 21)]; s = sorted(v); lo95, hi95 = boot(v, f'cell|{b}|{c}|{st}')
            cells.append(dict(backend=b, cell=c, stage=st, n=20, median=q(s, 0.5), q1=q(s, 0.25), q3=q(s, 0.75), min=s[0], max=s[-1], cv=statistics.stdev(v) / statistics.fmean(v), boot_median_lo95=lo95, boot_median_hi95=hi95))
with open(os.path.join(OUT, 'D1-cells.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(cells[0].keys())); w.writeheader(); w.writerows(cells)
get = lambda b, st, n: next(x for x in res if x['backend'] == b and x['stage'] == st and x['ratio'] == n)
share = {b: (get(b, 'prove_ms', 'pad-above/pad-below')['median'] - 1) / (get(b, 'prove_ms', 'd11/d10')['median'] - 1) for b in ('groth16', 'plonk')}
json.dump(dict(primary_contrast={b: get(b, 'prove_ms', 'pad-above/pad-below') for b in ('groth16', 'plonk')}, anchor_step={b: get(b, 'prove_ms', 'd11/d10') for b in ('groth16', 'plonk')},
               share_of_anchor_step_reproduced=share), open(os.path.join(OUT, 'D1-summary.json'), 'w'), indent=1, default=float)
print(json.dumps(share))
