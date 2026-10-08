#!/usr/bin/env python3
"""V2-PRV-D2-01 d2_analysis.py (v1.0) — Host-B statistics of the timed D2 campaign: the D3 computations (V2-PRV-D3-01
script v1.1, d3_reanalysis.py sha256 94c3ad06fcf027ca3e6c0a1155e40c97286e1de3db40e08a3577b512a64f0f21) with Host-B paths
and an input manifest of the frozen Host-B evidence; nothing else changed (D2-PREREGISTRATION.md §6). Hash-frozen before
the first timed round.

Host B = the workstation (2 x Xeon Platinum 8173M, native Docker Engine, linux/amd64); cpu2 / cpu4 / cpu8 are three
resource ALLOCATIONS (cpusets 1-2 / 1-4 / 1-8, NUMA node 0, SMT siblings excluded) on ONE host; never devices. Host A values
are the V2-PRV-D3-01 outputs; the hosts are reported side by side and never pooled.

usage: python3 d2_analysis.py --campaign <frozen campaign dir> --manifest <SHA256SUMS of the frozen evidence> --out <dir> --mode check|run

  --manifest: sha256sum-format list whose paths are relative to the manifest's directory; every input file below must be
              listed there with the same hash (the input manifest of the frozen Host-B evidence).
  check : verify the inputs against the manifest and the campaign identity (mode campaign, kit v3-x86, Host-A schedule and
          execution plan), then reconcile the campaign's own derived tables against the raw accepted rows. Writes
          D2-input-verification.json and D2-reconciliation.json. No statistics.
  run   : check, then the statistics (run once). Any input or identity mismatch aborts; reconciliation mismatches are
          reported, never repaired, and all statistics are computed from the RAW accepted rows only.

Definitions: identical to D3 v1.1 (accepted measured rows, rounds, type-7 quantiles, CV, percentile bootstrap of the
median with B = 10,000, within-round PLONK/Groth16 ratios, within-round allocation speedups, zkey diagnostic), except the
bootstrap seed per quantity = int(sha256(f"{BASE_SEED}|D2|{key}")[:16], 16), BASE_SEED = 20261004 (D2-PREREGISTRATION §6).
The V1 manuscript table prover_per_round.csv has no Host-B counterpart, so its reconciliation is omitted; the campaign's
own derived/prover_summary.csv and derived/prover_diag.csv are reconciled as in D3.
Stdlib only.
"""
import argparse, csv, hashlib, json, math, os, random, statistics, sys, datetime, collections

BASE_SEED = 20261004
B = 10_000
PROFILES = ['cpu2', 'cpu4', 'cpu8']
DEPTHS = list(range(5, 16))
STAGES = ['input_ms', 'witness_ms', 'prove_ms', 'verify_first_ms', 'verify_steady_ms', 'wall_ms', 'stage_sum_ms']
TRUE = ('1', 'true')   # raw tables encode booleans as 1 (as in D3 v1.1)
HOST_A_SCHEDULE_SHA256 = 'f7e6de3bbd1c9d24b0c41909414014c4e9cd1ee2ff2179c845aec8b9464fbb95'   # campaign-20260925T060607Z
HOST_A_PLAN_SHA256 = '99fb360ccb801606ee13a7aa03705522aceb5845a0d62affd647d9a2b0badc94'
INPUTS = (['CAMPAIGN.json'] + [f'prover/{p}/{f}.csv' for f in ('runs', 'diag', 'rounds') for p in PROFILES]
          + ['prover/round_ledger.csv', 'derived/prover_summary.csv', 'derived/prover_diag.csv'])


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


def seed_for(key): return int(hashlib.sha256(f'{BASE_SEED}|D2|{key}'.encode()).hexdigest()[:16], 16)


def boot_median(vals, key):
    rng = random.Random(seed_for(key)); n = len(vals)
    meds = sorted(quantile(sorted(rng.choice(vals) for _ in range(n)), 0.5) for _ in range(B))
    return quantile(meds, 0.025), quantile(meds, 0.975), seed_for(key)


def read_manifest(manifest):
    base = os.path.dirname(os.path.abspath(manifest)); m = {}
    for line in open(manifest):
        line = line.rstrip('\n')
        if not line.strip(): continue
        h, rel = line.split(None, 1); m[os.path.normpath(os.path.join(base, rel.lstrip('*')))] = h
    return m


def verify_inputs(camp, manifest):
    m = read_manifest(manifest); res = []
    for rel in INPUTS:
        p = os.path.normpath(os.path.abspath(os.path.join(camp, rel))); exp = m.get(p); got = sha(p) if os.path.exists(p) else None
        res.append(dict(path=rel, expected=exp, actual=got, ok=(exp is not None and got == exp)))
    return res


