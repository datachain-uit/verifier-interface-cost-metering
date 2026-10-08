#!/usr/bin/env python3
"""V2-C1 registered harness — H-freeze run manifest (RUN-MANIFEST-<campaign>.json). Verifies every pin before writing; exits non-zero on any mismatch."""
import hashlib, json, os, sys, subprocess, csv, glob, datetime, platform
HOME = os.path.expanduser('~'); PKG = os.path.join(HOME, 'c1/pkg'); H = os.path.dirname(os.path.abspath(__file__))
campaign_id, campaign, root = sys.argv[1:4]
f256 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
def run(*a): return subprocess.run(list(a), capture_output=True, text=True).stdout.strip()
problems = []
# 1. C1 package
c1 = f256(os.path.join(PKG, 'SHA256SUMS'))
if c1 != '7dac8482aea1420a30b303c3d45b0c46627da67a976e578fa1d09d7c715bfc8f': problems.append('C1 SHA256SUMS hash')
if subprocess.run(['sha256sum', '-c', '--quiet', 'SHA256SUMS'], cwd=PKG).returncode != 0: problems.append('C1 file check')
if subprocess.run(['sha256sum', '-c', '--quiet', 'CORPUS-SHA256SUMS'], cwd=os.path.join(PKG, 'corpus')).returncode != 0: problems.append('corpus file check')
# 2. pinned binaries (PINS-C1.txt; paths relative to ~/p0)
pins = []
for l in open(os.path.join(PKG, 'toolchain/PINS-C1.txt')):
    l = l.strip()
    if not l or l.startswith('#'): continue
    h, p = l.split(None, 1); base = os.path.join(HOME, 'p0') if not p.startswith('local-chains') and not p.startswith(('basic_system', 'evm_interpreter', 'zk_ee')) else None
    if p.startswith('local-chains'): full = os.path.join(HOME, 'p0/zkos/src', p)
    elif p.startswith(('basic_system', 'evm_interpreter', 'zk_ee')): full = os.path.join(HOME, 'p0/zkos/vm-0.4.0', p)
    else: full = os.path.join(HOME, 'p0', p)
    got = f256(full) if os.path.exists(full) else None; pins.append(dict(path=p, pinned=h, actual=got, match=got == h))
    if got != h: problems.append(f'pin {p}')
# 3. PLONK key regeneration (pilot step 1)
regen = [l.rstrip('\n').split('\t') for l in open(os.path.join(HOME, 'pilot/regen/regen-result.tsv')) if l.startswith('c1_')]
if len(regen) != 13 or any(x[-1] != 'MATCH' for x in regen): problems.append('PLONK regeneration')
# 4. harness hash
files = sorted(['cell.js', 'run_campaign.py', 'compile_all.js', 'contracts.js', 'zkos_node.sh', 'zkos_stop.sh', 'make_manifest.py', 'validate_evidence.py', 'freeze_evidence.sh', 'evidence-schema.json',
                'lib/solc.js', 'lib/proofs.js', 'lib/eravm.js', 'hh/evm_run.js', 'hh/hardhat.config.js'])
hs = ''.join(f'{f256(os.path.join(H, f))}  {f}\n' for f in files); open(os.path.join(root, 'HARNESS-SHA256SUMS'), 'w').write(hs)
harness_hash = hashlib.sha256(hs.encode()).hexdigest()
if f256(os.path.join(H, 'evidence-schema.json')) != f256(os.path.join(PKG, '18-evidence-schema.json')): problems.append('schema copy')
# 5. compiled bytecode (frozen verifiers + generated managers)
comp = {}
for f in sorted(glob.glob(os.path.join(root, 'compiled', '*.json'))):
    d = json.load(open(f)); comp[os.path.basename(f)] = dict(file_sha256=f256(f), verifier_source_sha256=d['verifier_source_sha256'], manager_source_sha256=d['manager_source_sha256'], base_source_sha256=d['base_source_sha256'],
        evm_verifier_runtime_sha256=d['evm']['V']['runtime_sha256'], evm_manager_runtime_sha256=d['evm']['M']['runtime_sha256'], eravm_verifier_sha256=d['eravm']['V']['sha256'], eravm_manager_sha256=d['eravm']['M']['sha256'])
    exp = [r for r in csv.DictReader(open(os.path.join(PKG, 'circuits/CIRCUITS.csv'))) if r['circuit'] == d['circuit']][0][f"{d['backend']}_verifier_sol_sha256"]
    if d['verifier_source_sha256'] != exp: problems.append(f"verifier source {d['circuit']} {d['backend']}")
