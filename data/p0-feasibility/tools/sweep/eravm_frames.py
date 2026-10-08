import json, glob, os, collections
H=os.path.expanduser('~/p0/out')
def frames(path):
    d=json.load(open(path)); rows=d['rows']
    v=[x for x in rows if x['op']=='deploy_verifier'][0]['contractAddress'].lower()
    r=[x for x in rows if x['op']=='verify_proof_direct' and x.get('trace')][0]
    def find(f):
        if (f.get('to') or '').lower()==v and (f.get('from') or '').lower().endswith('b92266'): return f
        for c in f.get('calls') or []:
            x=find(c)
            if x: return x
    vf=None
    for c in r['trace'].get('calls') or []:
        vf=find(c)
        if vf: break
    g=lambda f:int(f.get('gasUsed','0x0'),16)
    # transaction-level remainder outside the verifier frame
    outside=r['computational_gas']-g(vf)
    ch=collections.Counter(); chn=collections.Counter()
    for c in vf.get('calls') or []:
        a=(c.get('to') or '').lower()[-4:]; ch[a]+=g(c); chn[a]+=1
    return dict(circ=d['circuit'],b=d['backend'],k=d['k'],reg=d.get('regime'),total=r['computational_gas'],outside=outside,frame=g(vf),self=g(vf)-sum(ch.values()),children={k:(chn[k],ch[k]) for k in ch},size=d['sizes']['verifier_bytes'])
out=[]
for p in sorted(glob.glob(H+'/sweep-eravm-*.json')):
    try: out.append(frames(p))
    except Exception as e: print('ERR',p,e)
json.dump(out,open(H+'/eravm-frames.json','w'),indent=1)
for x in sorted(out,key=lambda x:(x['reg'],x['b'],x['k'],x['circ'])):
    print(x['reg'],x['b'],x['circ'],'k',x['k'],'total',x['total'],'outside',x['outside'],'frame',x['frame'],'self',x['self'],'size',x['size'],{k:v for k,v in sorted(x['children'].items())})
