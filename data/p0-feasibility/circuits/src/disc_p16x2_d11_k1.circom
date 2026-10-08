pragma circom 2.0.0;

include "poseidon.circom";
include "comparators.circom";

// Template to select left/right based on selector
template Selector() {
    signal input in[2];  // [left, right]
    signal input s;      // selector (0 or 1)
    signal output out[2];

    // Constrain the selector to a single bit.
    // Without this, s ranges over the whole field. Since the sibling is also a
    // prover-chosen witness, the two Poseidon inputs at this level would then be
    // unconstrained, detaching the proof from the credential leaf: the circuit
    // would prove knowledge of a hash chain ending at root rather than knowledge
    // of a credential recorded in the registry.
    // Regression coverage: test/circuit.selector.negative.js
    s * (s - 1) === 0;

    // s = 0: out = [in[0], in[1]]
    // s = 1: out = [in[1], in[0]]
    out[0] <== (in[1] - in[0]) * s + in[0];
    out[1] <== (in[0] - in[1]) * s + in[1];
}

// Template to verify Merkle proof
template MerkleProof(levels) {
    signal input leaf;
    signal input pathIndices[levels];
    signal input siblings[levels];
    signal output root;

    // Compute root from leaf and proof
    signal computedHash[levels + 1];
    computedHash[0] <== leaf;

    // Declare all components upfront
    component selectors[levels];
    component hashers[levels];
    
    // Initialize components
    for (var i = 0; i < levels; i++) {
        selectors[i] = Selector();
        hashers[i] = Poseidon(2);
    }

    // Walk from leaf up to root
    for (var i = 0; i < levels; i++) {
        // Order left/right based on pathIndex
        selectors[i].in[0] <== computedHash[i];
        selectors[i].in[1] <== siblings[i];
        selectors[i].s <== pathIndices[i];

        // Hash the left-right pair
        hashers[i].inputs[0] <== selectors[i].out[0];
        hashers[i].inputs[1] <== selectors[i].out[1];
        
        // Store hash result for the next level
        computedHash[i + 1] <== hashers[i].out;
    }

    // Root is the final hash
    root <== computedHash[levels];
}

template CredentialDisclosure(levels) {
    signal input pathIndices[levels];
    signal input siblings[levels];
    signal input root;
    signal input attrPriv[32];
    signal attr[32];
    for (var i = 0; i < 32; i++) { attr[0 + i] <== attrPriv[i]; }
    component h0 = Poseidon(16); component h1 = Poseidon(16); component h2 = Poseidon(2);
    for (var i = 0; i < 16; i++) { h0.inputs[i] <== attr[i]; h1.inputs[i] <== attr[16 + i]; }
    h2.inputs[0] <== h0.out; h2.inputs[1] <== h1.out;
    component merkleProof = MerkleProof(levels);
    merkleProof.leaf <== h2.out;
    for (var i = 0; i < levels; i++) {
        merkleProof.pathIndices[i] <== pathIndices[i];
        merkleProof.siblings[i] <== siblings[i];
    }
    merkleProof.root === root;
}
component main { public [root] } = CredentialDisclosure(11);
