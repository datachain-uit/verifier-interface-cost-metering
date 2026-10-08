#!/bin/bash
# usage: setup.sh <name> [backends...]   (feasibility setups with pot16; Groth16 phase-2 WITHOUT contribution — cost-identical, not for production)
set -u; cd ~/p0/circ; N=$1; shift; B=${@:-groth16 plonk}
SJ="node --max-old-space-size=6000 $HOME/p0/node/node_modules/snarkjs/cli.js"; PT=$HOME/p0/research/pot16_final.ptau
mkdir -p keys/$N logs
for b in $B; do
  t0=$(date +%s)
  if [ $b = groth16 ]; then $SJ groth16 setup build/$N/$N.r1cs $PT keys/$N/groth16.zkey > logs/$N-groth16.log 2>&1
  elif [ $b = plonk ]; then $SJ plonk setup build/$N/$N.r1cs $PT keys/$N/plonk.zkey > logs/$N-plonk.log 2>&1
  elif [ $b = fflonk ]; then $SJ fflonk setup build/$N/$N.r1cs ${PTF:-$PT} keys/$N/fflonk.zkey > logs/$N-fflonk.log 2>&1; fi
  rc=$?; t1=$(date +%s)
  if [ $rc = 0 ]; then $SJ zkey export verificationkey keys/$N/$b.zkey keys/$N/$b.vkey.json >> logs/$N-$b.log 2>&1; $SJ zkey export solidityverifier keys/$N/$b.zkey keys/$N/${b}Verifier.sol >> logs/$N-$b.log 2>&1; fi
  echo "$N $b rc=$rc secs=$((t1-t0))" >> logs/summary.txt
done