def verify_identity(camp):
    c = json.load(open(os.path.join(camp, 'CAMPAIGN.json')))
    checks = dict(mode_campaign=c.get('mode') == 'campaign', kit_v3_x86=c.get('kit') == 'v3-x86',
                  schedule_equals_host_a=c.get('schedule_sha256') == HOST_A_SCHEDULE_SHA256,
                  execution_plan_equals_host_a=c.get('execution_plan_sha256') == HOST_A_PLAN_SHA256)
    return dict(campaign_id=c.get('campaign_id'), mode=c.get('mode'), kit=c.get('kit'), schedule_sha256=c.get('schedule_sha256'),
                execution_plan_sha256=c.get('execution_plan_sha256'), checks=checks, ok=all(checks.values()))


def load_raw(camp):
    led = rcsv(os.path.join(camp, 'prover/round_ledger.csv'))
    acc = {(l['kind'], int(l['round'])): int(l['round_attempt']) for l in led if l['status'] == 'complete' and l['accepted'] == '1'}
    rows, diag = [], []
    for p in PROFILES:
        for r in rcsv(os.path.join(camp, f'prover/{p}/runs.csv')):
            if r['kind'] != 'primary' or r['is_warmup'] != '0' or r['status'] != 'ok': continue
            rnd, att = int(r['round']), int(r['round_attempt'])
            if acc.get(('primary', rnd)) != att: continue
            if r['proof_valid'] not in TRUE or r['root_matches'] not in TRUE: raise SystemExit(f'invalid proof row {p} {r["run_id"]}')
            rows.append(dict(profile=p, backend=r['backend'], depth=int(r['depth']), round=rnd, **{s: float(r[s]) for s in STAGES}))
        for r in rcsv(os.path.join(camp, f'prover/{p}/diag.csv')):
            rnd, att = int(r['diag_round']), int(r['round_attempt'])
            if r['status'] != 'ok' or acc.get(('diag', rnd)) != att: continue
            if r['proof_valid'] not in TRUE or r['root_matches'] not in TRUE: raise SystemExit(f'invalid diag row {p} round {rnd}')
            diag.append(dict(profile=p, backend=r['backend'], depth=int(r['depth']), round=rnd, call=r['call'], prove_ms=float(r['prove_ms']),
                             zkey_readfile_ms=(float(r['zkey_readfile_ms']) if r['zkey_readfile_ms'] not in ('', None) else None)))
    return rows, diag, acc


