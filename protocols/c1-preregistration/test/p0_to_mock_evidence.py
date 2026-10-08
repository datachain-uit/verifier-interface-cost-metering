# CODE TEST ONLY: converts P0 feasibility JSON into the C1 evidence schema to exercise score_c1.py. Output is NOT evidence.
import json, glob, os
H = os.path.expanduser('~'); MAP = {'v1_d11': 'c1_k01', 'a4_d11': 'c1_a4', 'a8_d11': 'c1_a8', 'disc_p16x2_d11_k4': 'c1_disc_k04'}
def cname(c): return MAP.get(c) or ('c1_ctx_k%02d' % int(c.split('_k')[-1]) if c.startswith('ctx_') else None)
frames = {(f['reg'], f['circ'], f['b']): f for f in json.load(open(H + '/p0/out/eravm-frames.json'))}
out = []
for f in sorted(glob.glob(H + '/p0/out/sweep-*.json')) + sorted(glob.glob(H + '/p0/out/zkos-t1-*-p0.json')):
    d = json.load(open(f)); c = cname(d['circuit'])
    if c is None or 'petersburg-bytecode' in f: continue
    zk = os.path.basename(f).startswith('zkos'); env = 'zkos-v32' if zk else ('evm-' + d.get('regime', 'osaka') if d['arm'] == 'evm' else 'eravm-' + str(d['regime']))
    reg = {'npg': 100, 'native_price': '0xf4240', 'pubdata_price': '0x0', 'priority_fee': 0} if zk else ({'hardfork': d.get('hardfork')} if d['arm'] == 'evm' else {'protocol': int(d['regime'])})
    js = {}
    for r in d['rows']:
        if r['op'] not in ('verify_proof_direct', 'verify_credential'): continue
        j = r.get('j'); j = js.setdefault(r['op'], -1) + 1 if j is None else j; js[r['op']] = j
        rec = dict(schema='v2-c1-evidence/1', campaign='MOCK', env=env, regime=reg, backend=d['backend'], circuit=c, k=d['k'], relation='ctx', proof_id=f"{c}/{d['backend']}/j{j}", op=r['op'], control=None, role='measurement',
                   status=r['status'], gas_used=r.get('gasUsed'), calldata_bytes=r.get('calldata_bytes'), calldata_zero=r.get('calldata_zero', 0), evm_trace=None, eravm=None, zkos=None)
        if env.startswith('evm') and r.get('trace'): rec['evm_trace'] = r['trace']
        if env.startswith('eravm'):
            rec['eravm'] = dict(computational_gas=r['computational_gas'])
            fr = frames.get((str(d['regime']), d['circuit'], d['backend']))
            if fr and r['op'] == 'verify_proof_direct' and r['computational_gas'] == fr['total']: rec['eravm']['frames'] = dict(outside=fr['outside'], self=fr['self'], precompiles=fr['children'])
        if zk: rec['zkos'] = dict(computational_native=r['computational_native'], native_used=r['native_used'], pubdata_used=r['pubdata_used'], effective_gas_price=str(r.get('effectiveGasPrice') or d['base_fee']))
        out.append(rec)
    for n, v in d.get('calls', {}).items():
        out.append(dict(schema='v2-c1-evidence/1', campaign='MOCK', env=env, regime=reg, backend=d['backend'], circuit=c, k=d['k'], proof_id=f"{c}/{d['backend']}/j0", op='control', control=n, role='control', status=1, returned=v))
open(H + '/c1/test/mock-evidence.jsonl', 'w').write('\n'.join(json.dumps(r) for r in out) + '\n'); print(len(out))
