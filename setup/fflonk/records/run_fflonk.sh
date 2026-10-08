#!/bin/bash
set -u
W="$HOME/Workspace/Z-CORP-V2-workstation"; F="$W/fflonk"; I="$W/inputs/fflonk-inputs"; PT="$W/ptau/local/powersOfTau19_v2_local_research.ptau"
export PATH="$(cat "$W/toolchain/node-bin-dir.txt"):$PATH"; export npm_config_cache="$W/tmp/npm-cache"
SJ="node --max-old-space-size=24000 $W/toolchain/js/node_modules/snarkjs/cli.js"; cd "$F"
st() { echo "$(date -u +%FT%TZ) $*" >> STATUS; }
EXP=$(python3 -c "import json;print(json.load(open('$W/ptau/local/PTAU-LOCAL-RECORD.json'))['blake2b512'])")
[ "$(b2sum "$PT" | cut -d' ' -f1)" = "$EXP" ] && st "ptau b2sum re-checked before use: PASS" || { st "ptau b2sum re-check FAILED"; echo 4 > FFLONK-DONE; exit 4; }
fail=0
for t in c1_ff_k01:c1_k01:v1 c1_ff_k04:c1_ctx_k04:ctx_k4 c1_ff_k16:c1_ctx_k16:ctx_k16 c1_ff_k32:c1_ctx_k32:ctx_k32; do
  IFS=: read N SRC REL <<< "$t"; K="keys/$N"; mkdir -p "$K"
  st "setup $N (r1cs $SRC) begin"
  nice -n 10 $SJ fflonk setup "$I/r1cs/$SRC.r1cs" "$PT" "$K/fflonk.zkey" > "$K/setup.log" 2>&1; rc=$?
  if [ $rc -eq 0 ]; then $SJ zkey export verificationkey "$K/fflonk.zkey" "$K/fflonk.vkey.json" >> "$K/setup.log" 2>&1 && $SJ zkey export solidityverifier "$K/fflonk.zkey" "$K/fflonkVerifier.sol" >> "$K/setup.log" 2>&1; rc=$?; fi
  st "setup $N rc=$rc"; [ $rc -eq 0 ] || { fail=1; continue; }
  st "prove $N begin"; nice -n 10 node --max-old-space-size=24000 prove_ff.js "$N" "$SRC" "$REL" > "$K/prove.log" 2>&1; rc=$?; st "prove $N rc=$rc"; [ $rc -eq 0 ] || fail=1
done
find keys proofs -type f | sort | xargs sha256sum > FFLONK-ARTIFACTS-SHA256SUMS; st "artifacts hashed: $(wc -l < FFLONK-ARTIFACTS-SHA256SUMS) files"
echo $fail > FFLONK-DONE; st "done fail=$fail"