# 6. predictions, scorer, corpus
pred_list = ''.join(f'{f256(p)}  {os.path.relpath(p, PKG)}\n' for p in sorted(glob.glob(os.path.join(PKG, '09-numeric-predictions', '*'))))
order = json.load(open(os.path.join(root, 'cell-order.json'))) if os.path.exists(os.path.join(root, 'cell-order.json')) else None
cells = [r for r in csv.DictReader(open(os.path.join(PKG, 'configs/design-cells.csv'))) if r['campaign'] == campaign]
order = sorted([dict(cell_id=r['cell_id'], order_key=hashlib.sha256(f"V2-C1-order|{campaign}|{r['cell_id']}".encode()).hexdigest()) for r in cells], key=lambda x: x['order_key'])
for i, o in enumerate(order): o['order_index'] = i
versions = dict(node=run('node', '--version'), solc=run(os.path.join(HOME, 'p0/bin/solc-0.8.20'), '--version').split('\n')[-1], zksolc=run(os.path.join(HOME, 'p0/bin/zksolc-1.5.15'), '--version'),
    anvil_zksync=run(os.path.join(HOME, 'p0/bin/anvil-zksync-0.6.11'), '--version'), zksync_os_server='v0.23.0 prebuilt (commit 610bfa2b); binary sha256 in pins', l1_anvil=run(os.path.join(HOME, 'p0/bin/foundry151/anvil'), '--version').split('\n')[0],
    packages={p: json.load(open(os.path.join(HOME, 'p0/node/node_modules', p, 'package.json')))['version'] for p in ('snarkjs', 'ethers', 'zksync-ethers', '@openzeppelin/contracts', 'circomlibjs')},
    hardhat=json.load(open(os.path.join(HOME, 'p0/hh/node_modules/hardhat/package.json')))['version'], edr=json.load(open(os.path.join(HOME, 'p0/hh/node_modules/@nomicfoundation/edr/package.json')))['version'],
    zksync_os_chain='local-chains/v32.0 (zksync_os_version 0.32.0, execution_version 7, VM zksync-os v0.4.0 @ 69bc4305)', eravm_protocols='29 (CORE pilot)', evm_hardfork='osaka', host=f'{platform.machine()} {platform.system()} {platform.release()}; {os.cpu_count()} vCPU')
m = dict(campaign_id=campaign_id, campaign=campaign, created_utc=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat() + 'Z', collection_start_utc='immediately after this manifest (first cell timestamp in orchestrator.log)',
    c1_package='research/csi/protocols/v2/V2-C1-preregistration', c1_sha256sums_sha256=c1, c1_files_verified=('C1 file check' not in problems),
    corpus=dict(manifest_sha256=f256(os.path.join(PKG, 'corpus/corpus-manifest.json')), corpus_sha256sums_sha256=f256(os.path.join(PKG, 'corpus/CORPUS-SHA256SUMS')), verified=('corpus file check' not in problems)),
    predictions=dict(files=pred_list.splitlines(), listing_sha256=hashlib.sha256(pred_list.encode()).hexdigest()), scorer_sha256=f256(os.path.join(PKG, 'scoring/score_c1.py')),
    model_sha256={f: f256(os.path.join(PKG, 'model', f)) for f in ('c1_model.py', 'zkos_native_trace_model.py')},
    harness=dict(files=hs.splitlines(), harness_sha256=harness_hash, self_test='selftest/ (P0 fixtures only; tooling check; not evidence)', env_overrides_in_registered_run='none (SELFTEST_FOREIGN_JSON unset; C1_KEYS unset → frozen package keys)'),
    plonk_key_regeneration=[dict(circuit=x[0], result=x[-1], **dict(kv.split('=', 1) for kv in x[1:-1])) for x in regen],
    pins=pins, versions=versions, compiled=comp, frozen_order=order, n_cells=len(order), problems=problems)
out = os.path.join(root, f'RUN-MANIFEST-{campaign}.json'); json.dump(m, open(out, 'w'), indent=1)
print('problems:', problems); print('harness_sha256', harness_hash); print('manifest', f256(out)); sys.exit(1 if problems else 0)
