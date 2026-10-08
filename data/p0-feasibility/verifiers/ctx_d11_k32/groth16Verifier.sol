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

    
    uint256 constant IC0x = 7419704759888405239175374913966504904165830798333661554253120259316408212222;
    uint256 constant IC0y = 14313164597147220219317549220798518602810005115087636837813232192088227335624;
    
    uint256 constant IC1x = 6691812770343580941754220173568049954647819969658806194630557497510917115414;
    uint256 constant IC1y = 12848182471226682192966347541615856455841530615138140527640658782365433950534;
    
    uint256 constant IC2x = 4113754526519596862212615999141403554747336951279692490846144247596086665072;
    uint256 constant IC2y = 12094947600853006874885667489375766956878447864149463900820085478508479511425;
    
    uint256 constant IC3x = 20877062506029601457746432031976158921479316437210661709604496243527257286852;
    uint256 constant IC3y = 14553489210567112387331412191202184143496206285320157156352744241565483259439;
    
    uint256 constant IC4x = 3115757819738707209880997614631350509740187208942057082267397320658486308533;
    uint256 constant IC4y = 14499049371341974464134037386417219372601812551560946245118193359556103020900;
    
    uint256 constant IC5x = 17743396176029545977030908157033500441332124684344745407918930904977747434002;
    uint256 constant IC5y = 12119419743142528693311072386331756217650168136652069893282514615546135267281;
    
    uint256 constant IC6x = 18597841312682002619734709046219989924013467319195301565231741393776943318123;
    uint256 constant IC6y = 672326982445790093148984691789484863180863814137114516429169131557159999233;
    
    uint256 constant IC7x = 8426207516875132665304094260249090666837936301891261103044648742157457196526;
    uint256 constant IC7y = 8752332554779746544878966017483463904236560915093793968312195394317707762791;
    
    uint256 constant IC8x = 11063114177475974611469232601909194459946218295142414940305332846162626327704;
    uint256 constant IC8y = 6666590544698297166010694424635642968224601662245975459417468159963327997431;
    
    uint256 constant IC9x = 6760333348290676361607047339028863376269348967369212367619944216384236477609;
    uint256 constant IC9y = 21854395589821189923185561245113082930913419706782134002486532433275278887242;
    
    uint256 constant IC10x = 17669523215343979427340571971280961051973732156514566779863469066320678963595;
    uint256 constant IC10y = 2559145262727134093409135165911352900263953172166722241475357631720309080753;
    
    uint256 constant IC11x = 11791914276292022433877351055991891298512376543259901243689710681968923911827;
    uint256 constant IC11y = 2521126920227925615847881091015968276710432539344961547672852440573393499916;
    
    uint256 constant IC12x = 2615877185751570226726502401768156453320262938301691699470655730955503977843;
    uint256 constant IC12y = 14342248259519116540817941987973922915440548464655619899673317476324578761906;
    
    uint256 constant IC13x = 10421158864268536684578393683887405411444768667961107192555426453699201910843;
    uint256 constant IC13y = 8375405721775700666305088512075888545239326346432902076627045522944518643414;
    
    uint256 constant IC14x = 17070181800272041708421172674727313858188198944981494896719091454060627219993;
    uint256 constant IC14y = 9385389157228191548574064050050196963998602570237628204109993221214425969823;
    
    uint256 constant IC15x = 4046519128151988224498291400478559508453756355783038114680480713316911823395;
    uint256 constant IC15y = 11114820388927842320849958638159716266015673696932760318679665720331313751748;
    
    uint256 constant IC16x = 2425227678242430532167946801271388707938449687927675449298419749393566327727;
    uint256 constant IC16y = 6943289048968579237480703758716173026024206679334222509583094146323962017602;
    
    uint256 constant IC17x = 4884832646270221015760788895927699301848619767917303110235614347459033483080;
    uint256 constant IC17y = 7102690170575467372136526134660841013703206054954384683186436424864327332429;
    
    uint256 constant IC18x = 8428883669585046944490606212221845070128202450623300151004419789351425497530;
    uint256 constant IC18y = 13912995262103176683518932346610483161247704961960439652383471881517962781339;
    
    uint256 constant IC19x = 15105356600013418695090406173416568519446534536477697080656373475487979554342;
    uint256 constant IC19y = 14086727790580665614700468027205353162503857110353147276908402794017226297251;
    
    uint256 constant IC20x = 4050985596033029238747070523296014238801506888101197249577949375680627917289;
    uint256 constant IC20y = 5263530006493310069066212691207673843507358541042816997003936449005165193913;
    
    uint256 constant IC21x = 8303081263865002533800446513485803958504737778492096872253875647768784573383;
    uint256 constant IC21y = 12955937823504399776241300388662975674026476541638417229711689054795205820625;
    
    uint256 constant IC22x = 17257887923450607132404557658806801572690557931781376329766874518204986632059;
    uint256 constant IC22y = 15446095510107910262222120649473143561583724078272197079273921521877948664086;
    
    uint256 constant IC23x = 13403324983105608785803136971300169459099438397904701589537265370088076807259;
    uint256 constant IC23y = 4285593803278725442506583122506059102176154699511083268744552332430388528140;
    
    uint256 constant IC24x = 13762489006126212715877263253092933706416196949904186202222733339968775851659;
    uint256 constant IC24y = 20948108654543158844815433516514858332024278449421020430747765165348339144450;
    
    uint256 constant IC25x = 20297252380955238614722196705881993060911144103274139259704033305584164030581;
    uint256 constant IC25y = 8935819747250579971877137183450228311053205231618612017794395360293526931124;
    
    uint256 constant IC26x = 10050048251227405306848493154032419590913698114165253413925711991530665413663;
    uint256 constant IC26y = 2168238181606390737362473730419125162058606424868805050351881939516667780070;
    
    uint256 constant IC27x = 15330945682584080050631351674782458212466765942222301352939345658579850947109;
    uint256 constant IC27y = 10918260147732385254758792872285774002272101976517109471921799683443726495093;
    
    uint256 constant IC28x = 20956119268264245554765414408359466848992755241272938837845166485751627954934;
    uint256 constant IC28y = 1452451399829689384557819687006380015382376956665389434416331593492323146175;
    
    uint256 constant IC29x = 8384158398561738734704160783845114599904864774401120828552448163317510708375;
    uint256 constant IC29y = 2773389233247133582884823441914737411870040903631020513428931341907221976966;
    
    uint256 constant IC30x = 14413115574189522054827794690217864990190199728952028426554694677684592390029;
    uint256 constant IC30y = 21702094861574115259705787628297999407663351000443471161071808964306090005505;
    
    uint256 constant IC31x = 815006327914373049343896570268649615068864607997733968863858195983885477654;
    uint256 constant IC31y = 9085116446987319878808417018913028889312337087890619039387198190355978412115;
    
    uint256 constant IC32x = 1196982745693284362305570606966778689349405264305806259939073241324744800168;
    uint256 constant IC32y = 14974538111363119249719904828081558670844908488525312955933716673890043642078;
    
 
    // Memory data
    uint16 constant pVk = 0;
    uint16 constant pPairing = 128;

    uint16 constant pLastMem = 896;

    function verifyProof(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[32] calldata _pubSignals) public view returns (bool) {
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
                
                g1_mulAccC(_pVk, IC17x, IC17y, calldataload(add(pubSignals, 512)))
                
                g1_mulAccC(_pVk, IC18x, IC18y, calldataload(add(pubSignals, 544)))
                
                g1_mulAccC(_pVk, IC19x, IC19y, calldataload(add(pubSignals, 576)))
                
                g1_mulAccC(_pVk, IC20x, IC20y, calldataload(add(pubSignals, 608)))
                
                g1_mulAccC(_pVk, IC21x, IC21y, calldataload(add(pubSignals, 640)))
                
                g1_mulAccC(_pVk, IC22x, IC22y, calldataload(add(pubSignals, 672)))
                
                g1_mulAccC(_pVk, IC23x, IC23y, calldataload(add(pubSignals, 704)))
                
                g1_mulAccC(_pVk, IC24x, IC24y, calldataload(add(pubSignals, 736)))
                
                g1_mulAccC(_pVk, IC25x, IC25y, calldataload(add(pubSignals, 768)))
                
                g1_mulAccC(_pVk, IC26x, IC26y, calldataload(add(pubSignals, 800)))
                
                g1_mulAccC(_pVk, IC27x, IC27y, calldataload(add(pubSignals, 832)))
                
                g1_mulAccC(_pVk, IC28x, IC28y, calldataload(add(pubSignals, 864)))
                
                g1_mulAccC(_pVk, IC29x, IC29y, calldataload(add(pubSignals, 896)))
                
                g1_mulAccC(_pVk, IC30x, IC30y, calldataload(add(pubSignals, 928)))
                
                g1_mulAccC(_pVk, IC31x, IC31y, calldataload(add(pubSignals, 960)))
                
                g1_mulAccC(_pVk, IC32x, IC32y, calldataload(add(pubSignals, 992)))
                

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
            
            checkField(calldataload(add(_pubSignals, 512)))
            
            checkField(calldataload(add(_pubSignals, 544)))
            
            checkField(calldataload(add(_pubSignals, 576)))
            
            checkField(calldataload(add(_pubSignals, 608)))
            
            checkField(calldataload(add(_pubSignals, 640)))
            
            checkField(calldataload(add(_pubSignals, 672)))
            
            checkField(calldataload(add(_pubSignals, 704)))
            
            checkField(calldataload(add(_pubSignals, 736)))
            
            checkField(calldataload(add(_pubSignals, 768)))
            
            checkField(calldataload(add(_pubSignals, 800)))
            
            checkField(calldataload(add(_pubSignals, 832)))
            
            checkField(calldataload(add(_pubSignals, 864)))
            
            checkField(calldataload(add(_pubSignals, 896)))
            
            checkField(calldataload(add(_pubSignals, 928)))
            
            checkField(calldataload(add(_pubSignals, 960)))
            
            checkField(calldataload(add(_pubSignals, 992)))
            

            // Validate all evaluations
            let isValid := checkPairing(_pA, _pB, _pC, _pubSignals, pMem)

            mstore(0, isValid)
             return(0, 0x20)
         }
     }
 }
