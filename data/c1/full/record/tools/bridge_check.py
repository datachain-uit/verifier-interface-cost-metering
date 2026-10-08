#!/usr/bin/env python3
"""V2-MPI-FULL-01 bridge reproduction check (17-negative-control-protocol.md: bridge cells must reproduce the pilot
exactly per proof ID). Compares every measurement record of the BRIDGE run with the pilot record of the same
(regime, backend, circuit, proof_id, op). Metered quantities compared: gas_used, calldata bytes / zero bytes,
EraVM computational gas, ZKsync OS computational native and native_used, returned value, status, verifier runtime hash.
usage: bridge_check.py <pilot_records.jsonl> <bridge_records.jsonl> <out_dir>"""
import json, sys, os, csv
P, B, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
def lbl(r): return r['env'] + (f"@npg{r['regime']['npg']}" if r['env'] == 'zkos-v32' else '')
def key(r): return (lbl(r), r['backend'], r['circuit'], r['proof_id'], r['op'])
def val(r): return dict(gas_used=r['gas_used'], calldata_bytes=r['calldata_bytes'], calldata_zero=r['calldata_zero'],
    eravm_computational_gas=(r.get('eravm') or {}).get('computational_gas'), zkos_native=(r.get('zkos') or {}).get('computational_native'),
    zkos_native_used=(r.get('zkos') or {}).get('native_used'), returned=r['returned'], status=r['status'], verifier_runtime_sha256=r['artifacts']['verifier_runtime_sha256'])
sel = lambda f: {key(r): r for r in (json.loads(l) for l in open(f) if l.strip()) if r['role'] == 'measurement' and r['op'] in ('verify_proof_direct', 'verify_credential')}
pil, bri = sel(P), sel(B); rows = []
for k, rb in sorted(bri.items()):
    rp = pil.get(k); vb = val(rb); vp = val(rp) if rp else None
    diff = 'NO-PILOT-RECORD' if rp is None else ';'.join(f for f in vb if vb[f] != vp[f])
    rows.append(dict(regime=k[0], backend=k[1], circuit=k[2], proof_id=k[3], op=k[4], identical=(rp is not None and diff == ''), differing_fields=diff,
                     bridge_gas=vb['gas_used'], pilot_gas=vp and vp['gas_used'], bridge_native=vb['zkos_native'], pilot_native=vp and vp['zkos_native'],
                     bridge_eravm=vb['eravm_computational_gas'], pilot_eravm=vp and vp['eravm_computational_gas']))
w = csv.DictWriter(open(os.path.join(OUT, 'BRIDGE-CHECK.csv'), 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
cells = sorted({r['regime'] + '|' + r['backend'] + '|' + r['circuit'] for r in rows})
s = dict(n_compared=len(rows), n_identical=sum(r['identical'] for r in rows), n_cells=len(cells), cells=cells,
         non_identical=[r for r in rows if not r['identical']], verdict='REPRODUCED' if rows and all(r['identical'] for r in rows) else 'NOT-REPRODUCED')
json.dump(s, open(os.path.join(OUT, 'BRIDGE-CHECK.json'), 'w'), indent=1); print(json.dumps({k: v for k, v in s.items() if k != 'non_identical'}), len(s['non_identical']), 'non-identical')
