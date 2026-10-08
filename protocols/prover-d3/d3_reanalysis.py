#!/usr/bin/env python3
"""V2-PRV-D3-01 (script v1.1) — statistics re-analysis of the frozen V1 prover campaign (no new runs, no new timing).

Source campaign: campaign-20260925T060607Z (V1 protocol v3; Apple M5 MacBook Pro, Docker Desktop VM, linux/arm64).
cpu2 / cpu4 / cpu8 are three resource ALLOCATIONS (VM-vCPU cpusets 1-2 / 1-4 / 1-8 with matched ffjavascript workers) on
ONE host; they are never treated as devices.

usage: python3 d3_reanalysis.py --root <V2 workspace root> --out <output dir> --mode check|run

  check : verify every input against the frozen sha256 manifest below, then reconcile the V1 derived tables against the
          raw accepted rows. Writes D3-input-verification.json and D3-reconciliation.json. No statistics.
  run   : check, then the statistics (run once). Hash mismatch aborts; reconciliation mismatches are reported, never
          repaired, and all statistics are computed from the RAW accepted rows only.

Definitions (fixed before the run; protocol research/csi/protocols/v2/prover-D3/D3-PROTOCOL.md):
  accepted measured row  : runs.csv kind=primary, is_warmup=0, status=ok, round_attempt = the accepted attempt of that
                           round in prover/round_ledger.csv (complete, accepted=1), proof_valid and root_matches true.
  rounds                 : PLONK rounds 1-5 (n = 5, labelled COARSE); Groth16 rounds 1-10 (n = 10) and, separately,
                           rounds 1-5 (n = 5). Cross-backend and cross-allocation quantities use rounds 1-5 only (v3 §3.3).
  quantiles              : linear interpolation between order statistics (type 7; identical to the V1 harness).
  CV                     : sample standard deviation (n - 1) / mean.
  bootstrap              : percentile bootstrap of the median, B = 10,000 resamples of the per-round values with
                           replacement, 95 % interval = 2.5th and 97.5th percentiles (type 7) of the resampled medians.
                           Seed per quantity = int(sha256(f"{BASE_SEED}|{key}")[:16], 16), BASE_SEED = 20261004.
  ratio PLONK/Groth16    : per round r in 1-5, same allocation and container: X_plonk,r(d) / X_groth16,r(d).
  allocation speedup     : per round r in 1-5: X_r(d; smaller allocation) / X_r(d; larger allocation) for
                           cpu2->cpu4, cpu4->cpu8, cpu2->cpu8 (pairs rounds; a value > 1 means faster with more vCPUs).
  zkey diagnostic        : per diag round 1-5 and (allocation, backend, depth): prove_ms with the key read from the file
                           path ('path') and with the key preloaded in memory ('mem'); difference path - mem.
Stdlib only.
"""
import argparse, csv, hashlib, json, math, os, random, statistics, sys, datetime, collections

