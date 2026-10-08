#!/usr/bin/env python3
"""V2-C2 source-augmented ZKsync OS native-cost model (extended transaction-level accounting), ZKsync OS v32.0 / VM v0.4.0.

N_hat = OPS + PRE + KEC + COP + CDT + DEC + HEAP + CALL + C_env      (computational native, direct verifyProof transaction)

All terms except C_env are source-defined constants of the pinned VM source (commit 69bc430549e88f9264066d14f2001707572c5d33)
applied to a structural record of the same proof (see c2_structural.js). C_env is the single environment-level constant,
calibrated on registered Groth16 / PLONK measurements only (c2_calibrate.py); no FFLONK quantity enters any parameter.
Input: one structural record (dict). Output: dict of terms. Stdlib only; the native table is read from the pinned source file.
"""
import math, os, re
SRC = os.environ.get('C2_ZKOS_SRC', os.path.expanduser('~/p0/zkos/vm-0.4.0'))
NRC = 'evm_interpreter/src/native_resource_constants.rs'
NRC_SHA256 = 'c3e722f436d70668e94ae8a021413bc09cc33007f6be1aee8b005d0e460f14b4'
# precompile natives (basic_system/src/cost_constants.rs; delegation coefficient 4), as frozen in C1 (zkos_native_trace_model.py)
ECADD = 51_400 + 1_650 * 4            # 58,000
ECMUL = 647_000 + 41_000 * 4          # 811,000
PAIR_BASE = 6_244_000
PAIR_PER = 5_572_000 + 334_000 * 4    # 6,908,000 per pair (192 input bytes)
KEC_BASE, KEC_ROUND = 1_150, 649 * 4 + 1_250   # 3,846 per keccak-f round
CDT_BYTE = 2 + 2 * math.ceil(KEC_ROUND / 136)  # bootloader/constants.rs:145,154 -> 60 per calldata byte
PREIMAGE_GET, BLAKE_BASE, BLAKE_ROUND = 500, 800, 340
WARM_ACCOUNT = 4_000                  # flat_storage_model account_cache.rs:242 / cost_constants.rs:41
HEAP_EVENT, HEAP_BYTE = 35, 1         # gas.rs:93-111; native_resource_constants.rs:68-69
PRECOMPILE_OUT = {'0x6': 64, '0x7': 64, '0x8': 32}
assert CDT_BYTE == 60 and KEC_ROUND == 3_846

def _table():
    p = os.path.join(SRC, NRC); raw = open(p, 'rb').read()
    import hashlib
    if hashlib.sha256(raw).hexdigest() != NRC_SHA256: raise SystemExit(f'native table source hash mismatch: {p}')
    C = {m.group(1): int(m.group(2).replace('_', '')) for m in re.finditer(r'pub const (\w+)_NATIVE_COST: u64 = ([\d_]+);', raw.decode())}
    return C
C = _table(); STEP = C['STEP']; COPY_BASE, COPY_BYTE = C['COPY_BASE'], C['COPY_BYTE']

def opnative(op):
    if op.startswith('PUSH'): return C.get(op)
    for p in ('DUP', 'SWAP', 'LOG'):
        if op.startswith(p): return C.get(p)
    if op == 'EXP': return None  # dynamic: handled per occurrence (EXP_BASE + EXP_PER_BYTE * exponent bytes)
    return C.get({'SHA3': 'KECCAK256'}.get(op, op))

def decommit(n):  # preimage_cache.rs:363-371; account_cache_entry.rs:138-163; evm_interpreter/src/lib.rs:192,321-328
    full = n + (-n) % 8 + math.ceil(n / 64) * 8
    return PREIMAGE_GET + BLAKE_BASE + BLAKE_ROUND * math.ceil(full / 64)

def terms(rec, c_env=None):
    unknown = []
    ops = 0
    for op, n in rec['ops'].items():
        if op == 'EXP':
            ops += n * STEP + sum(C['EXP_BASE'] + C['EXP_PER_BYTE'] * b for b in rec.get('exp_exponent_bytes', []))
            if len(rec.get('exp_exponent_bytes', [])) != n: unknown.append('EXP operand record incomplete')
            continue
        c = opnative(op)
        if c is None: unknown.append(op); continue
        ops += n * (c + STEP)
    pre = 0; call = 0; npair = 0
    for pc in rec['precompile_calls']:
        a = pc['addr']
        if a == '0x6': pre += ECADD
        elif a == '0x7': pre += ECMUL
        elif a == '0x8':
            if pc['in_len'] % 192: unknown.append('pairing input not a multiple of 192')
            pre += PAIR_BASE + PAIR_PER * (pc['in_len'] // 192); npair += pc['in_len'] // 192
        else: unknown.append(f'precompile {a}'); continue
        m = min(PRECOMPILE_OUT[a], pc['out_len'])
        call += WARM_ACCOUNT + (COPY_BASE + COPY_BYTE * m if m > 0 else 0)
    kec = sum(KEC_BASE + KEC_ROUND * math.ceil((s + 1) / 136) for s in rec['keccak_sizes'])
    cop = sum(COPY_BASE + COPY_BYTE * n for _, n in rec['copies']) + sum(COPY_BASE + COPY_BYTE * n for n in rec.get('mcopy_sizes', []))
    cdt = CDT_BYTE * rec['calldata_bytes']
    dec = decommit(rec['verifier_runtime_bytes'])
    heap = HEAP_EVENT * rec['heap_events'] + HEAP_BYTE * rec['heap_final_bytes']
    t = dict(OPS=ops, PRE=pre, KEC=kec, COP=cop, CDT=cdt, DEC=dec, HEAP=heap, CALL=call, pairs=npair, unknown=sorted(set(unknown)))
    t['SOURCE_SUM'] = ops + pre + kec + cop + cdt + dec + heap + call
    if c_env is not None: t['C_env'] = c_env; t['N_hat'] = t['SOURCE_SUM'] + c_env
    return t
