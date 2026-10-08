#!/usr/bin/env python3
"""V2-C1 registered harness — evidence validation (before scoring; no scientific outcome is computed here).

usage: validate_evidence.py <evidence_root> <cells_csv> <campaign>
Checks: schema fields (18-evidence-schema.json required keys and enums); completeness (every scheduled cell, 8 distinct
proof IDs per measured op, every frozen control present); measurement statuses; replay = success and same metered
cost as the first submission of the same proof (17); version stamps recorded; artifact hashes constant within a cell.
Writes VALIDATION.json. It does not compare anything with predictions.
"""
import csv, json, os, sys, glob, collections
root, cells_csv, campaign = sys.argv[1:4]
schema = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evidence-schema.json')))
req = schema['required']; enums = {k: v['enum'] for k, v in schema['properties'].items() if 'enum' in v}
cells = [r for r in csv.DictReader(open(cells_csv)) if r['campaign'] == campaign]
recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(root, 'cells', '*.jsonl'))) for l in open(f) if l.strip()]
issues = []; by = collections.defaultdict(list)
for r in recs:
    for k in req:
        if k not in r: issues.append(f"missing field {k} in {r.get('circuit')}/{r.get('op')}")
    for k, allowed in enums.items():
        if k in r and r[k] not in allowed: issues.append(f"bad enum {k}={r[k]!r}")
    lbl = r['env'] + (f"@npg{r['regime']['npg']}" if r['env'] == 'zkos-v32' else '')
    by[(lbl, r['backend'], r['circuit'])].append(r)
summary = []
for c in cells:
    env = c['env'] + ('@' + c['regime'] if c['env'] == 'zkos-v32' else ''); key = (env, c['backend'], c['circuit']); R = by.get(key, []); k = int(c['k'])
    row = dict(cell_id=c['cell_id'], n_records=len(R))
    if not R: issues.append(f"MISSING cell {c['cell_id']}"); row['status'] = 'MISSING'; summary.append(row); continue
    for op in ('verify_credential', 'verify_proof_direct'):
        M = [r for r in R if r['op'] == op and r['role'] == 'measurement']
        ids = sorted(r['proof_id'] for r in M)
        if len(M) != 8 or len(set(ids)) != 8: issues.append(f"{c['cell_id']} {op}: {len(M)} measurement records / {len(set(ids))} distinct proofs")
        bad = [r['proof_id'] for r in M if r['status'] != 1]
        if bad: issues.append(f"{c['cell_id']} {op}: unexpected non-success {bad}")
        if c['env'] == 'evm-osaka' and op == 'verify_proof_direct' and any(not r.get('evm_trace') for r in M): issues.append(f"{c['cell_id']}: missing EDR trace")
        if c['env'].startswith('eravm') and op == 'verify_proof_direct' and any(not (r.get('eravm') or {}).get('frames') for r in M): issues.append(f"{c['cell_id']}: missing EraVM frames")
        if c['env'] == 'zkos-v32' and any(not r.get('zkos') or r['zkos'].get('computational_native') is None for r in M): issues.append(f"{c['cell_id']}: missing ZKsync OS native")
    ctrl = collections.Counter(r['control'] for r in R if r['control'])
    want = ['valid', 'tampered_proof', 'out_of_field_pub', 'replay', 'unknown_root_tx'] + [f'perturb_pub_{i}' for i in range(k)]
    for w in want:
        if ctrl.get(w, 0) < 1: issues.append(f"{c['cell_id']}: control {w} missing")
    if ctrl.get('cross_regime_identity', 0) != 8: issues.append(f"{c['cell_id']}: cross_regime_identity count {ctrl.get('cross_regime_identity', 0)}")
    first = {r['proof_id']: r for r in R if r['op'] == 'verify_proof_direct' and r['role'] == 'measurement'}
    for r in R:
        if r['control'] == 'replay':
            f = first.get(r['proof_id']); metric = lambda x: (x['eravm']['computational_gas'] if x.get('eravm') else x['gas_used'], (x.get('zkos') or {}).get('computational_native'))
            row['replay_same_cost'] = bool(f) and r['status'] == 1 and metric(r) == metric(f)
            if not row['replay_same_cost']: issues.append(f"{c['cell_id']}: replay differs ({metric(r)} vs {metric(f) if f else None})")
    vs = {r['artifacts']['verifier_runtime_sha256'] for r in R if r['op'] != 'deploy_verifier'}; row['verifier_sha256'] = sorted(vs)
    if len(vs) != 1: issues.append(f"{c['cell_id']}: verifier hash not constant {vs}")
    row['status'] = 'COMPLETE'; summary.append(row)
meta = {os.path.basename(os.path.dirname(f)): json.load(open(f)) for f in glob.glob(os.path.join(root, 'raw', '*', 'attempt-*', 'cell-meta.json'))}
out = dict(campaign=campaign, n_cells_scheduled=len(cells), n_cells_complete=sum(1 for s in summary if s['status'] == 'COMPLETE'), n_records=len(recs), issues=issues, cells=summary, valid=not issues)
json.dump(out, open(os.path.join(root, 'VALIDATION.json'), 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('n_cells_scheduled', 'n_cells_complete', 'n_records', 'valid')}), len(issues), 'issues'); [print(' -', i) for i in issues[:40]]
