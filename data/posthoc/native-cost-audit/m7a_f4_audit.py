#!/usr/bin/env python3
"""V2-M7A — F4 mechanism audit (POST HOC, DESCRIPTIVE DIAGNOSTIC; not a revised model, not confirmatory evidence).

Inputs (all frozen / pinned; verified by hash before use):
  registered records: V2-MPI-PILOT-01-records.jsonl, V2-MPI-FULL-01-records.jsonl
  compiled verifier artifacts of both campaigns (runtime bytecode length only)
  frozen scorer output summary.json (ZC constants base, c)
  frozen C1 trace model zkos_native_trace_model.py (components ops / pre / kec / cop)
  pinned ZKsync OS v0.4.0 source at commit 69bc430549e88f9264066d14f2001707572c5d33 (constants quoted below)

What it does: for every registered ZKsync OS v32.0 @ npg 100 direct-call measurement (no priority fee), it adds to the
frozen model's components the source-defined charges that the frozen model does not contain, using ONLY source constants
(no fitted parameter): the L2 intrinsic native per calldata byte, the decommitment of the called verifier's bytecode
preimage, the per-call frame overhead (warm account-cache access + return-data copy) and the heap bytes implied by the
EVM memory-expansion gas of the same proof's frozen EDR trace. It then reports the remainder N - reconstruction per proof.
The only quantity not observable in the frozen evidence is the number of heap-expansion events (35 native each).
usage: m7a_f4_audit.py <pilot_records> <full_records> <compiled_dir_full> <compiled_dir_pilot> <scoring_summary.json> <out_dir>"""
import json, math, sys, os, csv, glob, statistics, collections
P, F, CF, CP, SUMM, OUT = sys.argv[1:7]; os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.expanduser('~/c1/pkg/model')); import zkos_native_trace_model as ZT
# ---- pinned v0.4.0 source constants (file:line in the audit note) ----
KECCAK256_ROUND_NATIVE_COST = 649 * 4 + 1250                      # basic_system/src/cost_constants.rs:26-32 (KECCAK_DELEGATION_COEFFICIENT 4)
DYN_KECCAK_PER_BYTE = math.ceil(KECCAK256_ROUND_NATIVE_COST / 136)  # bootloader/constants.rs:145
COPY_BASE, COPY_BYTE = 80, 2                                       # native_resource_constants.rs:74,80
CALLDATA_BYTE = COPY_BYTE + 2 * DYN_KECCAK_PER_BYTE                # bootloader/constants.rs:154 -> 60
WARM_ACCOUNT_ACCESS = 4000                                         # flat_storage_model/cost_constants.rs:41; account_cache.rs:242
PREIMAGE_GET, BLAKE_BASE, BLAKE_ROUND = 500, 800, 340              # flat_storage_model/cost_constants.rs:8; cost_constants.rs:44-45
HEAP_BASE, HEAP_BYTE = 35, 1                                       # native_resource_constants.rs:68-69; gas.rs:93-111
assert CALLDATA_BYTE == 60
def decommit(n):  # preimage_cache.rs:363-371; account_cache_entry.rs:138-163; evm_interpreter/src/lib.rs:192,321-328
    full = n + (-n) % 8 + math.ceil(n / 64) * 8
    return PREIMAGE_GET + BLAKE_BASE + BLAKE_ROUND * math.ceil(full / 64), full