BASE_SEED = 20261004
B = 10_000
PROFILES = ['cpu2', 'cpu4', 'cpu8']
DEPTHS = list(range(5, 16))
STAGES = ['input_ms', 'witness_ms', 'prove_ms', 'verify_first_ms', 'verify_steady_ms', 'wall_ms', 'stage_sum_ms']
CAMPAIGN = 'research/results/postcorr-20260925'
TRUE = ('1', 'true')   # V1 raw tables encode booleans as 1 (v1.1 fix, deviation DEV-D3-1)
MANIFEST = {
    f'{CAMPAIGN}/CAMPAIGN.json': '2f7aa7429902fc57565afeac34781df348e2c6729962fae3dd346ae1b5c39f30',
    f'{CAMPAIGN}/prover/cpu2/runs.csv': 'e20f4def6d96a23615c85a5daa7145a95d58002a6801891ead2a69b03a937e8a',
    f'{CAMPAIGN}/prover/cpu4/runs.csv': 'f0e5f134c08e440bfdd700f0917371c4976690d1200c5024a142919550f28b5c',
    f'{CAMPAIGN}/prover/cpu8/runs.csv': '917f10214dac0dbf713d6bef9327c49ae671aae03830b591e96104498ba63f24',
    f'{CAMPAIGN}/prover/cpu2/diag.csv': 'd653aaecf6e37d9b8776ac878e37ac96c113db42cf5fa20e1a01d6d90507ac88',
    f'{CAMPAIGN}/prover/cpu4/diag.csv': 'fd63b119f59c6414b33c0e9b71265dd93536a7d9bb2d3ab2e77d19b2d4e091a5',
    f'{CAMPAIGN}/prover/cpu8/diag.csv': '55e80397e56b7917aac190052dcc398f96bce26ac8437bed59b9320c55631477',
    f'{CAMPAIGN}/prover/cpu2/rounds.csv': '70604fc784c6aa1aafdca6ed1703ea2bc00c7e720c53f128101e18e15a4207f1',
    f'{CAMPAIGN}/prover/cpu4/rounds.csv': '331b7b5ed27c24a8208a5e11e844002a29d0b1a75f9d22b712c2a691986b3930',
    f'{CAMPAIGN}/prover/cpu8/rounds.csv': '690a58e01bf8d6867f68b7a38903d9c5cd8ad9964a69656009187ae4bf0f62f8',
    f'{CAMPAIGN}/prover/round_ledger.csv': '91f9d2ccb45bc1c572ead9a431d6da09c1f9cad9a0abdb56fbbd8229460d8162',
    f'{CAMPAIGN}/derived/prover_summary.csv': '7d047760b4bc80529e9f920cbaa46c3eb6cb4b343e97d599c32137d6008dd686',
    f'{CAMPAIGN}/derived/prover_diag.csv': '87a0cb5a38000a3645d7e17d054c3f06057c5d398f7f533c248243556796def6',
    'research/submission/csi/generated/prover_per_round.csv': '2ccd81f097a267f683d6e3f0b1b21c20cea38a28c3bb9a8ab28f6fa193375957',
}


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def rcsv(p): return list(csv.DictReader(open(p, newline='')))


def wcsv(p, rows):
    if not rows: return
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def quantile(sorted_vals, q):  # type 7, as lib/common.js
    pos = (len(sorted_vals) - 1) * q; lo, hi = math.floor(pos), math.ceil(pos)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def describe(vals):
    s = sorted(vals); n = len(s); mean = statistics.fmean(s); sd = statistics.stdev(s) if n > 1 else 0.0
    q1, med, q3 = quantile(s, 0.25), quantile(s, 0.5), quantile(s, 0.75)
    return dict(n=n, mean=mean, sd=sd, cv=(sd / mean if mean else None), median=med, q1=q1, q3=q3, iqr=q3 - q1, min=s[0], max=s[-1])


def seed_for(key): return int(hashlib.sha256(f'{BASE_SEED}|{key}'.encode()).hexdigest()[:16], 16)


def boot_median(vals, key):
    rng = random.Random(seed_for(key)); n = len(vals)
    meds = sorted(quantile(sorted(rng.choice(vals) for _ in range(n)), 0.5) for _ in range(B))
    return quantile(meds, 0.025), quantile(meds, 0.975), seed_for(key)


def verify_inputs(root):
    res = []
    for rel, exp in MANIFEST.items():
        p = os.path.join(root, rel); got = sha(p) if os.path.exists(p) else None
        res.append(dict(path=rel, expected=exp, actual=got, ok=(got == exp)))
    return res


