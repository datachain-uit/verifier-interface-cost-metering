// Generated managers (pass-through: root check on input[0] + verifier call + event), one per backend and k, V1 semantics.
const fs = require('fs'); const path = require('path');
const BASE = fs.readFileSync(process.env.HOME + '/p0/research/contracts/chain/CredentialManagerBase.sol', 'utf8');
function manager(backend, k) {
  if (backend === 'groth16') return `// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;
import "./CredentialManagerBase.sol";
interface IGroth16ProofVerifier { function verifyProof(uint256[2] calldata _pA, uint256[2][2] calldata _pB, uint256[2] calldata _pC, uint256[${k}] calldata _pubSignals) external view returns (bool); }
contract CredentialManagerGroth16K${k} is CredentialManagerBase {
    constructor(address _verifier) CredentialManagerBase(_verifier) {}
    function verifyCredential(uint256[2] calldata a, uint256[2][2] calldata b, uint256[2] calldata c, uint256[${k}] calldata input) external returns (bool) {
        require(validRoots[input[0]], "Invalid root");
        bool proofValid = IGroth16ProofVerifier(verifier).verifyProof(a, b, c, input);
        require(proofValid, "Invalid proof");
        emit CredentialVerified(input[0]);
        return true;
    }
}
`;
  if (backend === 'plonk') return `// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;
import "./CredentialManagerBase.sol";
interface IPlonkProofVerifier { function verifyProof(uint256[24] calldata _proof, uint256[${k}] calldata _pubSignals) external view returns (bool); }
contract CredentialManagerPlonkK${k} is CredentialManagerBase {
    constructor(address _verifier) CredentialManagerBase(_verifier) {}
    function verifyCredential(uint256[24] calldata proof, uint256[${k}] calldata input) external returns (bool) {
        require(validRoots[input[0]], "Invalid root");
        bool proofValid = IPlonkProofVerifier(verifier).verifyProof(proof, input);
        require(proofValid, "Invalid proof");
        emit CredentialVerified(input[0]);
        return true;
    }
}
`;
  if (backend === 'fflonk') return `// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;
import "./CredentialManagerBase.sol";
interface IFflonkProofVerifier { function verifyProof(bytes32[24] calldata proof, uint256[${k}] calldata pubSignals) external view returns (bool); }
contract CredentialManagerFflonkK${k} is CredentialManagerBase {
    constructor(address _verifier) CredentialManagerBase(_verifier) {}
    function verifyCredential(bytes32[24] calldata proof, uint256[${k}] calldata input) external returns (bool) {
        require(validRoots[input[0]], "Invalid root");
        bool proofValid = IFflonkProofVerifier(verifier).verifyProof(proof, input);
        require(proofValid, "Invalid proof");
        emit CredentialVerified(input[0]);
        return true;
    }
}
`;
}
function sources(circuit, backend, k) {
  const vname = { groth16: 'Groth16Verifier', plonk: 'PlonkVerifier', fflonk: 'FflonkVerifier' }[backend];
  const vsrc = fs.readFileSync(path.join(process.env.HOME, 'p0/circ/keys', circuit, `${backend}Verifier.sol`), 'utf8');
  const mname = `CredentialManager${backend[0].toUpperCase() + backend.slice(1)}K${k}`;
  return { vname, mname, extra: { 'contracts/p0/Verifier.sol': { content: vsrc }, 'contracts/p0/CredentialManagerBase.sol': { content: BASE }, 'contracts/p0/Manager.sol': { content: manager(backend, k) } } };
}
module.exports = { manager, sources };