def call_overhead(out_len): return WARM_ACCOUNT_ACCESS + COPY_BASE + COPY_BYTE * out_len   # account read + copy_returndata_to_heap (interpreter.rs:446-456)
def heap_words(t):  # EVM memory-expansion gas of MSTORE / MLOAD / MSTORE8 -> final words W (3W + W^2/512)
    o = t['ops']; mg = sum(o[x]['gas'] - 3 * o[x]['n'] for x in ('MSTORE', 'MLOAD', 'MSTORE8') if x in o)
    return next(W for W in range(0, 10000) if 3 * W + W * W // 512 == mg)
R = [json.loads(l) for f in (P, F) for l in open(f) if l.strip()]
M = [r for r in R if r['role'] == 'measurement' and r['op'] == 'verify_proof_direct']
evm = {r['proof_id']: r for r in M if r['env'] == 'evm-osaka'}
code = {}
for f in glob.glob(os.path.join(CF, '*.json')) + glob.glob(os.path.join(CP, '*.json')):
    d = json.load(open(f)); code[(d['circuit'], d['backend'])] = d['evm']['V']['runtime_bytes']
zc = json.load(open(SUMM))['ZC_constants']; base_c, c = zc['base'], zc['per_call']
rows = []
for r in M:
    if r['env'] != 'zkos-v32' or r['regime']['npg'] != 100 or int(r['regime'].get('priority_fee') or 0): continue
    t = evm[r['proof_id']]['evm_trace']; comp = ZT.components(t, r['backend'], '0.4.0'); pc = t['precompiles']
    nma = pc.get('0x7', {}).get('n', 0) + pc.get('0x6', {}).get('n', 0); npr = pc.get('0x8', {}).get('n', 0)
    dec, full = decommit(code[(r['circuit'], r['backend'])]); W = heap_words(t)
    N = r['zkos']['computational_native']; frozen_pred = comp['sum'] + base_c + c * ZT.ncalls(r['backend'], r['k'])
    omitted = dict(calldata=CALLDATA_BYTE * r['calldata_bytes'], decommit=dec, calls=call_overhead(64) * nma + call_overhead(32) * npr, heap_bytes=HEAP_BYTE * 32 * W)
    rows.append(dict(proof_id=r['proof_id'], backend=r['backend'], relation=r['relation'], k=r['k'], circuit=r['circuit'], N=N, frozen_prediction=round(frozen_pred, 1), frozen_residual=round(N - frozen_pred, 1),
        ops=comp['ops'], pre=comp['pre'], kec=comp['kec'], cop=comp['cop'], calldata_bytes=r['calldata_bytes'], verifier_bytecode=code[(r['circuit'], r['backend'])], preimage_bytes=full,
        ecmul_ecadd_calls=nma, pairing_calls=npr, heap_words=W, **{f'src_{k_}': v for k_, v in omitted.items()},
        remainder=N - comp['sum'] - sum(omitted.values())))
rem0 = {b: min(x['remainder'] for x in rows if x['backend'] == b) for b in ('groth16', 'plonk')}
B0 = min(rem0.values())
for x in rows:
    d = x['remainder'] - B0; x['remainder_minus_min'] = d; x['remainder_mod_35'] = d % HEAP_BASE; x['implied_heap_events_vs_min'] = d / HEAP_BASE
rows.sort(key=lambda x: (x['backend'], x['k'], x['relation'], x['proof_id']))
w = csv.DictWriter(open(os.path.join(OUT, 'M7A-per-proof.csv'), 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
cells = collections.defaultdict(list)
for x in rows: cells[(x['backend'], x['relation'], x['k'])].append(x)
cs = []
for (b, rel, k), v in sorted(cells.items(), key=lambda z: (z[0][0], z[0][2], z[0][1])):
    m = lambda f: statistics.mean(x[f] for x in v)
    cs.append(dict(backend=b, relation=rel, k=k, n=len(v), N_mean=round(m('N'), 1), frozen_residual_mean=round(m('frozen_residual'), 1), calldata_bytes=v[0]['calldata_bytes'], verifier_bytecode=v[0]['verifier_bytecode'],
        preimage_bytes=v[0]['preimage_bytes'], heap_words=v[0]['heap_words'], src_calldata=v[0]['src_calldata'], src_decommit=v[0]['src_decommit'], src_calls=v[0]['src_calls'], src_heap_bytes=v[0]['src_heap_bytes'],
        remainder_minus_min=sorted(set(x['remainder_minus_min'] for x in v)), mod35=sorted(set(x['remainder_mod_35'] for x in v)), implied_heap_events=sorted(set(x['implied_heap_events_vs_min'] for x in v))))
w = csv.DictWriter(open(os.path.join(OUT, 'M7A-cells.csv'), 'w', newline=''), fieldnames=list(cs[0].keys())); w.writeheader(); w.writerows(cs)
# k = 1 contrast that identified c
g = cells[('groth16', 'ctx', 1)]; p = cells[('plonk', 'ctx', 1)]; mm = lambda v, f: statistics.mean(x[f] for x in v)
Ug = mm(g, 'N') - mm(g, 'ops') - mm(g, 'pre') - mm(g, 'kec') - mm(g, 'cop'); Up = mm(p, 'N') - mm(p, 'ops') - mm(p, 'pre') - mm(p, 'kec') - mm(p, 'cop')
parts = dict(calldata=mm(p, 'src_calldata') - mm(g, 'src_calldata'), decommit=mm(p, 'src_decommit') - mm(g, 'src_decommit'), extra_calls_34=mm(p, 'src_calls') - mm(g, 'src_calls'), heap_bytes=mm(p, 'src_heap_bytes') - mm(g, 'src_heap_bytes'))
rest = (Up - Ug) - sum(parts.values())
summary = dict(label='V2-M7A POST HOC DESCRIPTIVE DIAGNOSTIC — not a revised model; F4 / H4 unchanged',
    source_commit='69bc430549e88f9264066d14f2001707572c5d33', constants=dict(calldata_byte=CALLDATA_BYTE, warm_account_access=WARM_ACCOUNT_ACCESS, returndata_copy_64=COPY_BASE + COPY_BYTE * 64, returndata_copy_32=COPY_BASE + COPY_BYTE * 32,
        decommit='500 + 800 + 340 * ceil((n + pad8(n) + 8*ceil(n/64)) / 64)', heap='35 per expansion event + 1 per byte'),
    frozen_c_identification=dict(U_groth16_k1=Ug, U_plonk_k1=Up, contrast=Up - Ug, calls_contrast=34, c=(Up - Ug) / 34, frozen_c=c),
    k1_contrast_decomposition=dict(parts, remainder=rest, remainder_over_35=rest / HEAP_BASE, source_per_call=call_overhead(64), c_minus_source_per_call=c - call_overhead(64),
        absorbed_non_call_per_call=(parts['calldata'] + parts['decommit'] + parts['heap_bytes'] + rest) / 34),
    remainder_structure={b: dict(n_proofs=sum(1 for x in rows if x['backend'] == b), min_remainder=rem0[b], all_mod35_zero=all(x['remainder_mod_35'] == 0 for x in rows if x['backend'] == b),
        events_by_k={f"{k}{'' if rel == 'ctx' else '-' + rel}": sorted(set(x['implied_heap_events_vs_min'] for x in v)) for (bb, rel, k), v in sorted(cells.items(), key=lambda z: (z[0][2], z[0][1])) if bb == b}) for b in ('groth16', 'plonk')})
json.dump(summary, open(os.path.join(OUT, 'M7A-summary.json'), 'w'), indent=1, default=float)
print(json.dumps(summary, indent=1, default=float))