def load_raw(root):
    led = rcsv(os.path.join(root, CAMPAIGN, 'prover/round_ledger.csv'))
    acc = {(l['kind'], int(l['round'])): int(l['round_attempt']) for l in led if l['status'] == 'complete' and l['accepted'] == '1'}
    rows, diag = [], []
    for p in PROFILES:
        for r in rcsv(os.path.join(root, CAMPAIGN, f'prover/{p}/runs.csv')):
            if r['kind'] != 'primary' or r['is_warmup'] != '0' or r['status'] != 'ok': continue
            rnd, att = int(r['round']), int(r['round_attempt'])
            if acc.get(('primary', rnd)) != att: continue
            if r['proof_valid'] not in TRUE or r['root_matches'] not in TRUE: raise SystemExit(f'invalid proof row {p} {r["run_id"]}')
            rows.append(dict(profile=p, backend=r['backend'], depth=int(r['depth']), round=rnd, **{s: float(r[s]) for s in STAGES}))
        for r in rcsv(os.path.join(root, CAMPAIGN, f'prover/{p}/diag.csv')):
            rnd, att = int(r['diag_round']), int(r['round_attempt'])
            if r['status'] != 'ok' or acc.get(('diag', rnd)) != att: continue
            if r['proof_valid'] not in TRUE or r['root_matches'] not in TRUE: raise SystemExit(f'invalid diag row {p} round {rnd}')
            diag.append(dict(profile=p, backend=r['backend'], depth=int(r['depth']), round=rnd, call=r['call'], prove_ms=float(r['prove_ms']),
                             zkey_readfile_ms=(float(r['zkey_readfile_ms']) if r['zkey_readfile_ms'] not in ('', None) else None)))
    return rows, diag, acc


def reconcile(root, rows, diag):
    out = dict(prover_per_round=collections.Counter(), prover_summary=collections.Counter(), prover_diag=collections.Counter(), mismatches=[])
    V = {(r['profile'], r['backend'], r['depth'], r['round']): r for r in rows}
    close = lambda a, b: abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))
    for q in rcsv(os.path.join(root, 'research/submission/csi/generated/prover_per_round.csv')):
        d, rnd, val = int(q['depth']), int(q['round']), float(q['value'])
        if q['quantity'] == 'prove_ms': ref = V[(q['profile'], q['backend'], d, rnd)]['prove_ms']
        elif q['quantity'] == 'norm_d5': ref = V[(q['profile'], q['backend'], d, rnd)]['prove_ms'] / V[(q['profile'], q['backend'], 5, rnd)]['prove_ms']
        elif q['quantity'] == 'plonk_minus_groth16_s': ref = (V[(q['profile'], 'plonk', d, rnd)]['prove_ms'] - V[(q['profile'], 'groth16', d, rnd)]['prove_ms']) / 1000
        elif q['quantity'] == 'gap_reduction_cpu2_to_cpu8_pct':
            g = lambda p: V[(p, 'plonk', d, rnd)]['prove_ms'] - V[(p, 'groth16', d, rnd)]['prove_ms']; ref = 100 * (1 - g('cpu8') / g('cpu2'))
        else: out['mismatches'].append(dict(table='prover_per_round', row=q, reason='unknown quantity')); continue
        ok = close(val, ref); out['prover_per_round']['match' if ok else 'MISMATCH'] += 1
        if not ok: out['mismatches'].append(dict(table='prover_per_round', row=q, recomputed=ref))
    for s in rcsv(os.path.join(root, CAMPAIGN, 'derived/prover_summary.csv')):
        rnds = [int(x) for x in s['rounds_used'].split()]
        vals = [V[(s['profile_id'], s['backend'], int(s['depth']), r)][s['metric']] for r in rnds]
        t = describe(vals); bad = [k for k in ('n', 'median', 'q1', 'q3', 'iqr', 'min', 'max') if not close(float(s[k]), float(t[k]))]
        out['prover_summary']['match' if not bad else 'MISMATCH'] += 1
        if bad: out['mismatches'].append(dict(table='prover_summary', row=s, fields=bad))
    D = collections.defaultdict(list)
    for r in diag: D[(r['profile'], r['backend'], r['depth'], r['call'])].append(r)
    for s in rcsv(os.path.join(root, CAMPAIGN, 'derived/prover_diag.csv')):
        rs = D[(s['profile_id'], s['backend'], int(s['depth']), s['call'])]
        mp = describe([r['prove_ms'] for r in rs])['median']; rf = [r['zkey_readfile_ms'] for r in rs if r['zkey_readfile_ms'] is not None]
        mr = describe(rf)['median'] if rf else None
        ok = int(s['n']) == len(rs) and close(float(s['median_prove_ms']), mp) and ((s['median_zkey_readfile_ms'] in ('', None) and mr is None) or (mr is not None and close(float(s['median_zkey_readfile_ms']), mr)))
        out['prover_diag']['match' if ok else 'MISMATCH'] += 1
        if not ok: out['mismatches'].append(dict(table='prover_diag', row=s, recomputed=dict(n=len(rs), median_prove_ms=mp, median_zkey_readfile_ms=mr)))
    for k in ('prover_per_round', 'prover_summary', 'prover_diag'): out[k] = dict(out[k])
    return out


