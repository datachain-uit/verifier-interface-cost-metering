# V2-C1 registered circuit family generator (derived from the P0 generator; Merkle/selector/credential-hash templates are byte-for-byte the V1 ones).
import sys, re, pathlib
V1 = pathlib.Path.home()/'p0/research/circuits/CredentialVerifier_Depth11.circom'
src = V1.read_text()
common = src[src.index('// Template to select left/right'):src.index('// Main template to verify credential')]
hdr = 'pragma circom 2.0.0;\n\ninclude "poseidon.circom";\ninclude "comparators.circom";\n\n'
hashcred = src[src.index('// Template to hash credential'):src.index('// Template to select left/right')]
merkle_use = '''    component merkleProof = MerkleProof(levels);
    merkleProof.leaf <== LEAF;
    for (var i = 0; i < levels; i++) {
        merkleProof.pathIndices[i] <== pathIndices[i];
        merkleProof.siblings[i] <== siblings[i];
    }
    merkleProof.root === root;
'''
def v1(d):  # k = 1: exact V1 relation
    return src.replace('include "../node_modules/circomlib/circuits/poseidon.circom";', 'include "poseidon.circom";').replace('CredentialVerifier(11)', f'CredentialVerifier({d})')
def ctx(d, nt):  # Context-tag family: k-1 verifier-visible context tags, each bound by one quadratic constraint tagSq[i] <== tag[i]*tag[i]
    body = f'''template CredentialVerifierCtx(levels, NT) {{
    signal input nameHash;
    signal input majorCode;
    signal input studentId;
    signal input issueDate;
    signal input pathIndices[levels];
    signal input siblings[levels];
    signal input root;
    signal input tag[NT];
    component hasher = HashCredential();
    hasher.nameHash <== nameHash;
    hasher.majorCode <== majorCode;
    hasher.studentId <== studentId;
    hasher.issueDate <== issueDate;
{merkle_use.replace('LEAF','hasher.out')}
    // Minimal uniform binding: one quadratic constraint per tag; satisfiable for every field value; makes each tag enter the verification equation
    signal tagSq[NT];
    for (var i = 0; i < NT; i++) {{ tagSq[i] <== tag[i] * tag[i]; }}
}}
component main {{ public [root, tag] }} = CredentialVerifierCtx({d}, {nt});
'''
    return hdr + hashcred + common + body
def disc(d, nattr, npub, scheme):  # Attribute-disclosure variant: fixed nattr-attribute credential; the first npub attributes are public
    if scheme == 'p16x2':   # two Poseidon(16) + Poseidon(2)
        leaf = '''    component h0 = Poseidon(16); component h1 = Poseidon(16); component h2 = Poseidon(2);
    for (var i = 0; i < 16; i++) { h0.inputs[i] <== attr[i]; h1.inputs[i] <== attr[16 + i]; }
    h2.inputs[0] <== h0.out; h2.inputs[1] <== h1.out;
'''; LEAF='h2.out'
    elif scheme == 'chain2':  # Poseidon(2) chain over attributes
        leaf = f'''    component hc[{nattr-1}];
    signal acc[{nattr}];
    acc[0] <== attr[0];
    for (var i = 1; i < {nattr}; i++) {{ hc[i-1] = Poseidon(2); hc[i-1].inputs[0] <== acc[i-1]; hc[i-1].inputs[1] <== attr[i]; acc[i] <== hc[i-1].out; }}
'''; LEAF=f'acc[{nattr-1}]'
    pubdecl = f'    signal input attrPub[{npub}];\n' if npub else ''
    assign = (f'    for (var i = 0; i < {npub}; i++) {{ attr[i] <== attrPub[i]; }}\n' if npub else '') + f'    for (var i = 0; i < {nattr-npub}; i++) {{ attr[{npub} + i] <== attrPriv[i]; }}\n'
    pub = 'root, attrPub' if npub else 'root'
    body = f'''template CredentialDisclosure(levels) {{
    signal input pathIndices[levels];
    signal input siblings[levels];
    signal input root;
{pubdecl}    signal input attrPriv[{nattr-npub}];
    signal attr[{nattr}];
{assign}{leaf}{merkle_use.replace('LEAF',LEAF)}}}
component main {{ public [{pub}] }} = CredentialDisclosure({d});
'''
    return hdr + common + body
