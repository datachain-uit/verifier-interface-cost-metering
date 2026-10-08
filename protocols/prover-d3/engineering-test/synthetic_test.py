# Engineering test of d3_reanalysis.py on SYNTHETIC data with the real schema (no real values used).
import os, sys, csv, json, random, hashlib, importlib.util, statistics
T = '/root/d3/test/root'; C = os.path.join(T, 'research/results/postcorr-20260925'); os.makedirs(C + '/derived', exist_ok=True)
rng = random.Random(1)
STAGES = ['input_ms', 'witness_ms', 'prove_ms', 'verify_first_ms', 'verify_steady_ms', 'wall_ms', 'stage_sum_ms']
hdr_runs = ['campaign_id','session_id','profile_id','container_id','kind','run_id','round','round_attempt','order_in_round','seed','is_warmup','warmup_kind','backend','depth','leaf_index','started_at_utc'] + STAGES[:-2] + ['stage_sum_ms','wall_ms','zkey_bytes','zkey_sha256','proof_valid','root_matches','input_matches_committed','public_root','expected_root','heap_used_mb','rss_mb','image_id','manifest_sha256','status','error']
raw = {}
for p, f in (('cpu2', 1.0), ('cpu4', 0.6), ('cpu8', 0.4)):
    os.makedirs(f'{C}/prover/{p}', exist_ok=True); rows = []
    for rnd in range(0, 11):
        for b in ('groth16', 'plonk'):
            if b == 'plonk' and rnd > 5: continue
            for d in range(5, 16):
                base = (300 if b == 'groth16' else 20000) * (1.1 ** (d - 5)) * f
                v = {s: round(base * rng.uniform(0.95, 1.05) * (0.1 if s != 'prove_ms' else 1), 3) for s in STAGES}
                rows.append(dict(kind='primary', run_id=f'{p}-{rnd}-{b}-{d}', round=rnd, round_attempt=1, is_warmup=('1' if rnd == 0 else '0'), warmup_kind=('round0' if rnd == 0 else ''), backend=b, depth=d, proof_valid='1', root_matches='1', status='ok', **v))
                if rnd > 0: raw[(p, b, d, rnd)] = v
    rows.append(dict(kind='primary', run_id='w', round=1, round_attempt=1, is_warmup='1', warmup_kind='in_process', backend='groth16', depth=5, proof_valid='1', root_matches='1', status='ok', **{s: 1 for s in STAGES}))
    with open(f'{C}/prover/{p}/runs.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=hdr_runs, extrasaction='ignore'); w.writeheader(); [w.writerow({k: r.get(k, '') for k in hdr_runs}) for r in rows]
    drows = []
    for rnd in range(1, 6):
        for b, d in (('groth16', 5), ('groth16', 7), ('groth16', 8), ('groth16', 15), ('plonk', 5), ('plonk', 10), ('plonk', 11), ('plonk', 15)):
            for call in ('path', 'mem'):
                drows.append(dict(diag_round=rnd, round_attempt=1, backend=b, depth=d, call=call, prove_ms=round(rng.uniform(100, 200), 3), zkey_readfile_ms=(round(rng.uniform(1, 5), 3) if call == 'path' else ''), proof_valid='1', root_matches='1', status='ok'))
    with open(f'{C}/prover/{p}/diag.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(drows[0].keys())); w.writeheader(); w.writerows(drows)
    open(f'{C}/prover/{p}/rounds.csv', 'w').write('x\n')
with open(f'{C}/prover/round_ledger.csv', 'w') as fh:
    fh.write('kind,round,round_attempt,status,accepted\n'); [fh.write(f'primary,{r},1,complete,1\n') for r in range(0, 11)]; [fh.write(f'diag,{r},1,complete,1\n') for r in range(1, 6)]
open(f'{C}/CAMPAIGN.json', 'w').write('{}')
spec = importlib.util.spec_from_file_location('d3', '/root/d3/d3_reanalysis.py'); d3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(d3)
# derived tables consistent with raw (to exercise reconciliation)
summ = []
for p in ('cpu2','cpu4','cpu8'):
    for b, rs in (('groth16', list(range(1, 11))), ('plonk', [1,2,3,4,5])):
        for d in range(5, 16):
            for s in STAGES:
                t = d3.describe([raw[(p,b,d,r)][s] for r in rs]); summ.append(dict(campaign_id='x', profile_id=p, backend=b, depth=d, metric=s, rounds_used=' '.join(map(str, rs)), round_attempts_used='', n=t['n'], median=t['median'], q1=t['q1'], q3=t['q3'], iqr=t['iqr'], min=t['min'], max=t['max']))
summ[0]['median'] = 1.0   # injected mismatch -> must be reported
d3.wcsv(f'{C}/derived/prover_summary.csv', summ)
pdg = []
_, diag, _ = None, None, None
os.makedirs(os.path.join(T, 'research/submission/csi/generated'), exist_ok=True)
ppr = []
for p in ('cpu2','cpu4','cpu8'):
    for b, rs in (('groth16', list(range(1, 11))), ('plonk', [1,2,3,4,5])):
        for d in range(5, 16):
            for r in rs: ppr.append(dict(quantity='prove_ms', profile=p, backend=b, depth=d, round=r, value=raw[(p,b,d,r)]['prove_ms'], definition='x'))
d3.wcsv(os.path.join(T, 'research/submission/csi/generated/prover_per_round.csv'), ppr)
rows, diag, acc = d3.load_raw(T)
DG = {}
for r in diag: DG.setdefault((r['profile'], r['backend'], r['depth'], r['call']), []).append(r)
for (p, b, d, c), rs in DG.items():
    rf = [x['zkey_readfile_ms'] for x in rs if x['zkey_readfile_ms'] is not None]
    pdg.append(dict(campaign_id='x', profile_id=p, backend=b, depth=d, call=c, round_attempts_used='', n=len(rs), median_prove_ms=d3.describe([x['prove_ms'] for x in rs])['median'], median_zkey_readfile_ms=(d3.describe(rf)['median'] if rf else '')))
d3.wcsv(f'{C}/derived/prover_diag.csv', pdg)
d3.MANIFEST = {rel: d3.sha(os.path.join(T, rel)) for rel in d3.MANIFEST}
d3.B = 500
sys.argv = ['d3', '--root', T, '--out', '/root/d3/test/out', '--mode', 'run']; d3.main()
rec = json.load(open('/root/d3/test/out/D3-reconciliation.json')); print('mismatches reported:', len(rec['mismatches']), rec['mismatches'][0]['fields'] if rec['mismatches'] else None)
import glob; [print(f, sum(1 for _ in open(f)) - 1) for f in sorted(glob.glob('/root/d3/test/out/*.csv'))]
c = list(csv.DictReader(open('/root/d3/test/out/D3-cell-stats.csv'))); print(c[0])
