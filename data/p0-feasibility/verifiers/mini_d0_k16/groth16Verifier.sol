// SPDX-License-Identifier: GPL-3.0
/*
    Copyright 2021 0KIMS association.

    This file is generated with [snarkJS](https://github.com/iden3/snarkjs).

    snarkJS is a free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    snarkJS is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.

    You should have received a copy of the GNU General Public License
    along with snarkJS. If not, see <https://www.gnu.org/licenses/>.
*/

pragma solidity >=0.7.0 <0.9.0;

contract Groth16Verifier {
    // Scalar field size
    uint256 constant r    = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
    // Base field size
    uint256 constant q   = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    // Verification Key data
    uint256 constant alphax  = 8827857762582705054404597661667644282232566277997863119052380782425064271368;
    uint256 constant alphay  = 15654631540125952645527808415365819994943364758920885904379965035702651990847;
    uint256 constant betax1  = 5570534694044507182591362464588960283107834665835237601623560390893908095405;
    uint256 constant betax2  = 19458784894872516135988576131208179974127883176317914181367021204942225069648;
    uint256 constant betay1  = 21341427832148363947884980825962342560882396010353440880555837592515128878252;
    uint256 constant betay2  = 7757373646905809319286843703251653024365514158337423950755039692392986818085;
    uint256 constant gammax1 = 11559732032986387107991004021392285783925812861821192530917403151452391805634;
    uint256 constant gammax2 = 10857046999023057135944570762232829481370756359578518086990519993285655852781;
    uint256 constant gammay1 = 4082367875863433681332203403145435568316851327593401208105741076214120093531;
    uint256 constant gammay2 = 8495653923123431417604973247489272438418190587263600148770280649306958101930;
    uint256 constant deltax1 = 11559732032986387107991004021392285783925812861821192530917403151452391805634;
    uint256 constant deltax2 = 10857046999023057135944570762232829481370756359578518086990519993285655852781;
    uint256 constant deltay1 = 4082367875863433681332203403145435568316851327593401208105741076214120093531;
    uint256 constant deltay2 = 8495653923123431417604973247489272438418190587263600148770280649306958101930;

    
    uint256 constant IC0x = 16236819850269572139726019439910861061013035303229977967857829926241578420902;
    uint256 constant IC0y = 13543303547839674183770141484542155808803094367210098965898934029542972570860;
    
    uint256 constant IC1x = 16932619408948640608222995259511989380346054617313933967792295681061585153419;
    uint256 constant IC1y = 8554667135086346910220694240631605557517386111173186827906660692614497676691;
    
    uint256 constant IC2x = 12944594574514952941445896070564059741998982186783096574812855266526931127207;
    uint256 constant IC2y = 2336406724359383322884742456654700048648728391950620873585918576729553483096;
    
    uint256 constant IC3x = 4991000783335370252556543582981459927258868132218419760321644084073252196077;
    uint256 constant IC3y = 16699590911010354270275356992588517661948473891626430003468851658753063466202;
    
    uint256 constant IC4x = 5219126824798511336006611558704893490264136227469220352826019092858916780742;
    uint256 constant IC4y = 18269047692163827241749285380350151193899646874251746142185041156401916896084;
    
    uint256 constant IC5x = 5273532306153589166990416969733685224683774970422603570768740807680334808757;
    uint256 constant IC5y = 11542451082804613872059800115010164339399555101441719062663039586665109420999;
    
    uint256 constant IC6x = 7062573039770454399015123205062241799375047224022800624167966079050922875304;
    uint256 constant IC6y = 15839152084942062249564398328041316522613625302144910187375606811695284756253;
    
    uint256 constant IC7x = 16669163453119221789120030366021207623790662099215107879433061108350309153495;
    uint256 constant IC7y = 18485255837168826395244478558195052371991926407430239501217257438720801871899;
    
    uint256 constant IC8x = 14134344778059602795900388894750732471335519785505070746115480556303856549704;
    uint256 constant IC8y = 4849632228999100166047518003730300847959727401432303675898938213484300146992;
    
    uint256 constant IC9x = 15941377135557648064781327954324767090251867904099708244312889653435170454222;
    uint256 constant IC9y = 13923038304301402559237463302375460113340750355923757681764472561744638924395;
    
    uint256 constant IC10x = 18718374277074451312383513941466545973272972794884008371498377662363196930556;
    uint256 constant IC10y = 20694247536147404756362773770953565899624395775485513297775507859420154609097;
    
    uint256 constant IC11x = 10909737514848726129816693952862001237347056231198221652128175572901482511002;
    uint256 constant IC11y = 8273128662750140813228267726363687718705006437554029343055049087453308164007;
    
    uint256 constant IC12x = 4190514112177966100817622393402502917671293259202682695377201146342651172932;
    uint256 constant IC12y = 1414652422065780834950537967650057082774325533833949860693109872461942143267;
    
    uint256 constant IC13x = 4701700876091991360254610098120628784236195642408505689940295819313280470734;
    uint256 constant IC13y = 1220800369678225499208934051137100989992682706742854604483732323567272308877;
    
    uint256 constant IC14x = 18947800982531638495293355292738031228310114083044885069241982573866880890945;
    uint256 constant IC14y = 15996868757932729821660341253082030756453883842905722655491686060396023386330;
    
    uint256 constant IC15x = 8243850028903053629483365452064728045849106842656965025779508256299232453173;
    uint256 constant IC15y = 20965957181719021499417243705180087013803642451367259792652762337132114227128;
    
    uint256 constant IC16x = 6044558604789541164016736018181769260611415421380771669126677060714627553655;
    uint256 constant IC16y = 16360304705855523427296522009879091347056012729453200749483489468460794802873;
    
 
    // Memory data
    uint16 constant pVk = 0;
    uint16 constant pPairing = 128;

    uint16 constant pLastMem = 896;

    function verifyProof(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[16] calldata _pubSignals) public view returns (bool) {
        assembly {
            function checkField(v) {
                if iszero(lt(v, r)) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }
            
            // G1 function to multiply a G1 value(x,y) to value in an address
            function g1_mulAccC(pR, x, y, s) {
                let success
                let mIn := mload(0x40)
                mstore(mIn, x)
                mstore(add(mIn, 32), y)
                mstore(add(mIn, 64), s)

                success := staticcall(sub(gas(), 2000), 7, mIn, 96, mIn, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }

                mstore(add(mIn, 64), mload(pR))
                mstore(add(mIn, 96), mload(add(pR, 32)))

                success := staticcall(sub(gas(), 2000), 6, mIn, 128, pR, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }

            function checkPairing(pA, pB, pC, pubSignals, pMem) -> isOk {
                let _pPairing := add(pMem, pPairing)
                let _pVk := add(pMem, pVk)

                mstore(_pVk, IC0x)
                mstore(add(_pVk, 32), IC0y)

                // Compute the linear combination vk_x
                
                g1_mulAccC(_pVk, IC1x, IC1y, calldataload(add(pubSignals, 0)))
                
                g1_mulAccC(_pVk, IC2x, IC2y, calldataload(add(pubSignals, 32)))
                
                g1_mulAccC(_pVk, IC3x, IC3y, calldataload(add(pubSignals, 64)))
                
                g1_mulAccC(_pVk, IC4x, IC4y, calldataload(add(pubSignals, 96)))
                
                g1_mulAccC(_pVk, IC5x, IC5y, calldataload(add(pubSignals, 128)))
                
                g1_mulAccC(_pVk, IC6x, IC6y, calldataload(add(pubSignals, 160)))
                
                g1_mulAccC(_pVk, IC7x, IC7y, calldataload(add(pubSignals, 192)))
                
                g1_mulAccC(_pVk, IC8x, IC8y, calldataload(add(pubSignals, 224)))
                
                g1_mulAccC(_pVk, IC9x, IC9y, calldataload(add(pubSignals, 256)))
                
                g1_mulAccC(_pVk, IC10x, IC10y, calldataload(add(pubSignals, 288)))
                
                g1_mulAccC(_pVk, IC11x, IC11y, calldataload(add(pubSignals, 320)))
                
                g1_mulAccC(_pVk, IC12x, IC12y, calldataload(add(pubSignals, 352)))
                
                g1_mulAccC(_pVk, IC13x, IC13y, calldataload(add(pubSignals, 384)))
                
                g1_mulAccC(_pVk, IC14x, IC14y, calldataload(add(pubSignals, 416)))
                
                g1_mulAccC(_pVk, IC15x, IC15y, calldataload(add(pubSignals, 448)))
                
                g1_mulAccC(_pVk, IC16x, IC16y, calldataload(add(pubSignals, 480)))
                

                // -A
                mstore(_pPairing, calldataload(pA))
                mstore(add(_pPairing, 32), mod(sub(q, calldataload(add(pA, 32))), q))

                // B
                mstore(add(_pPairing, 64), calldataload(pB))
                mstore(add(_pPairing, 96), calldataload(add(pB, 32)))
                mstore(add(_pPairing, 128), calldataload(add(pB, 64)))
                mstore(add(_pPairing, 160), calldataload(add(pB, 96)))

                // alpha1
                mstore(add(_pPairing, 192), alphax)
                mstore(add(_pPairing, 224), alphay)

                // beta2
                mstore(add(_pPairing, 256), betax1)
                mstore(add(_pPairing, 288), betax2)
                mstore(add(_pPairing, 320), betay1)
                mstore(add(_pPairing, 352), betay2)

                // vk_x
                mstore(add(_pPairing, 384), mload(add(pMem, pVk)))
                mstore(add(_pPairing, 416), mload(add(pMem, add(pVk, 32))))


                // gamma2
                mstore(add(_pPairing, 448), gammax1)
                mstore(add(_pPairing, 480), gammax2)
                mstore(add(_pPairing, 512), gammay1)
                mstore(add(_pPairing, 544), gammay2)

                // C
                mstore(add(_pPairing, 576), calldataload(pC))
                mstore(add(_pPairing, 608), calldataload(add(pC, 32)))

                // delta2
                mstore(add(_pPairing, 640), deltax1)
                mstore(add(_pPairing, 672), deltax2)
                mstore(add(_pPairing, 704), deltay1)
                mstore(add(_pPairing, 736), deltay2)


                let success := staticcall(sub(gas(), 2000), 8, _pPairing, 768, _pPairing, 0x20)

                isOk := and(success, mload(_pPairing))
            }

            let pMem := mload(0x40)
            mstore(0x40, add(pMem, pLastMem))

            // Validate that all evaluations ∈ F
            
            checkField(calldataload(add(_pubSignals, 0)))
            
            checkField(calldataload(add(_pubSignals, 32)))
            
            checkField(calldataload(add(_pubSignals, 64)))
            
            checkField(calldataload(add(_pubSignals, 96)))
            
            checkField(calldataload(add(_pubSignals, 128)))
            
            checkField(calldataload(add(_pubSignals, 160)))
            
            checkField(calldataload(add(_pubSignals, 192)))
            
            checkField(calldataload(add(_pubSignals, 224)))
            
            checkField(calldataload(add(_pubSignals, 256)))
            
            checkField(calldataload(add(_pubSignals, 288)))
            
            checkField(calldataload(add(_pubSignals, 320)))
            
            checkField(calldataload(add(_pubSignals, 352)))
            
            checkField(calldataload(add(_pubSignals, 384)))
            
            checkField(calldataload(add(_pubSignals, 416)))
            
            checkField(calldataload(add(_pubSignals, 448)))
            
            checkField(calldataload(add(_pubSignals, 480)))
            

            // Validate all evaluations
            let isValid := checkPairing(_pA, _pB, _pC, _pubSignals, pMem)

            mstore(0, isValid)
             return(0, 0x20)
         }
     }
 }
