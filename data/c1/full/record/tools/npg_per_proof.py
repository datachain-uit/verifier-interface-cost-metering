#!/usr/bin/env python3
"""V2-M5 derived table (no verdicts): ZKsync OS per-proof meters for every registered ZKsync OS measurement (direct call),
pilot + FULL. EVM trace cost = gas_used of the EVM Osaka record of the same proof ID (same bytecode, same calldata).
native_per_gas is a meter-binding parameter of the operator configuration (gas = max(EVM gas, floor(native_used x
native_price / effective_gas_price))), not a cryptographic tariff. usage: npg_per_proof.py <out.csv> <records.jsonl ...>"""
import sys, json, csv
OUT, FILES = sys.argv[1], sys.argv[2:]
R = [json.loads(l) for f in FILES for l in open(f) if l.strip()]
M = [r for r in R if r['role'] == 'measurement' and r['op'] == 'verify_proof_direct']
edr = {r['proof_id']: r['gas_used'] for r in M if r['env'] == 'evm-osaka'}
rows = []
for r in M:
    if r['env'] != 'zkos-v32': continue
    g = r['regime']; z = r['zkos']; price = int(str(g['native_price']), 0); egp = int(str(z['effective_gas_price']), 0); nb = z['native_used'] * price // egp; e = edr.get(r['proof_id'])
    rows.append(dict(proof_id=r['proof_id'], backend=r['backend'], k=r['k'], circuit=r['circuit'], native_per_gas=g['npg'], priority_fee_wei=g.get('priority_fee', 0), campaign=r['campaign'],
                     evm_trace_gas=e, computational_native=z['computational_native'], native_used=z['native_used'], native_bound_gas=nb,
                     binding_meter=('NATIVE' if e is not None and nb > e else 'EVM_GAS' if e is not None else 'NO-EDR-PAIR'), final_gas=r['gas_used']))
rows.sort(key=lambda x: (x['k'], x['circuit'], x['native_per_gas'], x['priority_fee_wei'], x['backend'], x['proof_id']))
w = csv.DictWriter(open(OUT, 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows); print(len(rows), 'rows')
