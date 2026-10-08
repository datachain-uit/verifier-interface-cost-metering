import json,glob,os,sys
sys.path.insert(0,os.path.expanduser('~/c1/model')); from zkos_native_trace_model import *
tr={}
for f in sorted(glob.glob(os.path.expanduser('~/p0/out/sweep-evm-osaka-*.json'))):
    d=json.load(open(f)); r=[x for x in d['rows'] if x['op']=='verify_proof_direct' and x.get('trace')]
    if r: tr[(d['circuit'],d['backend'])]=(d['k'],r[0]['trace'])
meas31={}
for f in glob.glob(os.path.expanduser('~/p0/out/zkos-t1-*-p0.json'))+glob.glob(os.path.expanduser('~/p0/out/zkos-t3-mini*-p0.json')):
    d=json.load(open(f)); r=[x for x in d['rows'] if x['op']=='verify_proof_direct']; meas31[(d['circuit'],d['backend'])]=r[0]['computational_native']
meas32={}
for b in ('groth16','plonk'):
    d=json.load(open(os.path.expanduser(f'~/p0/out/zkos-v32c-v1_d11-{b}-p0.json'))); r=[x for x in d['rows'] if x['op']=='verify_proof_direct']; meas32[('v1_d11',b)]=r[0]['computational_native']
for ver,meas in (('0.3.2',meas31),('0.4.0',meas32)):
    comp={key:components(t,key[1],ver) for key,(k,t) in tr.items()}
    cal=[(b,1,comp[('v1_d11',b)]['sum'],meas[('v1_d11',b)]) for b in ('groth16','plonk')]
    base,c=calibrate(cal); print(f'== VM {ver}: base={base:.0f} per-call={c:.1f}')
    for key in sorted(tr,key=lambda x:(x[1],tr[x][0],x[0])):
        k=tr[key][0]; p=predict(comp[key],key[1],k,base,c); m=meas.get(key)
        e=f'{(p-m)/m*100:+.3f}%' if m else '   (no meas)'
        print(f'{key[0]:18} {key[1]:7} k={k:>2} pred={p:>12.0f} meas={m}  {e}  unk={comp[key]["unknown"]}')
