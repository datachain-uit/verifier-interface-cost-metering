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
    uint256 constant deltax1 = 2681093956523553579009250172541358833150360017575043424692747045246856992314;
    uint256 constant deltax2 = 7594113891545934128333155442110538268083937113975612603797978161995166380284;
    uint256 constant deltay1 = 15239873682468165205937134548380098522808500669840951295221467278310336532762;
    uint256 constant deltay2 = 18774367475144404487361207923209438606623794403043454097521248550051610006571;

    
    uint256 constant IC0x = 6318870346731966095918521539781924534981160184963194023177658686071293988285;
    uint256 constant IC0y = 16470403147705822027314361375292481148270519192158155788744844341150471303178;
    
    uint256 constant IC1x = 17484069959700451801938623152825149318127082370223059608398188051651572110151;
    uint256 constant IC1y = 9394904003918787915696428693723402470484790307888969773498886798958741662793;
    
    uint256 constant IC2x = 5602152645394486163925477195797656849064526094383165208185488760578422071565;
    uint256 constant IC2y = 12867797982004959998802076040361495495134800072845520648619229842505137726347;
    
    uint256 constant IC3x = 13794072677955683593546585021396938677877491341819531900594658131209620487721;
    uint256 constant IC3y = 19226098572792019422473196838971651180541637234029274791226789596782318448369;
    
    uint256 constant IC4x = 16803345319544446936665535577112725826333457149759174723270904178113148140806;
    uint256 constant IC4y = 12924041747825986254280252620398283740155197850848321561780112369582389433960;
    
    uint256 constant IC5x = 8779718430860351643104499690223560567085622079483809993176474921600241429606;
    uint256 constant IC5y = 54665776068623743122108735811754860074919201949807220626492026527279031502;
    
    uint256 constant IC6x = 12178233960683051314426919051679789025790812455386098560958045848279800767277;
    uint256 constant IC6y = 3672989107030049779005555011863677304168805323231356131639411213951949889176;
    
    uint256 constant IC7x = 18339476175835297952858348702975773372224034174266428805872494528859353804318;
    uint256 constant IC7y = 20278771534916366802116637242414546375180191110621512198267823793844241676800;
    
    uint256 constant IC8x = 3605013893609486803419623914389337673596619991470290770873131267433908571744;
    uint256 constant IC8y = 5657176672270643600049150807357170798577852723617910447346395168077555526670;
    
    uint256 constant IC9x = 16007928626843911342683588727951045668867928218848991870802558406833377783743;
    uint256 constant IC9y = 9315190212293617945384733658022017037524262066879328811613691736986201890209;
    
    uint256 constant IC10x = 7217900923592722963862995647725217997914418160028922527349255182653679063592;
    uint256 constant IC10y = 1967654979798697022275655637466698417657813318806956176967762249529113828283;
    
    uint256 constant IC11x = 20896520729500605303068135042441070256793415545532232734852681632870777607434;
    uint256 constant IC11y = 20683443522108426027595210906245550267714902052035024070638204137312184374148;
    
    uint256 constant IC12x = 6642238918115777253625974045914149502907230941671327991421357816585690756345;
    uint256 constant IC12y = 12777684852175269853140769865431882346078227828827670051433915891493566707031;
    
    uint256 constant IC13x = 17846862322562397855309346809744024006854502048638020334900071466508048729420;
    uint256 constant IC13y = 9233935221069212052681163344622721816427236943861799404801011970737308010183;
    
    uint256 constant IC14x = 17617000968106580793769832264991839623321603256033083029410660335471653012072;
    uint256 constant IC14y = 3348695207978688415016190183302317324002388411954658091928628639979470305923;
    
    uint256 constant IC15x = 20260618379796345614927637110918239617380613275580208409301229262019237884400;
    uint256 constant IC15y = 10851410792402511799489958121473151093501614941428484590156952733542786130097;
    
    uint256 constant IC16x = 12728841466029394687296344283265436400049963613063740884686978512423851431489;
    uint256 constant IC16y = 12865481339259114731397721545513841637747169646825486420228345946253607200557;
    
    uint256 constant IC17x = 9224312078357363572851274343681144428901062368073642776568137541193448828785;
    uint256 constant IC17y = 16112653673064196394217077792732893336404533438602335133143023291608054085394;
    
    uint256 constant IC18x = 4710153760359175992590268460488972835738233753543672664920494974277099166734;
    uint256 constant IC18y = 13701522374334683931274698871499506195860672738055629881672088400913593457291;
    
    uint256 constant IC19x = 9239292563864444067439001951479316161447537683271759911498922445225884720683;
    uint256 constant IC19y = 3526916266277613560286896122782528426978823484866692714312352746223962541027;
    
    uint256 constant IC20x = 6905040350191600769503921083652870792394958314451382596110668429050282541271;
    uint256 constant IC20y = 1148168570758174158429773380289957681775384434759068329302283545367234693481;
    
    uint256 constant IC21x = 16845940446484076700946837724763486211044976375998308910896503463333322166035;
    uint256 constant IC21y = 11465073560016670038380229194964503466199637063771534923101133314110121482514;
    
    uint256 constant IC22x = 3230719871162273869811546759764157849233845285876125279463602508508090919036;
    uint256 constant IC22y = 3273426305832367898071513054719233413603605770757388215674165310290801661137;
    
    uint256 constant IC23x = 20891914768469502425667711910402232032966457504007291494895270708361668001513;
    uint256 constant IC23y = 10548095992168709294789455195795212475124268404813303871150727874542374781987;
    
    uint256 constant IC24x = 19911744811455969118748062873736649402295087902048772456044870733159474770413;
    uint256 constant IC24y = 18726083128526974392041142974069172923163910296876268291137584946190427360658;
    
 
    // Memory data
    uint16 constant pVk = 0;
    uint16 constant pPairing = 128;

    uint16 constant pLastMem = 896;

    function verifyProof(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[24] calldata _pubSignals) public view returns (bool) {
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
            

            // Validate all evaluations
            let isValid := checkPairing(_pA, _pB, _pC, _pubSignals, pMem)

            mstore(0, isValid)
             return(0, 0x20)
         }
     }
 }
