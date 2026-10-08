# EraVM / EVM microbenchmarks for P0f (feasibility). Each fn takes calldata inputs to defeat constant folding.
Q='21888242871839275222246405745257275088548364400416034343698204186575808495617'
P='21888242871839275222246405745257275088696311157297823662689037894645226208583'
fns=[]
def chain(name,op,n):
    body='\n'.join([f'            a := {op}' for _ in range(n)])
    fns.append(f'''    function {name}(uint256 x, uint256 y) external pure returns (uint256 r) {{
        assembly {{
            let a := x
{body}
            r := a
        }}
    }}''')
for n in (64,256):
    chain(f'mulmod{n}','mulmod(a, y, q)',n); chain(f'addmod{n}','addmod(a, y, q)',n); chain(f'add{n}','add(a, y)',n)
    chain(f'sub{n}','sub(a, y)',n); chain(f'mul{n}','mul(a, y)',n); chain(f'sdiv{n}','sdiv(a, or(y, 1))',n)
    chain(f'mod{n}','mod(a, or(y,1))',n)
    # memory: store then load chain at distinct offsets
    body='\n'.join([f'            mstore(add(p, {32*i}), a) a := add(mload(add(p, {32*((i*7)%n)})), y)' for i in range(n)])
    fns.append(f'''    function mem{n}(uint256 x, uint256 y) external pure returns (uint256 r) {{
        assembly {{ let p := mload(0x40) let a := x
{body}
            r := a }}
    }}''')
    body='\n'.join([f'            a := xor(a, calldataload({4+32*i}))' for i in range(n)])
    fns.append(f'''    function cdl{n}(uint256 x, uint256 y) external pure returns (uint256 r) {{
        assembly {{ let a := x
{body}
            r := a }}
    }}''')
for n in (64,256):
    body='\n'.join([f'            a := xor(a, add(x, {i}))' for i in range(n)])
    fns.append(f'''    function xorc{n}(uint256 x, uint256 y) external pure returns (uint256 r) {{
        assembly {{ let a := y
{body}
            r := a }}
    }}''')
for w in (1,8,16,24,32):
    fns.append(f'''    function keccak{w}(uint256 x, uint256 y) external pure returns (uint256 r) {{
        assembly {{ let p := mload(0x40) for {{ let i := 0 }} lt(i, {w}) {{ i := add(i, 1) }} {{ mstore(add(p, mul(i, 32)), add(x, i)) }}
            r := keccak256(p, {32*w}) }}
    }}''')
fns.append(f'''    function inv(uint256 x, uint256 y) external pure returns (uint256 inv_) {{
        assembly {{
            let qq := {Q}
            let t := 0 let newt := 1 let r := qq let newr := mod(x, qq) let quotient let aux let it := 0
            for {{ }} newr {{ }} {{ quotient := sdiv(r, newr) aux := sub(t, mul(quotient, newt)) t := newt newt := aux aux := sub(r, mul(quotient, newr)) r := newr newr := aux it := add(it, 1) }}
            if slt(t, 0) {{ t := add(t, qq) }}
            inv_ := add(mul(it, 0x10000000000000000000000000000000000000000000000000000000000000), 0) inv_ := it
        }}
    }}''')
G1='1, 2'
fns.append('''    function nop(uint256 x, uint256 y) external pure returns (uint256 r) { assembly { r := add(x, y) } }''')
fns.append(f'''    function ecadd(uint256 x, uint256 y) external view returns (uint256 r) {{
        assembly {{ let p := mload(0x40) mstore(p, 1) mstore(add(p,32), 2) mstore(add(p,64), 1) mstore(add(p,96), 2)
            let ok := staticcall(sub(gas(), 2000), 6, p, 128, p, 64) if iszero(ok) {{ revert(0,0) }} r := mload(p) }}
    }}''')
fns.append(f'''    function ecmul(uint256 x, uint256 y) external view returns (uint256 r) {{
        assembly {{ let p := mload(0x40) mstore(p, 1) mstore(add(p,32), 2) mstore(add(p,64), x)
            let ok := staticcall(sub(gas(), 2000), 7, p, 96, p, 64) if iszero(ok) {{ revert(0,0) }} r := mload(p) }}
    }}''')
# pairing e(G1,G2)*e(-G1,G2) == 1 (n pairs repeated)
G2=['11559732032986387107991004021392285783925812861821192530917403151452391805634','10857046999023057135944570762232829481370756359578518086990519993285655852781','4082367875863433681332203403145435568316851327593401208105741076214120093531','8495653923123431417604973247489272438418190587263600148770280649306958101930']
for npairs in (2,4):
    stores=[]
    for i in range(npairs):
        o=192*i; y='2' if i%2==0 else str(int(P)-2)
        vals=['1',y]+G2
        for j,v in enumerate(vals): stores.append(f'mstore(add(p,{o+32*j}), {v})')
    fns.append(f'''    function pair{npairs}(uint256 x, uint256 y) external view returns (uint256 r) {{
        assembly {{ let p := mload(0x40) {' '.join(stores)}
            let ok := staticcall(sub(gas(), 2000), 8, p, {192*npairs}, p, 32) if iszero(ok) {{ revert(0,0) }} r := mload(p) }}
    }}''')
src='// SPDX-License-Identifier: MIT\npragma solidity 0.8.20;\ncontract Micro {\n    uint256 constant q = '+Q+';\n'+'\n'.join(fns)+'\n}\n'
open('Micro.sol','w').write(src)
print(len(fns),'functions')
