#!/usr/bin/env python3
"""V2-C2 calibration of the single environment-level constant C_env (registered Groth16 / PLONK data only; no FFLONK input).
usage: c2_calibrate.py <calibration-structural.jsonl> <pilot records> <full records> <M7A-per-proof.csv> <M7B-A-per-proof.csv> <C1 model dir> <out.json>
For each calibration proof: C_env(proof) = N_registered - SOURCE_SUM(structural record). Calibration rule (frozen in
03-calibration.md): C_env = the value common to every calibration proof; if the values were not all identical the C2
package could not be frozen (no averaging). Cross-checks: structural record vs the registered EVM-Osaka trace of the
same proof; OPS+PRE+KEC+COP vs the frozen C1 trace model; source terms vs V2-M7A; heap events vs V2-M7B-A."""
import csv, json, os, sys
STR, PREC, FREC, M7A, M7B, C1M, OUT = sys.argv[1:8]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import c2_model as M
sys.path.insert(0, C1M); import zkos_native_trace_model as ZT
recs = [json.loads(l) for l in open(STR) if l.strip()]
reg = {}; evm = {}
for f in (PREC, FREC):
    for l in open(f):
        if not l.strip(): continue
        r = json.loads(l)
        if r.get('op') != 'verify_proof_direct' or r.get('role') != 'measurement': continue
        if r['env'] == 'zkos-v32' and r['regime'].get('npg') == 100 and not int(r['regime'].get('priority_fee') or 0):
            n = r['zkos']['computational_native']
            if r['proof_id'] in reg and reg[r['proof_id']] != n: raise SystemExit(f"inconsistent registered native for {r['proof_id']}")
            reg[r['proof_id']] = n
        if r['env'] == 'evm-osaka': evm.setdefault(r['proof_id'], r['evm_trace'])
m7a = {r['proof_id']: r for r in csv.DictReader(open(M7A))}; m7b = {r['proof_id']: r for r in csv.DictReader(open(M7B))}
rows = []
for s in recs:
    pid = s['proof_id']; t = M.terms(s); fz = evm[pid]
    chk = dict(
        ops_counts_equal_registered_trace={k: v['n'] for k, v in fz['ops'].items()} == s['ops'],
        precompile_counts_equal=sorted((a, v['n']) for a, v in fz['precompiles'].items()) == sorted((a, sum(1 for c in s['precompile_calls'] if c['addr'] == a)) for a in {c['addr'] for c in s['precompile_calls']}),
        keccak_sizes_equal=fz['keccak_sizes'] == s['keccak_sizes'], copies_equal=[list(x) for x in fz['copies']] == s['copies'],
        c1_components_equal=(ZT.components(fz, s['backend'], '0.4.0')['sum'] == t['OPS'] + t['PRE'] + t['KEC'] + t['COP']),
        m7a_terms_equal=(int(m7a[pid]['src_calldata']) == t['CDT'] and int(m7a[pid]['src_decommit']) == t['DEC'] and int(m7a[pid]['src_calls']) == t['CALL']
                         and int(m7a[pid]['src_heap_bytes']) == s['heap_final_bytes']),
        m7b_events_equal=int(m7b[pid]['observed_heap_events_zkos_rule']) == s['heap_events'],
        no_unknown_terms=not t['unknown'], verified_true=bool(s['returns_true']) and s['status'] == 1)
    rows.append(dict(proof_id=pid, backend=s['backend'], k=s['k'], N_registered=reg[pid], **{k: t[k] for k in ('OPS', 'PRE', 'KEC', 'COP', 'CDT', 'DEC', 'HEAP', 'CALL', 'SOURCE_SUM')},
                     heap_events=s['heap_events'], heap_final_bytes=s['heap_final_bytes'], C_env_implied=reg[pid] - t['SOURCE_SUM'], checks=chk))
vals = sorted({r['C_env_implied'] for r in rows}); allchk = all(all(r['checks'].values()) for r in rows)
res = dict(label='V2-C2 calibration of C_env (registered Groth16 / PLONK only; no FFLONK input)', calibration_proofs=len(rows),
           C_env_values=vals, C_env=vals[0] if len(vals) == 1 else None, single_value=len(vals) == 1, all_cross_checks_pass=allchk,
           calibration_residuals_after_C_env=sorted({r['N_registered'] - (r['SOURCE_SUM'] + vals[0]) for r in rows}) if len(vals) == 1 else None, rows=rows)
json.dump(res, open(OUT, 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'rows'}, indent=1))
for r in rows: print(r['proof_id'], r['N_registered'], r['SOURCE_SUM'], r['C_env_implied'], all(r['checks'].values()))
if not (len(vals) == 1 and allchk): sys.exit(1)
