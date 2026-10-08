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

    
    uint256 constant IC0x = 1186873111606972252784033131367413575988264407054352185405198446522183055438;
    uint256 constant IC0y = 687685271935354894009243433468745583816714434437036288855418175875375369380;
    
    uint256 constant IC1x = 556459041020806290931660401787329218332624767060013618128822135776360730110;
    uint256 constant IC1y = 6460193055101584956460055207852760262999815612950963503630263230919645730432;
    
    uint256 constant IC2x = 7607242443609149841422593450654727660203992891922163877607588496422407434068;
    uint256 constant IC2y = 10378309735311257450556737586414216288987983220636044069760712385020555799829;
    
    uint256 constant IC3x = 4150669787568639238947903355472476741076688005538994621725154571635423283526;
    uint256 constant IC3y = 2941356998919048912349010969689439793026261598883495947590099017327072746498;
    
    uint256 constant IC4x = 14846273530032179824711302637666087877342677039358368926798325489645603637036;
    uint256 constant IC4y = 15976515700669813340209556710082329913062213949482519780712635456521854234275;
    
    uint256 constant IC5x = 14629020487543720843868491788950026285277673243010259437805347529168207166765;
    uint256 constant IC5y = 8081515795523523886237572216668291034003624859079772071139535800268119956348;
    
    uint256 constant IC6x = 19901768505264282101329062653374403961986062842141992536918222608342191091550;
    uint256 constant IC6y = 3631501457229733941700062030184456245023932105908399644226739764249414145306;
    
    uint256 constant IC7x = 9705487809147939897863697070806181688139702121110080957086798659584551958683;
    uint256 constant IC7y = 7316777633409735887772928492540077626705190466356642658093144230884597505603;
    
    uint256 constant IC8x = 16609983400480406212874236251099037033852430759535628280216929594419091418863;
    uint256 constant IC8y = 12693146052130963113301460243303696294833636244229422873308736394718252237896;
    
    uint256 constant IC9x = 13772016210445692499424794180753837085848535031875185384819873558183454750653;
    uint256 constant IC9y = 18829040331597746645578756350121478895926311852253658359330626461562472162360;
    
    uint256 constant IC10x = 10473195608855295423623323006554987526402287202744652073102485477362431072686;
    uint256 constant IC10y = 3796497486285596395851940773210469978041493236335641470845318850523331797117;
    
    uint256 constant IC11x = 1908347720458602487509060832470749989026316499713002764015207206836644140559;
    uint256 constant IC11y = 4893642605429380934060510700794060743756015213344276674160245709786983848907;
    
    uint256 constant IC12x = 18020243355444551348266759673129622510248929290520631602656105200920377617760;
    uint256 constant IC12y = 16728050053199367241142325228864558062095941200578850131527778449231802812023;
    
    uint256 constant IC13x = 3865315357684000727253262341182518810977938006701106201385657583219262269541;
    uint256 constant IC13y = 11119824403480154672043896052559913851503053717744426376730129943333081172183;
    
    uint256 constant IC14x = 18514497460396377336530912565945775193591681122579525382830467602152791875351;
    uint256 constant IC14y = 3133693845080948415947499799394492543137455058607933700580779174820023385468;
    
    uint256 constant IC15x = 5300134334401719886160409315302335408802642746503346891234962292365092593441;
    uint256 constant IC15y = 8141653988032895421667545897018723701396457979534572396554878930554828546706;
    
    uint256 constant IC16x = 14765670083653096461475992144978400812274389335061268712646905345653925281563;
    uint256 constant IC16y = 1324916547406024181214035288940810204075899492780383542839814225466756691027;
    
    uint256 constant IC17x = 17184884950412052006578745767941166771032508562614781093595581637084049977792;
    uint256 constant IC17y = 85264398943463951665542902354707715893970383372029746189581734946579726833;
    
    uint256 constant IC18x = 405650104283939993826530878199971811280940222461208965324682814636877476630;
    uint256 constant IC18y = 18636845162234727259415585501306165533466959414745813146229732717753003070977;
    
    uint256 constant IC19x = 17697097009832819366724057221481016969289036515598257906880788611010692460810;
    uint256 constant IC19y = 15257393781672385235719400545127870612560528065610222109323455825265518408222;
    
    uint256 constant IC20x = 14463709356171033864379313555508903849407576511207421375013351339164728789961;
    uint256 constant IC20y = 17840573439313868472893211575198875365620011106574535158667288248781147177920;
    
    uint256 constant IC21x = 8484429091060384808283302868162336409946063626133426835866137337989971899444;
    uint256 constant IC21y = 14623894175892366194388626253055101660793380880271021754721662414979893273856;
    
    uint256 constant IC22x = 10237290548043238957491266257525230957809070686320476698174716201747396948945;
    uint256 constant IC22y = 3112826856793014464334762262472074356228777648785069250762165652289557298547;
    
    uint256 constant IC23x = 17323181716528153190201735041819786510355682599032365078335992592861978536489;
    uint256 constant IC23y = 13256229490713861431192839326682667584343555062618780651920416159826342746355;
    
    uint256 constant IC24x = 19962143648985078849999565734330472164874986368821174534456459064309689514391;
    uint256 constant IC24y = 3134359272821423432737617251531758490291521934451882514071933902701280846470;
    
    uint256 constant IC25x = 8242481013978360784283683054412228512641847343034608247246169883577486376006;
    uint256 constant IC25y = 16983261762076066530401558597587645784849660423749196192336399343206913920946;
    
    uint256 constant IC26x = 346491091439665316521844892466008781723883186976294731750005506279683656663;
    uint256 constant IC26y = 18284024224684979566129790908012395865034299248450508734146289356477065483606;
    
    uint256 constant IC27x = 21454726240096014272384253549474237856263044905546646313990737579782213736621;
    uint256 constant IC27y = 7172798947791942669652933458283703597354639161236452720503393282623135413898;
    
    uint256 constant IC28x = 15266490742129208447279599285110771842413992197940581262683475595892369419935;
    uint256 constant IC28y = 991233872421505651398372815361353347140294965424273726126095989402082268424;
    
    uint256 constant IC29x = 17593158014282350387180040649535510993206843353849210834719023901626588735467;
    uint256 constant IC29y = 8100239253177007641697492118067711047211346880276924834834314728000924961217;
    
    uint256 constant IC30x = 3931197685896243709871628612071448780695919472300675779359325593275871666266;
    uint256 constant IC30y = 8536690075906169871639333953671527364387998025365810836512191515507750830395;
    
    uint256 constant IC31x = 13905564476079098885269109564345121349558776889149019501804228587932878609962;
    uint256 constant IC31y = 8356722972574181683352109701149538549343902624158730544152701529071078057954;
    
    uint256 constant IC32x = 11879260754414474283823629953800409821478479446018473960858039647571173386091;
    uint256 constant IC32y = 9752417379845866520303120528207121512254042103150338741796988687616068524383;
    
    uint256 constant IC33x = 5159569879188140927851404311770847277023403797421415656227167798012389215756;
    uint256 constant IC33y = 15182945125477166124244329769436100411505602673418059100291818964937603018659;
    
    uint256 constant IC34x = 12793836554000676946336508004965806781475014177144991883373753023948642685516;
    uint256 constant IC34y = 11029240126488966384525344579084907147472259555687731787484522415881476347613;
    
    uint256 constant IC35x = 18857587674402586701536583633534802263497880617048150023145790001092904381414;
    uint256 constant IC35y = 4665193848318240670987732653348024125330116441670347793741304938757627508696;
    
    uint256 constant IC36x = 4892549293281267760013157523854072330005884056958524355055088050173994360329;
    uint256 constant IC36y = 752921179936328867721281075424575037166045185856074174892282833689072770295;
    
    uint256 constant IC37x = 5532681731065901075717746668752219722418905804525188186355314028543367351131;
    uint256 constant IC37y = 6389891983591244262339339892541382763268901916581187032372431759111633073564;
    
    uint256 constant IC38x = 9119224860618561724276180056657551475455395585187059552993009462114583909917;
    uint256 constant IC38y = 21378965462730379351329150257984754588752963846971054275845349163490232650659;
    
    uint256 constant IC39x = 20233074211983709220572622967641074490175006958360989681104788252042562391049;
    uint256 constant IC39y = 5612561372685589824447819593273910309460043835880310634860654390745573491703;
    
    uint256 constant IC40x = 7391123060362630392832312724496451782977834395781003618941912649543706710295;
    uint256 constant IC40y = 10388257762041553169458254575614550291109779305385669311246410407024021236113;
    
    uint256 constant IC41x = 2210241755145824118145884971075705797837733688827732330829791474178028566533;
    uint256 constant IC41y = 2563753728440259079016220956713866461496938971163922018916243634178858826960;
    
    uint256 constant IC42x = 18911872093750053283891321406774273420392253669062352048276001221264894780140;
    uint256 constant IC42y = 13840489799151591720965067467401282062480541093428394727902712794392741848921;
    
    uint256 constant IC43x = 13106188893336772188752749204498725536038816986798207045101064656541897568737;
    uint256 constant IC43y = 18982879964378843435512301721033733099458879925530631728473749923863486565854;
    
    uint256 constant IC44x = 15545603909017578014287130459627402081006512596554823445547322111849918435282;
    uint256 constant IC44y = 66274243210370994662600680481529875300277994357694531638720962484128583618;
    
    uint256 constant IC45x = 2132273162167020003467886089641148013929122565267913170114606974335018267868;
    uint256 constant IC45y = 15531163056608144859058813338309500853079148410701281952641765414838376188506;
    
    uint256 constant IC46x = 724900077035196947225845065649034202997139550757179291199766713809636372433;
    uint256 constant IC46y = 2601174779688285084531422372877107520909918242589817818910833366147692018487;
    
    uint256 constant IC47x = 21667503514058999220708051770101449491588045794216044833817275728245330548419;
    uint256 constant IC47y = 6556109167687194648211295643841478789932471516506481658413947021426134334559;
    
    uint256 constant IC48x = 9469990780712211381518784930814505613270068949053387079144837800687816212323;
    uint256 constant IC48y = 3767256620410535843887768096991710612256617408698552893899254453198216306126;
    
    uint256 constant IC49x = 1630926287105912124702132352494543848234060282462303234867590810698576800593;
    uint256 constant IC49y = 4648639365313497511377019970741412902130311113670244341388237251101156559235;
    
    uint256 constant IC50x = 14552332672308517516460397296175340551672553291299852480635979356815521002789;
    uint256 constant IC50y = 11833399070721197127730457276404770807986620307159753331865049424635747212856;
    
    uint256 constant IC51x = 10508757120434646492691462409206827926377249299527027505481979101195336240471;
    uint256 constant IC51y = 19536531950251610345381271003384572859075232360990830624806652254560741420932;
    
    uint256 constant IC52x = 4254962209695752712324686043270425631693017751051902272350787379008919884729;
    uint256 constant IC52y = 14142889167058538895653878082047364481123331252856685477976645893191143567900;
    
    uint256 constant IC53x = 13154006781894015399008820258865629707337676813439810654208439881420925922441;
    uint256 constant IC53y = 4095872233176602786021975918680299440489676334122320973537633275083497512345;
    
    uint256 constant IC54x = 14636123292487394112425910762660593468621676045398668938611743431400670024839;
    uint256 constant IC54y = 10193462191082607343089632682928321931056914766495704718852746659842688330043;
    
    uint256 constant IC55x = 21488561460705677189756604821117045584808690939297702937858877242925662298074;
    uint256 constant IC55y = 20197951558413320106384522708411669436784631647093949584822578876918667315803;
    
    uint256 constant IC56x = 2888185094032117298631439726022839817461045345558403506672959766851949372394;
    uint256 constant IC56y = 1402539289878565173462120408988084048219348023688210330820813011164535088422;
    
    uint256 constant IC57x = 20702061701264031633700700461171877386199400166225295846526126802867705625417;
    uint256 constant IC57y = 19747707714263240037192289327880870844508964372617498718530175252362369426385;
    
    uint256 constant IC58x = 18307018948077574418129981448632890872693409997684228840586556322333503223050;
    uint256 constant IC58y = 5989615799097055808215370038546865208798393430795559122561486580438976079916;
    
    uint256 constant IC59x = 5548733503444357294763300054181363849134183393446878635835761425705722502788;
    uint256 constant IC59y = 15598006813647168283967228917325408329059043938645685347592638996155431561310;
    
    uint256 constant IC60x = 16138067261438652044165111298370567215297966312517806417426182046836744338396;
    uint256 constant IC60y = 9192304396171104474866056212413184397073832063874062166845758313502168658958;
    
    uint256 constant IC61x = 4608321848558657305289218804752788570359337243460419013481709661584304317821;
    uint256 constant IC61y = 7530734137771278495582186135695824543803874755411951403760431277005763939949;
    
    uint256 constant IC62x = 5242150891876562042473998592773080086248643801279135134241813535793286203264;
    uint256 constant IC62y = 15798663120525916861251921427181521269056053793773086192447724041193628134997;
    
    uint256 constant IC63x = 19778585567302888769795588164117387148770534500478506211144137934954335464019;
    uint256 constant IC63y = 6870835105959240965658575570509931073848647324541204868977258003459215561869;
    
    uint256 constant IC64x = 6675790453428461134206778417141881795310206797428585150356465304022297224416;
    uint256 constant IC64y = 4910012303330702584107065439198550014724499207370928197744232866859646059064;
    
 
    // Memory data
    uint16 constant pVk = 0;
    uint16 constant pPairing = 128;

    uint16 constant pLastMem = 896;

    function verifyProof(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[64] calldata _pubSignals) public view returns (bool) {
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
                
                g1_mulAccC(_pVk, IC33x, IC33y, calldataload(add(pubSignals, 1024)))
                
                g1_mulAccC(_pVk, IC34x, IC34y, calldataload(add(pubSignals, 1056)))
                
                g1_mulAccC(_pVk, IC35x, IC35y, calldataload(add(pubSignals, 1088)))
                
                g1_mulAccC(_pVk, IC36x, IC36y, calldataload(add(pubSignals, 1120)))
                
                g1_mulAccC(_pVk, IC37x, IC37y, calldataload(add(pubSignals, 1152)))
                
                g1_mulAccC(_pVk, IC38x, IC38y, calldataload(add(pubSignals, 1184)))
                
                g1_mulAccC(_pVk, IC39x, IC39y, calldataload(add(pubSignals, 1216)))
                
                g1_mulAccC(_pVk, IC40x, IC40y, calldataload(add(pubSignals, 1248)))
                
                g1_mulAccC(_pVk, IC41x, IC41y, calldataload(add(pubSignals, 1280)))
                
                g1_mulAccC(_pVk, IC42x, IC42y, calldataload(add(pubSignals, 1312)))
                
                g1_mulAccC(_pVk, IC43x, IC43y, calldataload(add(pubSignals, 1344)))
                
                g1_mulAccC(_pVk, IC44x, IC44y, calldataload(add(pubSignals, 1376)))
                
                g1_mulAccC(_pVk, IC45x, IC45y, calldataload(add(pubSignals, 1408)))
                
                g1_mulAccC(_pVk, IC46x, IC46y, calldataload(add(pubSignals, 1440)))
                
                g1_mulAccC(_pVk, IC47x, IC47y, calldataload(add(pubSignals, 1472)))
                
                g1_mulAccC(_pVk, IC48x, IC48y, calldataload(add(pubSignals, 1504)))
                
                g1_mulAccC(_pVk, IC49x, IC49y, calldataload(add(pubSignals, 1536)))
                
                g1_mulAccC(_pVk, IC50x, IC50y, calldataload(add(pubSignals, 1568)))
                
                g1_mulAccC(_pVk, IC51x, IC51y, calldataload(add(pubSignals, 1600)))
                
                g1_mulAccC(_pVk, IC52x, IC52y, calldataload(add(pubSignals, 1632)))
                
                g1_mulAccC(_pVk, IC53x, IC53y, calldataload(add(pubSignals, 1664)))
                
                g1_mulAccC(_pVk, IC54x, IC54y, calldataload(add(pubSignals, 1696)))
                
                g1_mulAccC(_pVk, IC55x, IC55y, calldataload(add(pubSignals, 1728)))
                
                g1_mulAccC(_pVk, IC56x, IC56y, calldataload(add(pubSignals, 1760)))
                
                g1_mulAccC(_pVk, IC57x, IC57y, calldataload(add(pubSignals, 1792)))
                
                g1_mulAccC(_pVk, IC58x, IC58y, calldataload(add(pubSignals, 1824)))
                
                g1_mulAccC(_pVk, IC59x, IC59y, calldataload(add(pubSignals, 1856)))
                
                g1_mulAccC(_pVk, IC60x, IC60y, calldataload(add(pubSignals, 1888)))
                
                g1_mulAccC(_pVk, IC61x, IC61y, calldataload(add(pubSignals, 1920)))
                
                g1_mulAccC(_pVk, IC62x, IC62y, calldataload(add(pubSignals, 1952)))
                
                g1_mulAccC(_pVk, IC63x, IC63y, calldataload(add(pubSignals, 1984)))
                
                g1_mulAccC(_pVk, IC64x, IC64y, calldataload(add(pubSignals, 2016)))
                

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
            
            checkField(calldataload(add(_pubSignals, 1024)))
            
            checkField(calldataload(add(_pubSignals, 1056)))
            
            checkField(calldataload(add(_pubSignals, 1088)))
            
            checkField(calldataload(add(_pubSignals, 1120)))
            
            checkField(calldataload(add(_pubSignals, 1152)))
            
            checkField(calldataload(add(_pubSignals, 1184)))
            
            checkField(calldataload(add(_pubSignals, 1216)))
            
            checkField(calldataload(add(_pubSignals, 1248)))
            
            checkField(calldataload(add(_pubSignals, 1280)))
            
            checkField(calldataload(add(_pubSignals, 1312)))
            
            checkField(calldataload(add(_pubSignals, 1344)))
            
            checkField(calldataload(add(_pubSignals, 1376)))
            
            checkField(calldataload(add(_pubSignals, 1408)))
            
            checkField(calldataload(add(_pubSignals, 1440)))
            
            checkField(calldataload(add(_pubSignals, 1472)))
            
            checkField(calldataload(add(_pubSignals, 1504)))
            
            checkField(calldataload(add(_pubSignals, 1536)))
            
            checkField(calldataload(add(_pubSignals, 1568)))
            
            checkField(calldataload(add(_pubSignals, 1600)))
            
            checkField(calldataload(add(_pubSignals, 1632)))
            
            checkField(calldataload(add(_pubSignals, 1664)))
            
            checkField(calldataload(add(_pubSignals, 1696)))
            
            checkField(calldataload(add(_pubSignals, 1728)))
            
            checkField(calldataload(add(_pubSignals, 1760)))
            
            checkField(calldataload(add(_pubSignals, 1792)))
            
            checkField(calldataload(add(_pubSignals, 1824)))
            
            checkField(calldataload(add(_pubSignals, 1856)))
            
            checkField(calldataload(add(_pubSignals, 1888)))
            
            checkField(calldataload(add(_pubSignals, 1920)))
            
            checkField(calldataload(add(_pubSignals, 1952)))
            
            checkField(calldataload(add(_pubSignals, 1984)))
            
            checkField(calldataload(add(_pubSignals, 2016)))
            

            // Validate all evaluations
            let isValid := checkPairing(_pA, _pB, _pC, _pubSignals, pMem)

            mstore(0, isValid)
             return(0, 0x20)
         }
     }
 }
