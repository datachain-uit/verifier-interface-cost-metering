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

template Presentation8(levels) {
    signal input nameHash; signal input studentId; signal input issueDate; signal input holderSecret; signal input validUntil;
    signal input pathIndices[levels]; signal input siblings[levels];
    signal input root; signal input nullifier; signal input scope; signal input message;
    signal input majorCode; signal input issuerId; signal input minIssueDate; signal input epoch;
    component leafH = Poseidon(7);
    leafH.inputs[0] <== nameHash; leafH.inputs[1] <== majorCode; leafH.inputs[2] <== studentId; leafH.inputs[3] <== issueDate;
    leafH.inputs[4] <== holderSecret; leafH.inputs[5] <== issuerId; leafH.inputs[6] <== validUntil;
    component merkleProof = MerkleProof(levels);
    merkleProof.leaf <== leafH.out;
    for (var i = 0; i < levels; i++) {
        merkleProof.pathIndices[i] <== pathIndices[i];
        merkleProof.siblings[i] <== siblings[i];
    }
    merkleProof.root === root;

    component nf = Poseidon(2); nf.inputs[0] <== holderSecret; nf.inputs[1] <== scope; nf.out === nullifier;
    signal messageSq; messageSq <== message * message;
    component ge = GreaterEqThan(32); ge.in[0] <== issueDate; ge.in[1] <== minIssueDate; ge.out === 1;
    component lt = LessThan(32); lt.in[0] <== epoch; lt.in[1] <== validUntil; lt.out === 1;
}
component main { public [root, nullifier, scope, message, majorCode, issuerId, minIssueDate, epoch] } = Presentation8(11);
