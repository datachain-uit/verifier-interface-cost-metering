import json, glob, os, re, statistics as st
H=os.path.expanduser('~/p0/out')
rows=[]
for f in sorted(glob.glob(H+'/sweep-*.json')):
    d=json.load(open(f)); arm=d['arm']; reg=d.get('regime') or ('osaka' if arm=='evm' else '29')
    tag=re.sub(r'.*-(paris-bytecode|petersburg-bytecode)\.json$',r'\1',f) if 'bytecode' in f else ''
    key='computational_gas' if arm=='eravm' else 'gasUsed'
    g=lambda o:[r.get(key) for r in d['rows'] if r['op']==o]
    neg=d['calls']; ok=all((v=='true') if n=='valid' else (v!='true') for n,v in neg.items())
    unk=[r for r in d['rows'] if r['op']=='neg_unknown_root_tx']
    rows.append(dict(arm=arm,reg=reg+('/'+tag if tag else ''),circ=d['circuit'],b=d['backend'],k=d['k'],vpd=g('verify_proof_direct'),vc=g('verify_credential'),dep=g('deploy_verifier')[0],
      size=d['sizes'].get('verifier_runtime') or d['sizes'].get('verifier_bytes'),controls=f"{sum(1 for n,v in neg.items() if ((v=='true') if n=='valid' else (v!='true')))}/{len(neg)}",unk_rejected=(unk[0]['status']==0 if unk else None),
      pubdata=[r.get('pubdata_bytes') for r in d['rows'] if r['op']=='verify_proof_direct'][:1]))
for f in sorted(glob.glob(H+'/zkos-t1-*-p0.json'))+sorted(glob.glob(H+'/zkos-t3-mini*-p0.json')):
    d=json.load(open(f)); g=lambda o,k2:[r.get(k2) for r in d['rows'] if r['op']==o]
    neg=d['calls']
    rows.append(dict(arm='zkos',reg='v31/npg100',circ=d['circuit'],b=d['backend'],k=d['k'],vpd=g('verify_proof_direct','gasUsed'),vc=g('verify_credential','gasUsed'),dep=g('deploy_verifier','gasUsed')[0],size=d['sizes']['verifier_runtime'],
      controls=f"{sum(1 for n,v in neg.items() if ((v=='true') if n=='valid' else (v!='true')))}/{len(neg)}",unk_rejected=None,pubdata=g('verify_proof_direct','pubdata_used')[:1], native=g('verify_proof_direct','native_used')))
json.dump(rows,open(H+'/summary-rows.json','w'),indent=1)
print(f"{'arm':5} {'regime':22} {'circuit':20} {'b':7} {'k':>3} {'vpd(min-max)':>22} {'vc(min)':>9} {'deployV':>9} {'size':>6} ctrl unk")
for r in sorted(rows,key=lambda r:(r['arm'],r['reg'],r['b'],r['k'],r['circ'])):
    v=[x for x in r['vpd'] if x is not None]
    print(f"{r['arm']:5} {r['reg']:22} {r['circ']:20} {r['b']:7} {r['k']:>3} {min(v):>10}-{max(v):<10} {min([x for x in r['vc'] if x]):>9} {r['dep']:>9} {r['size']:>6} {r['controls']} {r['unk_rejected']}")
# ratios
print('\nPLONK/G16 ratio of direct verify (plonk min..max over proofs / groth16 mean)')
idx={}
for r in rows: idx[(r['arm'],r['reg'],r['circ'],r['b'])]=r
for (arm,reg,circ,b),r in sorted(idx.items()):
    if b!='groth16': continue
    g=st.mean([x for x in r['vpd'] if x]); line=f"{arm:5} {reg:22} {circ:20} k={r['k']:>2}  G16={g:>10.0f}"
    for ob in ['plonk','fflonk']:
        p=idx.get((arm,reg,circ,ob))
        if not p: continue
        pv=[x for x in p['vpd'] if x]
        line+=f"  {ob.upper()}={min(pv)}..{max(pv)} ratio={min(pv)/g:.4f}..{max(pv)/g:.4f}"
    print(line)