def anchor4(d):  # Semantic anchor, k = 4: membership + scoped nullifier Poseidon(holderSecret, scope) + bound message (public: root, nullifier, scope, message)
    body = f'''template Presentation4(levels) {{
    signal input nameHash; signal input majorCode; signal input studentId; signal input issueDate; signal input holderSecret;
    signal input pathIndices[levels]; signal input siblings[levels];
    signal input root; signal input nullifier; signal input scope; signal input message;
    component leafH = Poseidon(5);
    leafH.inputs[0] <== nameHash; leafH.inputs[1] <== majorCode; leafH.inputs[2] <== studentId; leafH.inputs[3] <== issueDate; leafH.inputs[4] <== holderSecret;
{merkle_use.replace('LEAF','leafH.out')}
    component nf = Poseidon(2); nf.inputs[0] <== holderSecret; nf.inputs[1] <== scope; nf.out === nullifier;
    signal messageSq; messageSq <== message * message;
}}
component main {{ public [root, nullifier, scope, message] }} = Presentation4({d});
'''
    return hdr + common + body
def anchor8(d):  # Semantic anchor, k = 8: k = 4 anchor + disclosed majorCode and issuerId + issue-date lower bound + expiry check against a public epoch
    body = f'''template Presentation8(levels) {{
    signal input nameHash; signal input studentId; signal input issueDate; signal input holderSecret; signal input validUntil;
    signal input pathIndices[levels]; signal input siblings[levels];
    signal input root; signal input nullifier; signal input scope; signal input message;
    signal input majorCode; signal input issuerId; signal input minIssueDate; signal input epoch;
    component leafH = Poseidon(7);
    leafH.inputs[0] <== nameHash; leafH.inputs[1] <== majorCode; leafH.inputs[2] <== studentId; leafH.inputs[3] <== issueDate;
    leafH.inputs[4] <== holderSecret; leafH.inputs[5] <== issuerId; leafH.inputs[6] <== validUntil;
{merkle_use.replace('LEAF','leafH.out')}
    component nf = Poseidon(2); nf.inputs[0] <== holderSecret; nf.inputs[1] <== scope; nf.out === nullifier;
    signal messageSq; messageSq <== message * message;
    component ge = GreaterEqThan(32); ge.in[0] <== issueDate; ge.in[1] <== minIssueDate; ge.out === 1;
    component lt = LessThan(32); lt.in[0] <== epoch; lt.in[1] <== validUntil; lt.out === 1;
}}
component main {{ public [root, nullifier, scope, message, majorCode, issuerId, minIssueDate, epoch] }} = Presentation8({d});
'''
    return hdr + common + body

def mini(nt):  # FFLONK feasibility mini-relation: V1 credential leaf with depth 0 (root = leaf) + (k-1) bound context tags
    body = f'''template MiniCtx(NT) {{
    signal input nameHash; signal input majorCode; signal input studentId; signal input issueDate;
    signal input root;
    signal input tag[NT];
    component hasher = HashCredential();
    hasher.nameHash <== nameHash; hasher.majorCode <== majorCode; hasher.studentId <== studentId; hasher.issueDate <== issueDate;
    hasher.out === root;
    signal tagSq[NT];
    for (var i = 0; i < NT; i++) {{ tagSq[i] <== tag[i] * tag[i]; }}
}}
component main {{ public [root, tag] }} = MiniCtx({nt});
'''
    return hdr + hashcred + body

def _main():
    kind, d = sys.argv[1], int(sys.argv[2]); out = pathlib.Path(sys.argv[-1])
    if kind == 'v1': t = v1(d)
    elif kind == 'ctx': t = ctx(d, int(sys.argv[3]) - 1)
    elif kind == 'disc': t = disc(d, int(sys.argv[3]), int(sys.argv[4]) - 1, sys.argv[5])
    elif kind == 'a4': t = anchor4(d)
    elif kind == 'a8': t = anchor8(d)
    elif kind == 'pad': t = pad(d, int(sys.argv[3]))
    elif kind == 'mini': t = mini(int(sys.argv[3]) - 1)
    out.write_text(t)

def pad(d, npad):  # D1 prover intervention: V1 relation at depth d + npad inert private squaring constraints (chained)
    t = v1(d).replace('component main { public [root] } = CredentialVerifier(%d);' % d, '')
    t = t.replace('template CredentialVerifier(levels) {', 'template CredentialVerifierPad(levels, NPAD) {\n    signal input padSeed;\n    signal padChain[NPAD + 1];\n    padChain[0] <== padSeed;\n    for (var i = 0; i < NPAD; i++) { padChain[i + 1] <== padChain[i] * padChain[i]; }')
    return t + f'component main {{ public [root] }} = CredentialVerifierPad({d}, {npad});\n'
if __name__ == '__main__':
    _main()
