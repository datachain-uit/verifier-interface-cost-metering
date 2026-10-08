pragma circom 2.0.0;

include "poseidon.circom";
include "comparators.circom";

// Template to hash credential information into a leaf node
template HashCredential() {
    signal input nameHash;
    signal input majorCode;
    signal input studentId;
    signal input issueDate;
    signal output out;

    // Hash all credential information
    component hasher = Poseidon(4);
    hasher.inputs[0] <== nameHash;
    hasher.inputs[1] <== majorCode;
    hasher.inputs[2] <== studentId;
    hasher.inputs[3] <== issueDate;
    out <== hasher.out;
}

template MiniCtx(NT) {
    signal input nameHash; signal input majorCode; signal input studentId; signal input issueDate;
    signal input root;
    signal input tag[NT];
    component hasher = HashCredential();
    hasher.nameHash <== nameHash; hasher.majorCode <== majorCode; hasher.studentId <== studentId; hasher.issueDate <== issueDate;
    hasher.out === root;
    signal tagSq[NT];
    for (var i = 0; i < NT; i++) { tagSq[i] <== tag[i] * tag[i]; }
}
component main { public [root] } = MiniCtx(0);
