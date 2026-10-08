# P0f: EraVM v29 component model retrodiction. Calibration from microbenchmarks only (no verifier data), except where noted.
import json, glob, os
H=os.path.expanduser('~/p0/out')
U=dict(mulmod=283.0, addmod=12.0, inv_iter=120.0, memop=28.6, cdl=7.0, call_ecadd=516, call_ecmul=522, call_pair2=692, call_pair4=836, call_keccak=345, fn_base=231)
TAR=dict(ecadd=107+194, ecmul=5334+162, pair2=160000+570, pair4=320000+954)   # tariff + handling (handling from microbenchmark frames)
def kecc(sz): import math; return 119+40*math.ceil((sz+1)/136)
TX_BASE=114743; CALLDATA_PER_BYTE=0.3; MICRO_CALLDATA=68
fr={(x['circ'],x['b']):x for x in json.load(open(H+'/eravm-frames.json')) if x['reg']=='29'}
out=[]
for f in sorted(glob.glob(H+'/sweep-evm-osaka-*.json')):
    d=json.load(open(f)); c,b,k=d['circuit'],d['backend'],d['k']
    if (c,b) not in fr: continue
    tr=[x for x in d['rows'] if x['op']=='verify_proof_direct' and x.get('trace')]
    if not tr: continue
    t=tr[0]['trace']; n=lambda o:t['ops'].get(o,{}).get('n',0)
    if 'keccak_sizes' not in t: continue
    if b=='groth16': calls=k*U['call_ecadd']+k*U['call_ecmul']+U['call_pair4']; pre=k*TAR['ecadd']+k*TAR['ecmul']+TAR['pair4']; kec=0; kcalls=0
    else: calls=18*U['call_ecadd']+18*U['call_ecmul']+U['call_pair2']; pre=18*TAR['ecadd']+18*TAR['ecmul']+TAR['pair2']; kec=sum(kecc(s) for s in t['keccak_sizes']); kcalls=len(t['keccak_sizes'])*U['call_keccak']
    self_pred=U['fn_base']+calls+kcalls+n('MULMOD')*U['mulmod']+n('ADDMOD')*U['addmod']+n('SDIV')*U['inv_iter']+(n('MLOAD')+n('MSTORE'))*U['memop']+n('CALLDATALOAD')*U['cdl']
    F=fr[(c,b)]; words=F['size']/32
    calldata=(4+(256 if b=='groth16' else 768)+32*k)
    outside_pred=TX_BASE+CALLDATA_PER_BYTE*(calldata-MICRO_CALLDATA)+4*words
    total_pred=outside_pred+pre+kec+self_pred
    out.append((c,b,k,F['self'],self_pred,F['outside'],outside_pred,F['total'],total_pred))
print(f"{'circuit':14} {'b':7} {'k':>2} {'self meas':>9} {'self pred':>9} {'err%':>7} {'outside m':>9} {'outside p':>9} {'total meas':>10} {'total pred':>10} {'err%':>6}")
for c,b,k,sm,sp,om,op,tm,tp in sorted(out,key=lambda x:(x[1],x[2],x[0])):
    print(f"{c:14} {b:7} {k:>2} {sm:>9} {sp:>9.0f} {100*(sp-sm)/sm:>+7.1f} {om:>9} {op:>9.0f} {tm:>10} {tp:>10.0f} {100*(tp-tm)/tm:>+6.2f}")
# backend difference at k=1 (V1-style), and per-input slopes
D={(x[0],x[1]):x for x in out}
g,p=D[('v1_d11','groth16')],D[('v1_d11','plonk')]
print('\nk=1 PLONK-G16 total: measured',p[7]-g[7],' predicted',round(p[8]-g[8]))
for b in ['groth16','plonk']:
    a,z=D[('v1_d11',b)],D[('ctx_d11_k32',b)]
    print(b,'per-input slope total: measured',round((z[7]-a[7])/31,1),' predicted',round((z[8]-a[8])/31,1),'| self slope meas',round((z[3]-a[3])/31,1),'pred',round((z[4]-a[4])/31,1))
