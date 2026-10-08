#!/usr/bin/env python3
"""V2-M7B-A — count heap-expansion events in the deterministic EDR re-trace of 18 frozen proofs (post hoc mechanism
confirmation; not C1 confirmatory evidence). Protocol: research/csi/protocols/v2/V2-M7B-heap-retrace/M7B-A-PROTOCOL.md
(sha256 16012294695ef276d48c69805b5e354da8e521c834477183188b170e6896c7b8, frozen before the re-trace).
usage: m7b_a_count.py <retrace-summary.json> <retrace-mem-summary.json> <raw dir> <pilot records> <full records> <M7A-per-proof.csv> <out dir>"""
import csv, gzip, json, os, sys
SUM, MSUM, RAW, PREC, FREC, M7A, OUT = sys.argv[1:8]; os.makedirs(OUT, exist_ok=True)
PRED = {1: 22, 2: 22, 4: 24, 8: 24, 12: 28, 16: 32, 24: 40, 32: 48, 64: 80}   # recorded in the protocol before the re-trace
HEAP_BASE = 35
ceil32 = lambda x: (x + 31) // 32 * 32
I = lambda h: int(h, 16)
# ---- registered (frozen) EVM-Osaka traces of the same proofs ----
frozen = {}
for f in (PREC, FREC):
    for l in open(f):
        if not l.strip(): continue
        r = json.loads(l)
        if r.get('env') == 'evm-osaka' and r.get('op') == 'verify_proof_direct' and r.get('role') == 'measurement' and r.get('evm_trace'):
            frozen.setdefault(r['proof_id'], r['evm_trace'])
m7a = {r['proof_id']: r for r in csv.DictReader(open(M7A))}
def regions(op, s):  # ZKsync OS v0.4.0 resize_heap call sites; s = stack (top = last); returns resize calls in order
    t = lambda i: I(s[-1 - i])
    if op == 'MLOAD': return [(t(0), 32)]
    if op == 'MSTORE': return [(t(0), 32)]
    if op == 'MSTORE8': return [(t(0), 1)]
    if op in ('KECCAK256', 'SHA3', 'RETURN', 'REVERT') or op.startswith('LOG'): return [(t(0), t(1))]
    if op in ('CALLDATACOPY', 'CODECOPY', 'RETURNDATACOPY'): return [(t(0), t(2))]
    if op == 'MCOPY': return [(max(t(0), t(1)), t(2))]
    if op == 'EXTCODECOPY': return [(t(1), t(3))]
    if op in ('STATICCALL', 'DELEGATECALL'): return [(t(2), t(3)), (t(4), t(5))]
    if op in ('CALL', 'CALLCODE'): return [(t(3), t(4)), (t(5), t(6))]
    if op in ('CREATE', 'CREATE2'): return [(t(1), t(2))]
    return []