def reconcile(camp, rows, diag):
    out = dict(prover_summary=collections.Counter(), prover_diag=collections.Counter(), mismatches=[])   # no Host-B prover_per_round table
    V = {(r['profile'], r['backend'], r['depth'], r['round']): r for r in rows}
    close = lambda a, b: abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))
    for s in rcsv(os.path.join(camp, 'derived/prover_summary.csv')):
        rnds = [int(x) for x in s['rounds_used'].split()]
        vals = [V[(s['profile_id'], s['backend'], int(s['depth']), r)][s['metric']] for r in rnds]
        t = describe(vals); bad = [k for k in ('n', 'median', 'q1', 'q3', 'iqr', 'min', 'max') if not close(float(s[k]), float(t[k]))]
        out['prover_summary']['match' if not bad else 'MISMATCH'] += 1
        if bad: out['mismatches'].append(dict(table='prover_summary', row=s, fields=bad))
    D = collections.defaultdict(list)
    for r in diag: D[(r['profile'], r['backend'], r['depth'], r['call'])].append(r)
    for s in rcsv(os.path.join(camp, 'derived/prover_diag.csv')):
        rs = D[(s['profile_id'], s['backend'], int(s['depth']), s['call'])]
        mp = describe([r['prove_ms'] for r in rs])['median']; rf = [r['zkey_readfile_ms'] for r in rs if r['zkey_readfile_ms'] is not None]
        mr = describe(rf)['median'] if rf else None
        ok = int(s['n']) == len(rs) and close(float(s['median_prove_ms']), mp) and ((s['median_zkey_readfile_ms'] in ('', None) and mr is None) or (mr is not None and close(float(s['median_zkey_readfile_ms']), mr)))
        out['prover_diag']['match' if ok else 'MISMATCH'] += 1
        if not ok: out['mismatches'].append(dict(table='prover_diag', row=s, recomputed=dict(n=len(rs), median_prove_ms=mp, median_zkey_readfile_ms=mr)))
    for k in ('prover_summary', 'prover_diag'): out[k] = dict(out[k])
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
    wcsv(os.path.join(out, 'D2-cell-stats.csv'), cells)
    ratios = []
    for p in PROFILES:
        for d in DEPTHS:
            for st in ('prove_ms', 'wall_ms'):
                per = [V[(p, 'plonk', d, r)][st] / V[(p, 'groth16', d, r)][st] for r in R5]; t = describe(per)
                lo, hi, sd_ = boot_median(per, f'ratio|{p}|{d}|{st}')
                ratios.append(dict(allocation_profile=p, depth=d, stage=st, quantity='PLONK/Groth16 within round', **{f'r{r}': x for r, x in zip(R5, per)}, median=t['median'], min=t['min'], max=t['max'], cv=t['cv'],
                                   boot_median_lo95=lo, boot_median_hi95=hi, bootstrap_seed=sd_, precision='COARSE (n = 5)'))
    wcsv(os.path.join(out, 'D2-backend-ratios.csv'), ratios)
    speed = []
    for b in ('groth16', 'plonk'):
        for st in STAGES:
            for d in DEPTHS:
                for a, c in (('cpu2', 'cpu4'), ('cpu4', 'cpu8'), ('cpu2', 'cpu8')):
                    per = [V[(a, b, d, r)][st] / V[(c, b, d, r)][st] for r in R5]; t = describe(per)
                    lo, hi, sd_ = boot_median(per, f'speedup|{b}|{st}|{d}|{a}|{c}')
                    speed.append(dict(backend=b, stage=st, depth=d, allocation_from=a, allocation_to=c, quantity='within-round time ratio (from / to)', **{f'r{r}': x for r, x in zip(R5, per)},
                                      median=t['median'], min=t['min'], max=t['max'], boot_median_lo95=lo, boot_median_hi95=hi, bootstrap_seed=sd_, precision='COARSE (n = 5)'))
    wcsv(os.path.join(out, 'D2-allocation-speedups.csv'), speed)
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
    wcsv(os.path.join(out, 'D2-zkey-diagnostic.csv'), zk)
    return dict(cells=len(cells), ratios=len(ratios), speedups=len(speed), zkey=len(zk))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--campaign', required=True); ap.add_argument('--manifest', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--mode', choices=['check', 'run'], required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    started = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    ver = verify_inputs(a.campaign, a.manifest); ident = verify_identity(a.campaign) if os.path.exists(os.path.join(a.campaign, 'CAMPAIGN.json')) else dict(ok=False, checks={})
    json.dump(dict(manifest=os.path.abspath(a.manifest), manifest_sha256=sha(a.manifest), inputs=ver, identity=ident), open(os.path.join(a.out, 'D2-input-verification.json'), 'w'), indent=1)
    if not all(v['ok'] for v in ver): print('INPUT MANIFEST MISMATCH — abort'); [print(v) for v in ver if not v['ok']]; sys.exit(3)
    if not ident['ok']: print('CAMPAIGN IDENTITY MISMATCH — abort', ident); sys.exit(4)
    rows, diag, acc = load_raw(a.campaign)
    exp_rows = 3 * (11 * 10 + 11 * 5); exp_diag = 3 * 5 * 8 * 2
    if len(rows) != exp_rows or len(diag) != exp_diag: raise SystemExit(f'unexpected row counts {len(rows)} / {len(diag)} (expected {exp_rows} / {exp_diag})')
    rec = reconcile(a.campaign, rows, diag); json.dump(rec, open(os.path.join(a.out, 'D2-reconciliation.json'), 'w'), indent=1, default=str)
    print('inputs OK; identity OK; accepted rows', len(rows), 'diag rows', len(diag), '; reconciliation', {k: rec[k] for k in ('prover_summary', 'prover_diag')}, 'mismatches', len(rec['mismatches']))
    record = dict(campaign_id='V2-PRV-D2-01', source_campaign=ident['campaign_id'], mode=a.mode, started_utc=started, script_sha256=sha(os.path.abspath(__file__)), manifest_sha256=sha(a.manifest),
                  base_seed=BASE_SEED, seed_namespace='D2', bootstrap_resamples=B, python=sys.version.split()[0], accepted_rows=len(rows), diag_rows=len(diag),
                  accepted_attempts={f'{k[0]}:{k[1]}': v for k, v in sorted(acc.items())},
                  reconciliation={k: rec[k] for k in ('prover_summary', 'prover_diag')}, reconciliation_mismatches=len(rec['mismatches']),
                  note='Host B: cpu2/cpu4/cpu8 are allocations (cpusets 1-2/1-4/1-8, NUMA node 0) on one Xeon host, never devices; PLONK n = 5 intervals are coarse; Host A = V2-PRV-D3-01 outputs, side by side, never pooled')
    if a.mode == 'run':
        record['outputs'] = stats(rows, diag, a.out)
    record['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    json.dump(record, open(os.path.join(a.out, f'D2-{a.mode.upper()}-RECORD.json'), 'w'), indent=1)
    print(json.dumps(record.get('outputs', {})))


if __name__ == '__main__':
    main()
