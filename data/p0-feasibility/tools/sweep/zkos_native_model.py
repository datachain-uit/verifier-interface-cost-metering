# Predict ZKsync OS computational native from the EDR opcode trace x zksync-os v0.3.2 native table (P0f composability probe).
import re, json, os, math, glob
SRC=os.path.expanduser('~/p0/zkos/vm-0.3.2/evm_interpreter/src/native_resource_constants.rs')
C={m.group(1):int(m.group(2).replace('_','')) for m in re.finditer(r'pub const (\w+)_NATIVE_COST: u64 = ([\d_]+);',open(SRC).read())}
STEP=C['STEP']
def opcost(op):
    if op.startswith('PUSH'): return C.get(op, C.get('PUSH'+op[4:],0))
    if op.startswith('DUP'): return C['DUP']
    if op.startswith('SWAP'): return C['SWAP']
    if op.startswith('LOG'): return C['LOG']
    alias={'KECCAK256':'KECCAK256','SHA3':'KECCAK256','STATICCALL':'STATICCALL','JUMPDEST':'JUMPDEST'}
    k=alias.get(op,op)
    if k not in C: return None
    return C[k]
PRE={'0x6':52600,'0x7':764000}
def pairing(npairs): return 15000000+15000000*npairs
def keccak(len_): return math.ceil((len_+1)/136)*17500+2500   # rounds = ceil((len+1)/136) assumed (padding); checked below
rows=[]
for f in sorted(glob.glob(os.path.expanduser('~/p0/out/sweep-evm-osaka-*.json'))):
    d=json.load(open(f)); tr=[x for x in d['rows'] if x['op']=='verify_proof_direct' and x.get('trace')]
    if not tr: continue
    t=tr[0]['trace']; unknown=set(); ops=0
    for op,v in t['ops'].items():
        c=opcost(op)
        if c is None: unknown.add(op); continue
        ops+=v['n']*(c+STEP)
    pre=sum(PRE.get(a,0)*v['n'] for a,v in t['precompiles'].items())
    npairs={1:4}.get(0,0)
    k=d['k']; b=d['backend']
    pre+=pairing(4 if b=='groth16' else 2)
    kec=sum(keccak(s) for s in t.get('keccak_sizes',[]))
    cop=sum(80+n for _,n in t.get('copies',[]))
    rows.append(dict(circ=d['circuit'],b=b,k=k,ops=ops,pre=pre,kec=kec,cop=cop,unknown=sorted(unknown),steps=t['steps']))
# measured (proof j=0 is the traced proof in both arms)
meas={}
for f in glob.glob(os.path.expanduser('~/p0/out/zkos-t1-*-p0.json'))+glob.glob(os.path.expanduser('~/p0/out/zkos-t3-mini*-p0.json')):
    d=json.load(open(f)); r=[x for x in d['rows'] if x['op']=='verify_proof_direct']
    meas[(d['circuit'],d['backend'])]=r[0]['computational_native']
base=None
for r in rows:
    m=meas.get((r['circ'],r['b']))
    r['pred_noovh']=r['ops']+r['pre']+r['kec']+r['cop']; r['meas']=m
    if r['circ']=='v1_d11' and r['b']=='groth16' and m: base=m-r['pred_noovh']
print('calibrated tx overhead (G16 k=1):',base)
for r in sorted(rows,key=lambda r:(r['b'],r['k'],r['circ'])):
    if r['meas'] is None: continue
    p=r['pred_noovh']+base; e=(p-r['meas'])/r['meas']*100
    print(f"{r['circ']:14} {r['b']:7} k={r['k']:>2} meas={r['meas']:>10} pred={p:>10} err={e:+.3f}%  [ops {r['ops']} pre {r['pre']} kec {r['kec']} copy {r['cop']}] unknown={r['unknown']}")
# --- refinement: per-call frame overhead c (native) and base constant, calibrated on k=1 only (both backends) ---
import itertools
R={(r['circ'],r['b']):r for r in rows}
ncalls=lambda r: (2*r['k']+1) if r['b']=='groth16' else (37 if r['b']=='plonk' else 13)
g1,p1=R[('v1_d11','groth16')],R[('v1_d11','plonk')]
# meas = pred_noovh + base + c*ncalls
c=((p1['meas']-p1['pred_noovh'])-(g1['meas']-g1['pred_noovh']))/(ncalls(p1)-ncalls(g1)); base2=g1['meas']-g1['pred_noovh']-c*ncalls(g1)
print(f'\nrefined: per-call overhead c={c:.0f} native, base={base2:.0f} (calibrated on k=1 G16+PLONK); held-out predictions:')
errs=[]
for r in sorted(rows,key=lambda r:(r['b'],r['k'],r['circ'])):
    if r['meas'] is None: continue
    p=r['pred_noovh']+base2+c*ncalls(r); e=(p-r['meas'])/r['meas']*100; errs.append((r['circ'],r['b'],e))
    print(f"{r['circ']:14} {r['b']:7} k={r['k']:>2} meas={r['meas']:>10} pred={p:>12.0f} err={e:+.3f}%")