S = json.load(open(SUM)); MS = {x['proof_id']: x for x in json.load(open(MSUM))['items']}
rows, events = [], []
for it in S['items']:
    pid = it['proof_id']; tr = json.load(gzip.open(os.path.join(RAW, it['raw_file']))); logs = tr['structLogs']
    mem = json.load(gzip.open(os.path.join(RAW, MS[pid]['raw_file'])))
    # determinism gate: profile of the re-trace == registered evm_trace of the same proof
    fz = frozen.get(pid); p = it['profile']
    gate = {k: (fz is not None and fz.get(k) == p.get(k)) for k in ('gas', 'steps', 'ops', 'precompiles', 'keccak_sizes', 'copies', 'failed')}
    same_ops = mem['ops'] == [x['op'] for x in logs] and mem['gas'] == tr['gas']
    heap = 0; zk_events = 0; zk_resize_calls = 0; after = []; evlist = []
    for i, x in enumerate(logs):
        if x['depth'] != 1: after.append(heap); continue
        for (off, ln) in regions(x['op'], x['stack']):
            if ln == 0: continue
            zk_resize_calls += 1; new = ceil32(off + ln)
            if new > heap: zk_events += 1; evlist.append((i, x['pc'], x['op'], heap, new)); heap = new
        after.append(heap)
    ms = mem['memSize']
    evm_events = sum(1 for i in range(len(ms) - 1) if ms[i + 1] > ms[i]) + (1 if after[-1] > ms[-1] else 0)
    consistent = all(after[i] == ms[i + 1] for i in range(len(ms) - 1))
    two_step_calls = sum(1 for i, (a, b) in enumerate(zip(evlist, evlist[1:])) if a[0] == b[0])
    m = m7a.get(pid, {})
    rows.append(dict(proof_id=pid, backend=it['backend'], k=it['k'], steps=len(logs), gas=tr['gas'], determinism_gate_pass=all(gate.values()), gate_detail=';'.join(k for k, v in gate.items() if not v) or 'all equal',
                     memtrace_same_execution=same_ops, observed_heap_events_zkos_rule=zk_events, observed_evm_expansions_edr_memsize=evm_events, opcodes_with_two_expanding_resizes=two_step_calls,
                     heap_size_replay_equals_edr_memsize=consistent, final_heap_bytes=after[-1], m7a_heap_words=m.get('heap_words'), final_heap_words_equal_m7a=(str(after[-1] // 32) == m.get('heap_words')),
                     m7a_remainder=m.get('remainder')))
    events += [dict(proof_id=pid, step=i, pc=pc, op=op, heap_before=b, heap_after=a) for (i, pc, op, b, a) in evlist]
rows.sort(key=lambda r: (r['k'], r['backend']))
cmp = []
for k in sorted(PRED):
    g = next(r for r in rows if r['k'] == k and r['backend'] == 'groth16'); pl = next(r for r in rows if r['k'] == k and r['backend'] == 'plonk')
    d = pl['observed_heap_events_zkos_rule'] - g['observed_heap_events_zkos_rule']
    cmp.append(dict(k=k, groth16_proof=g['proof_id'], plonk_proof=pl['proof_id'], groth16_events=g['observed_heap_events_zkos_rule'], plonk_events=pl['observed_heap_events_zkos_rule'],
                    predicted_difference=PRED[k], observed_difference=d, result='MATCH' if d == PRED[k] else 'MISMATCH',
                    evm_expansions_groth16=g['observed_evm_expansions_edr_memsize'], evm_expansions_plonk=pl['observed_evm_expansions_edr_memsize']))
g_ev = sorted(set(r['observed_heap_events_zkos_rule'] for r in rows if r['backend'] == 'groth16'))
closure = sorted(set(int(r['m7a_remainder']) - HEAP_BASE * r['observed_heap_events_zkos_rule'] for r in rows if r['m7a_remainder']))
summary = dict(label='V2-M7B-A POST HOC MECHANISM CONFIRMATION — not C1 confirmatory evidence; F4 / H4 unchanged',
    protocol_sha256='16012294695ef276d48c69805b5e354da8e521c834477183188b170e6896c7b8', hardfork=S['hardfork'],
    proofs=len(rows), determinism_gate_all_pass=all(r['determinism_gate_pass'] for r in rows), memtrace_same_execution_all=all(r['memtrace_same_execution'] for r in rows),
    heap_replay_consistent_with_edr_memsize_all=all(r['heap_size_replay_equals_edr_memsize'] for r in rows), final_heap_equals_m7a_all=all(r['final_heap_words_equal_m7a'] for r in rows),
    per_k=cmp, matches=sum(1 for c in cmp if c['result'] == 'MATCH'), verdict='CONFIRMED' if all(c['result'] == 'MATCH' for c in cmp) and all(r['determinism_gate_pass'] for r in rows) else 'NOT CONFIRMED',
    P2_groth16_event_counts=g_ev, P2_groth16_constant=len(g_ev) == 1,
    P3_remainder_minus_35E_values=closure, P3_single_constant=len(closure) == 1)
for name, data in (('M7B-A-per-proof.csv', rows), ('M7B-A-per-k.csv', cmp), ('M7B-A-events.csv', events)):
    w = csv.DictWriter(open(os.path.join(OUT, name), 'w', newline=''), fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
json.dump(summary, open(os.path.join(OUT, 'M7B-A-summary.json'), 'w'), indent=1)
print(json.dumps(summary, indent=1))
