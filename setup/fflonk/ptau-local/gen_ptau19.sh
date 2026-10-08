#!/bin/bash
set -u
W="$HOME/Workspace/Z-CORP-V2-workstation"; D="$W/ptau/local"; cd "$D"
export PATH="$(cat "$W/toolchain/node-bin-dir.txt"):$PATH"; export npm_config_cache="$W/tmp/npm-cache"
SJ="node --max-old-space-size=32000 $W/toolchain/js/node_modules/snarkjs/cli.js"
st() { echo "$(date -u +%FT%TZ) $*" | tee -a STATUS; }
step() { local name=$1; shift; st "begin $name"; { echo "\$ $*"; "$@"; } > "log-$name.txt" 2>&1; local rc=$?; st "end $name rc=$rc"; [ $rc -eq 0 ] || { echo $rc > FAILED; exit $rc; }; }
{ echo "host=$(hostname) kernel=$(uname -r)"; echo "node=$(node --version)"; cat "$W/toolchain/PACKAGE-VERSIONS.txt"; } > TOOL-VERSIONS.txt
step new $SJ powersoftau new bn128 19 pot19_0000.ptau -v
# Contribution entropy: 64 random bytes from /dev/urandom, used once and discarded (only its sha256 commitment is kept).
ENT=$(head -c 64 /dev/urandom | od -An -tx1 | tr -d ' \n'); echo -n "$ENT" | sha256sum | cut -c1-64 > entropy-sha256-commitment.txt
# DEV-FF-PTAU-1 (pre-execution correction): the entropy is passed on stdin, not on the command line, so that it never
# appears in log-contribute.txt or in the process list; snarkjs mixes it with its own 64 random bytes (getRandomRng).
st "begin contribute"
{ echo "\$ $SJ powersoftau contribute pot19_0000.ptau pot19_0001.ptau --name=\"Z-CORP-V2 research contribution (local, AMD-FF-1)\" -v   [entropy: 64 B /dev/urandom on stdin; not recorded; sha256 commitment in entropy-sha256-commitment.txt]"
  printf '%s\n' "$ENT" | $SJ powersoftau contribute pot19_0000.ptau pot19_0001.ptau --name="Z-CORP-V2 research contribution (local, AMD-FF-1)" -v; } > log-contribute.txt 2>&1
rc=$?; st "end contribute rc=$rc"; [ $rc -eq 0 ] || { echo $rc > FAILED; exit $rc; }
unset ENT
# Beacon: deterministic and recorded (research ptau, not a trusted setup): sha256 of a fixed label, the frozen C1
# SHA256SUMS hash and the sha256 of the contributed file. 2^10 iterations.
C1=7dac8482aea1420a30b303c3d45b0c46627da67a976e578fa1d09d7c715bfc8f
BEACON=$(printf 'V2-C1-AMD-FF-1|%s|%s' "$C1" "$(sha256sum pot19_0001.ptau | cut -c1-64)" | sha256sum | cut -c1-64); echo "$BEACON" > beacon-hash.txt
step beacon $SJ powersoftau beacon pot19_0001.ptau pot19_beacon.ptau "$BEACON" 10 -n="AMD-FF-1 deterministic beacon" -v
step prepare $SJ powersoftau prepare phase2 pot19_beacon.ptau powersOfTau19_v2_local_research.ptau -v
step verify $SJ powersoftau verify powersOfTau19_v2_local_research.ptau -v
grep -qi "Powers of Tau Ok" log-verify.txt && V=PASS || V=FAIL
F=powersOfTau19_v2_local_research.ptau
cat > PTAU-LOCAL-RECORD.json <<J
{"artifact":"$F","label":"LOCALLY GENERATED RESEARCH PTAU (C1 doc 21 fallback; not the Hermez ceremony file; not a trusted setup)",
 "decision":"V2-D-38 (owner approval of the doc-21 fallback)","procedure":"powersoftau new bn128 19; contribute (urandom 64 B entropy, discarded; sha256 commitment kept); beacon (deterministic, recorded, 2^10); prepare phase2; verify",
 "beacon_hash":"$(cat beacon-hash.txt)","entropy_sha256_commitment":"$(cat entropy-sha256-commitment.txt)",
 "bytes":$(stat -c %s $F),"blake2b512":"$(b2sum $F | cut -d' ' -f1)","sha256":"$(sha256sum $F | cut -c1-64)",
 "powersoftau_verify":"$V","host":"$(hostname)","started_utc":"$(head -1 STATUS | cut -d' ' -f1)","ended_utc":"$(date -u +%FT%TZ)","path":"$D/$F"}
J
sha256sum pot19_0000.ptau pot19_0001.ptau pot19_beacon.ptau "$F" log-*.txt TOOL-VERSIONS.txt beacon-hash.txt entropy-sha256-commitment.txt > PTAU-LOCAL-SHA256SUMS
st "done verify=$V"; echo $V > DONE
