# ZKsync OS computational-native model: EVM opcode trace x VM native table + precompile/keccak/copy natives
# + two calibrated constants (base, per-call). Version-parameterised (v0.3.2 = chain v31.0, v0.4.0 = chain v32.0).
import re, json, os, math, glob, sys
VMSRC={'0.3.2':os.path.expanduser('~/p0/zkos/vm-0.3.2'),'0.4.0':os.path.expanduser('~/p0/zkos/vm-0.4.0')}
def load(ver):
    src=open(os.path.join(VMSRC[ver],'evm_interpreter/src/native_resource_constants.rs')).read()
    C={m.group(1):int(m.group(2).replace('_','')) for m in re.finditer(r'pub const (\w+)_NATIVE_COST: u64 = ([\d_]+);',src)}
    if ver=='0.3.2':
        P=dict(ecadd=46_000+1650*4, ecmul=600_000+41_000*4, pair_base=13_000_000+500_000*4, pair_per=13_000_000+500_000*4,
               kec_round=17_500, kec_base=2_500, copy_base=80, copy_byte=1)
    else:
        P=dict(ecadd=51_400+1650*4, ecmul=647_000+41_000*4, pair_base=6_244_000, pair_per=5_572_000+334_000*4,
               kec_round=649*4+1_250, kec_base=1_150, copy_base=C['COPY_BASE'], copy_byte=C['COPY_BYTE'])
    return C,P
def opcost(C,op):
    if op.startswith('PUSH'): return C.get(op)
    for p in ('DUP','SWAP','LOG'):
        if op.startswith(p): return C[p]
    return C.get({'SHA3':'KECCAK256'}.get(op,op))
NPAIRS={'groth16':4,'plonk':2,'fflonk':2}
def ncalls(b,k,counts=None):
    return {'groth16':2*k+1,'plonk':37,'fflonk':13}[b]
def components(trace,b,ver):
    C,P=load(ver); STEP=C['STEP']; ops=0; unknown=set()
    for op,v in trace['ops'].items():
        c=opcost(C,op)
        if c is None: unknown.add(op); continue
        ops+=v['n']*(c+STEP)
    pre=sum({'0x6':P['ecadd'],'0x7':P['ecmul']}.get(a,0)*v['n'] for a,v in trace['precompiles'].items())
    pre+=P['pair_base']+P['pair_per']*NPAIRS[b]
    kec=sum(math.ceil((s+1)/136)*P['kec_round']+P['kec_base'] for s in trace.get('keccak_sizes',[]))
    cop=sum(P['copy_base']+P['copy_byte']*n for _,n in trace.get('copies',[]))
    return dict(ops=ops,pre=pre,kec=kec,cop=cop,sum=ops+pre+kec+cop,unknown=sorted(unknown))
def calibrate(cal):  # cal: list of (b,k,components_sum,measured) for exactly two cells with distinct ncalls
    (b1,k1,s1,m1),(b2,k2,s2,m2)=cal
    n1,n2=ncalls(b1,k1),ncalls(b2,k2)
    c=((m2-s2)-(m1-s1))/(n2-n1); base=(m1-s1)-c*n1
    return base,c
def predict(comp,b,k,base,c): return comp['sum']+base+c*ncalls(b,k)
