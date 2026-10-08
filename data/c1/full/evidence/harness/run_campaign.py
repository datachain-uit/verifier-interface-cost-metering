#!/usr/bin/env python3
"""V2-C1 registered harness (v2, full campaign) — orchestrator.

usage: run_campaign.py <campaign PILOT|SELFTEST> <evidence_root> [--proofs DIR] [--compiled DIR] [--cells FILE]
- Cell list: rows of the frozen configs/design-cells.csv whose `campaign` column equals the campaign (or a self-test
  cell file); order = ascending sha256("V2-C1-order|" + campaign + "|" + cell_id) (03-factors-and-configurations.md §5).
- Every cell runs on a fresh node (EDR: new hardhat process; EraVM: new anvil-zksync; ZKsync OS: fresh L1 state +
  ephemeral server at the cell's native_per_gas).
- A cell attempt that fails is preserved (raw/<NN>-<slug>/attempt-<n>/ with CELL-ERROR.txt) and the orchestrator STOPS,
  so that the operator records a deviation (20-deviations-policy.md) before any retry. A cell with a completed attempt
  is never re-run (no duplicates).
"""
import csv, hashlib, json, os, subprocess, sys, time, datetime
H = os.path.dirname(os.path.abspath(__file__)); HOME = os.path.expanduser('~')
PKG = os.environ.get('C1_PKG', os.path.join(HOME, 'c1/pkg'))
campaign, root = sys.argv[1], sys.argv[2]
opt = dict(zip(sys.argv[3::2], sys.argv[4::2]))
proofs_dir = opt.get('--proofs', os.path.join(PKG, 'corpus/proofs')); compiled_dir = opt.get('--compiled', os.path.join(root, 'compiled'))
cells_file = opt.get('--cells', os.path.join(PKG, 'configs/design-cells.csv'))
sha = lambda b: hashlib.sha256(b).hexdigest()
pins_sha = sha(open(os.path.join(PKG, 'toolchain/PINS-C1.txt'), 'rb').read())
rows = [r for r in csv.DictReader(open(cells_file)) if r['campaign'] == campaign]
order = sorted(rows, key=lambda r: sha(f"V2-C1-order|{campaign}|{r['cell_id']}".encode()))
os.makedirs(os.path.join(root, 'raw'), exist_ok=True); os.makedirs(os.path.join(root, 'cells'), exist_ok=True)
json.dump([dict(order_index=i, cell_id=r['cell_id'], order_key=sha(f"V2-C1-order|{campaign}|{r['cell_id']}".encode())) for i, r in enumerate(order)],
          open(os.path.join(root, 'cell-order.json'), 'w'), indent=1)
run_id = os.environ.get('RUN_ID') or f"{campaign}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
log = open(os.path.join(root, 'orchestrator.log'), 'a')
def L(msg): s = f"{datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat()}Z {msg}"; print(s, flush=True); log.write(s + '\n'); log.flush()
L(f'start campaign={campaign} run_id={run_id} cells={len(order)} pins_sha256={pins_sha}')
for i, r in enumerate(order):
    slug = f"{i:02d}-" + r['cell_id'].replace('|', '__').replace('@', '_at_')
    done = os.path.join(root, 'cells', slug + '.jsonl')
    if os.path.exists(done): L(f'skip (completed) {slug}'); continue
    cdir = os.path.join(root, 'raw', slug); os.makedirs(cdir, exist_ok=True)
    n = 1 + len([d for d in os.listdir(cdir) if d.startswith('attempt-')]); adir = os.path.join(cdir, f'attempt-{n}'); os.makedirs(adir)
    env = r['env']; regime = r['regime']
    if env == 'zkos-v32':
        npg = int(regime.split('npg')[1].split('+')[0]); prio = 0
        if 'priority_fee=' in regime:   # CORE-ROBUSTNESS (tx-gas-price route), 16-full-protocol.md §1.4: 1e8 wei
            v = regime.split('priority_fee=')[1].replace('wei', ''); prio = int(float(v)) if 'e' in v else int(v)
        reg = dict(npg=npg, native_price='0xf4240', pubdata_price='0x0', priority_fee=prio)
    elif env.startswith('eravm'): reg = dict(protocol=int(env.split('-')[1]))
    else: reg = dict(hardfork=env.split('-')[1])
    spec = dict(campaign=campaign, run_id=run_id, order_index=i, cell_id=r['cell_id'], env=env, regime=reg, backend=r['backend'], circuit=r['circuit'], k=int(r['k']),
                relation=r['relation'], compiled=os.path.join(compiled_dir, f"{r['circuit']}-{r['backend']}.json"), proofs_dir=proofs_dir, outdir=adir, pins_sha256=pins_sha,
                port=18011, server_log=os.path.join(adir, 'node', 'server.log'), attempt=n)
    json.dump(spec, open(os.path.join(adir, 'spec.json'), 'w'), indent=1)
    L(f'cell {slug} attempt {n} begin')
    t0 = time.time(); ok = True
    with open(os.path.join(adir, 'stdout.txt'), 'w') as so, open(os.path.join(adir, 'stderr.txt'), 'w') as se:
        if env == 'zkos-v32':
            p = subprocess.run([os.path.join(H, 'zkos_node.sh'), os.path.join(adir, 'node'), str(reg['npg'])], stdout=so, stderr=se)
            if p.returncode != 0: ok = False; open(os.path.join(adir, 'CELL-ERROR.txt'), 'w').write('D-CRASH\nZKsync OS node did not start\n')
        if ok:
            p = subprocess.run(['node', os.path.join(H, 'cell.js'), os.path.join(adir, 'spec.json')], stdout=so, stderr=se, cwd=H, timeout=3600)
            ok = p.returncode == 0
        if env == 'zkos-v32': subprocess.run([os.path.join(H, 'zkos_stop.sh')], stdout=so, stderr=se)
    if not ok:
        L(f'cell {slug} attempt {n} FAILED after {time.time() - t0:.0f}s — orchestrator stops for deviation classification'); sys.exit(2)
    open(done, 'w').write(open(os.path.join(adir, 'records.jsonl')).read())
    L(f'cell {slug} attempt {n} done in {time.time() - t0:.0f}s')
L('campaign complete'); open(os.path.join(root, 'COLLECTION-COMPLETE'), 'w').write(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat() + 'Z\n')
