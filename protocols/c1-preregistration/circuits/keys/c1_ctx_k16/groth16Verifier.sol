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
    uint256 constant deltax1 = 554922257710505653534232027421401430030998179966136994042512043274552446839;
    uint256 constant deltax2 = 4152715131280878242749490017358538613630299515651182354805314311014366342689;
    uint256 constant deltay1 = 3503730872860781977741165138244843895568208900543427783639270973803532274210;
    uint256 constant deltay2 = 10535752118463390734112923102916232026048101300779751667908027037016271589007;

    
    uint256 constant IC0x = 1419331484064592743116006490631498338846117137849439152460304591055810444782;
    uint256 constant IC0y = 4368022413714659836553293952998109953172945633275017151444650031178979157853;
    
    uint256 constant IC1x = 16561327335977012284520277569738039009170533652654195052038625280145576924152;
    uint256 constant IC1y = 10849295052872952097559020769212727354846714379194157362447601802256193042374;
    
    uint256 constant IC2x = 1672517428865579537484531134355439386966503410933859233751902853636355685055;
    uint256 constant IC2y = 20168610976073706184628029624298337885149451896372801825534589766665579062759;
    
    uint256 constant IC3x = 11137573409417339855924423452879154016065961281117833593628471547140436418918;
    uint256 constant IC3y = 8136670773225980128330890958200012959461648974999059693611869641678473618247;
    
    uint256 constant IC4x = 13735434155687563027100887854576480626786361007038786367221555838573375391237;
    uint256 constant IC4y = 753198203623430015158791895202412355014537587160758950050539359497968159418;
    
    uint256 constant IC5x = 8645816037739170518885432182278393336916865119748925917970554194221468992979;
    uint256 constant IC5y = 20629830068766568775380062099072343128139465043967434933112442133950935303337;
    
    uint256 constant IC6x = 20292460359232890606150546429082252672771899119977152490684997423917134970188;
    uint256 constant IC6y = 5548569309038708199715443180110828600855849894999740675872712506841155969408;
    
    uint256 constant IC7x = 6175536157337433568147090785445831072320568815113857915250767334221865141988;
    uint256 constant IC7y = 15619833353533713470373688326351530037671726897039548717439568212921613532948;
    
    uint256 constant IC8x = 1584293951575440995711942465534691166814453990726458364975919141004819892107;
    uint256 constant IC8y = 13787693177924489707556626066531226540966969362242383158327023677842075193161;
    
    uint256 constant IC9x = 15781861815877709516031884545872802579186514872252352047395582045635734574734;
    uint256 constant IC9y = 17672695889251315329906433973225845086128031186753526322761849186677334456296;
    
    uint256 constant IC10x = 5154317571540989474722778136304963534715418249391434751303306058377239759368;
    uint256 constant IC10y = 14265741163956246028198692563101051028049258309522882964701858104341953376753;
    
    uint256 constant IC11x = 12401673858937965378409434985775975846553606320821728969755832972000696654083;
    uint256 constant IC11y = 5170468822115735038695332091813187037058100986214909104227801894663276287378;
    
    uint256 constant IC12x = 11260382141569890861547056388098950787629237078304297640344648146560992081882;
    uint256 constant IC12y = 5546592494134260686243515453257646930345707663943673935449305995630528177967;
    
    uint256 constant IC13x = 3596324241752473680290960517100558067754157092667339972229470713983447381979;
    uint256 constant IC13y = 13941394973697627267362401053895074390249460459804035956515864720260378130872;
    
    uint256 constant IC14x = 6158730963168218155642790426469483641681423791608816400059457450129959900172;
    uint256 constant IC14y = 14529281229656181584258863609716387807987526706215566389939351503921319566717;
    
    uint256 constant IC15x = 21576503119601768066074973098992770548121085024051494927634139614706910534844;
    uint256 constant IC15y = 8245026183436372112626727889706995960197743757315440257944211746514274520517;
    
    uint256 constant IC16x = 6165067534404017252137441069214396242019539374061383395125493439445349820741;
    uint256 constant IC16y = 11577100427821431503223190144492015928413427645620986016715660885797779880902;
    
 
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