def stats(rows, diag, out):
    V = {(r['profile'], r['backend'], r['depth'], r['round']): r for r in rows}
    R5, R10 = [1, 2, 3, 4, 5], list(range(1, 11))
    cells = []
    for p in PROFILES:
        for b, sets in (('groth16', [('1-10', R10), ('1-5', R5)]), ('plonk', [('1-5', R5)])):
            for d in DEPTHS:
                for label, rs in sets:
                    for st in STAGES:
                        vals = [V[(p, b, d, r)][st] for r in rs]; t = describe(vals); key = f'cell|{p}|{b}|{d}|{label}|{st}'
                        lo, hi, sd_ = boot_median(vals, key)
                        cells.append(dict(allocation_profile=p, backend=b, depth=d, rounds=label, stage=st, n=t['n'], mean=t['mean'], sd=t['sd'], cv=t['cv'], median=t['median'], q1=t['q1'], q3=t['q3'], iqr=t['iqr'],
                                          min=t['min'], max=t['max'], boot_median_lo95=lo, boot_median_hi95=hi, bootstrap_seed=sd_, precision=('COARSE (n = 5)' if t['n'] <= 5 else 'n = 10')))
    wcsv(os.path.join(out, 'D3-cell-stats.csv'), cells)
    ratios = []
    for p in PROFILES:
        for d in DEPTHS:
            for st in ('prove_ms', 'wall_ms'):
                per = [V[(p, 'plonk', d, r)][st] / V[(p, 'groth16', d, r)][st] for r in R5]; t = describe(per)
                lo, hi, sd_ = boot_median(per, f'ratio|{p}|{d}|{st}')
                ratios.append(dict(allocation_profile=p, depth=d, stage=st, quantity='PLONK/Groth16 within round', **{f'r{r}': x for r, x in zip(R5, per)}, median=t['median'], min=t['min'], max=t['max'], cv=t['cv'],
                                   boot_median_lo95=lo, boot_median_hi95=hi, bootstrap_seed=sd_, precision='COARSE (n = 5)'))
    wcsv(os.path.join(out, 'D3-backend-ratios.csv'), ratios)
    speed = []
    for b in ('groth16', 'plonk'):
        for st in STAGES:
            for d in DEPTHS:
                for a, c in (('cpu2', 'cpu4'), ('cpu4', 'cpu8'), ('cpu2', 'cpu8')):
                    per = [V[(a, b, d, r)][st] / V[(c, b, d, r)][st] for r in R5]; t = describe(per)
                    lo, hi, sd_ = boot_median(per, f'speedup|{b}|{st}|{d}|{a}|{c}')
                    speed.append(dict(backend=b, stage=st, depth=d, allocation_from=a, allocation_to=c, quantity='within-round time ratio (from / to)', **{f'r{r}': x for r, x in zip(R5, per)},
                                      median=t['median'], min=t['min'], max=t['max'], boot_median_lo95=lo, boot_median_hi95=hi, bootstrap_seed=sd_, precision='COARSE (n = 5)'))
    wcsv(os.path.join(out, 'D3-allocation-speedups.csv'), speed)
    Dg = collections.defaultdict(dict)
    for r in diag: Dg[(r['profile'], r['backend'], r['depth'], r['round'])][r['call']] = r
    zk = []
    for p in PROFILES:
        for (b, d) in sorted({(r['backend'], r['depth']) for r in diag}):
            rs = sorted(r for (pp, bb, dd, r) in Dg if (pp, bb, dd) == (p, b, d))
            path = [Dg[(p, b, d, r)]['path']['prove_ms'] for r in rs]; mem = [Dg[(p, b, d, r)]['mem']['prove_ms'] for r in rs]
            diff = [x - y for x, y in zip(path, mem)]; rf = [Dg[(p, b, d, r)]['path']['zkey_readfile_ms'] for r in rs]
            for name, vals in (('prove_ms_path', path), ('prove_ms_mem', mem), ('path_minus_mem_ms', diff), ('zkey_readfile_ms', [x for x in rf if x is not None])):
                if not vals: continue
                t = describe(vals); lo, hi, sd_ = boot_median(vals, f'zkey|{p}|{b}|{d}|{name}')
                zk.append(dict(allocation_profile=p, backend=b, depth=d, quantity=name, n=t['n'], median=t['median'], q1=t['q1'], q3=t['q3'], iqr=t['iqr'], min=t['min'], max=t['max'], cv=t['cv'],
                               boot_median_lo95=lo, boot_median_hi95=hi, bootstrap_seed=sd_, precision='COARSE (n = 5)'))
    wcsv(os.path.join(out, 'D3-zkey-diagnostic.csv'), zk)
    return dict(cells=len(cells), ratios=len(ratios), speedups=len(speed), zkey=len(zk))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); ap.add_argument('--out', required=True); ap.add_argument('--mode', choices=['check', 'run'], required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    started = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    ver = verify_inputs(a.root); json.dump(ver, open(os.path.join(a.out, 'D3-input-verification.json'), 'w'), indent=1)
    if not all(v['ok'] for v in ver): print('INPUT HASH MISMATCH — abort'); [print(v) for v in ver if not v['ok']]; sys.exit(3)
    rows, diag, acc = load_raw(a.root)
    exp_rows = 3 * (11 * 10 + 11 * 5); exp_diag = 3 * 5 * 8 * 2
    if len(rows) != exp_rows or len(diag) != exp_diag: raise SystemExit(f'unexpected row counts {len(rows)} / {len(diag)} (expected {exp_rows} / {exp_diag})')
    rec = reconcile(a.root, rows, diag); json.dump(rec, open(os.path.join(a.out, 'D3-reconciliation.json'), 'w'), indent=1, default=str)
    print('inputs OK; accepted rows', len(rows), 'diag rows', len(diag), '; reconciliation', {k: rec[k] for k in ('prover_per_round', 'prover_summary', 'prover_diag')}, 'mismatches', len(rec['mismatches']))
    record = dict(campaign_id='V2-PRV-D3-01', source_campaign='campaign-20260925T060607Z', mode=a.mode, started_utc=started, script_sha256=sha(os.path.abspath(__file__)), base_seed=BASE_SEED, bootstrap_resamples=B,
                  python=sys.version.split()[0], accepted_rows=len(rows), diag_rows=len(diag), accepted_attempts={f'{k[0]}:{k[1]}': v for k, v in sorted(acc.items())},
                  reconciliation={k: rec[k] for k in ('prover_per_round', 'prover_summary', 'prover_diag')}, reconciliation_mismatches=len(rec['mismatches']),
                  note='cpu2/cpu4/cpu8 are allocations on one Apple M5 host (VM-vCPU cpusets), never devices; PLONK n = 5 intervals are coarse')
    if a.mode == 'run':
        record['outputs'] = stats(rows, diag, a.out)
    record['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    json.dump(record, open(os.path.join(a.out, f'D3-{a.mode.upper()}-RECORD.json'), 'w'), indent=1)
    print(json.dumps(record.get('outputs', {})))


if __name__ == '__main__':
    main()
