#!/bin/bash
# V2-PRV-D1-01 runner — macOS host (MacBook Pro M5) with Docker Desktop; started by the owner in macOS Terminal.
#   bash research/csi/protocols/v2/prover-D1/kit/run-d1.sh preflight   # host + container checks, untimed; no timing
#   bash research/csi/protocols/v2/prover-D1/kit/run-d1.sh campaign    # preflight, untimed dry run, rounds 0..20 (timed)
#   bash research/csi/protocols/v2/prover-D1/kit/run-d1.sh resume      # continue after a stopped session (accepted rounds kept)
# Host conditions follow the V1 v3 P9 rules: AC power, Low Power Mode off, caffeinate held by this runner, no other
# container running; they are re-checked before every timed round. Any failure stops the session (no silent retry).
# Allocation: cpu8 = Docker cpuset 1-8 of the Docker Desktop VM's vCPUs, 8 ffjavascript workers (adapter), 8 GiB, swap 0,
# no CPU quota, no network, artifacts read-only. bash 3.2 compatible.
set -u
MODE="${1:-}"; case "$MODE" in preflight|campaign|resume) ;; *) echo "usage: $0 preflight|campaign|resume"; exit 2 ;; esac
KIT="$(cd "$(dirname "$0")" && pwd)"; P="$(cd "$KIT/.." && pwd)"; V2="$(cd "$P/../../../../.." && pwd)"
ART="$P/artifacts"; OUT="$V2/research/results/v2/V2-PRV-D1-01"; POT="$V2/research/pot16_final.ptau"
POT_SHA=4a64b121623021d5bcb19eee0a716d50ecb936e04b2cd021e71e74a86441439e
SID="S$(date -u +%Y%m%dT%H%M%SZ)"; mkdir -p "$OUT/sessions/$SID" "$OUT/raw" "$OUT/keys"; LOG="$OUT/sessions/$SID/runner.log"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
fail() { log "STOP: $*"; echo "$SID,stopped,$(date -u +%FT%TZ),\"$*\"" >> "$OUT/sessions.csv"; exit 2; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
log "session $SID mode $MODE V2=$V2"
[ -f "$OUT/sessions.csv" ] || echo "session,event,utc,detail" > "$OUT/sessions.csv"; echo "$SID,start,$(date -u +%FT%TZ),$MODE" >> "$OUT/sessions.csv"
[ -f "$OUT/ledger.csv" ] || echo "kind,round,attempt,session,status,utc" > "$OUT/ledger.csv"
# ---- 1. frozen protocol, kit and artifacts ----
( cd "$P" && shasum -a 256 -c SHA256SUMS > "$OUT/sessions/$SID/protocol-check.txt" 2>&1 ) || fail "protocol / kit / artifacts differ from the frozen SHA256SUMS"
KITHASH=$(sha "$P/SHA256SUMS"); log "protocol SHA256SUMS $KITHASH"
[ "$(sha "$POT")" = "$POT_SHA" ] || fail "pot16_final.ptau hash"
# ---- 2. host conditions (P9) ----
CAFF=""; caffeinate -dimsu -w $$ & CAFF=$!; sleep 2
p9() {
  PS=$(pmset -g batt 2>/dev/null | head -1); LPM=$(pmset -g 2>/dev/null | awk '/lowpowermode/{print $2}')
  NA=$(pmset -g assertions 2>/dev/null | grep -c "pid $CAFF(caffeinate)"); NC=$(docker ps -q | wc -l | tr -d ' ')
  echo "$(date -u +%FT%TZ),$1,\"$PS\",${LPM:-?},$NA,$NC,\"$(sysctl -n vm.loadavg)\",\"$(pmset -g therm 2>/dev/null | tr '\n' ' ')\"" >> "$OUT/sessions/$SID/host-samples.csv"
  echo "$PS" | grep -q "AC Power" || return 1; [ "${LPM:-1}" = 0 ] || return 1; [ "$NA" -ge 1 ] || return 1; [ "$NC" = 0 ] || return 1; return 0
}
echo "utc,phase,power,low_power_mode,caffeinate_assertions,running_containers,loadavg,therm" > "$OUT/sessions/$SID/host-samples.csv"
p9 start || fail "host conditions (AC power, Low Power Mode off, caffeinate, no other container)"
{ sw_vers; sysctl -n hw.model machdep.cpu.brand_string hw.physicalcpu hw.memsize; docker version; docker info; } > "$OUT/sessions/$SID/host.txt" 2>&1
DI=$(docker info --format '{{.Architecture}} {{.NCPU}} {{.MemTotal}} {{.CgroupVersion}}'); set -- $DI
[ "$1" = aarch64 ] && [ "$2" -ge 9 ] && [ "$3" -ge 11811160064 ] && [ "$4" = 2 ] || fail "Docker VM: $DI (need aarch64, >= 9 vCPUs, >= 11 GiB, cgroup v2)"
# ---- 3. image ----
TAG="zcorp-d1:${KITHASH:0:12}"
docker build --platform linux/arm64 -t "$TAG" "$KIT" > "$OUT/sessions/$SID/docker-build.log" 2>&1 || fail "image build"
IMG=$(docker image inspect --format '{{.Id}}' "$TAG"); log "image $TAG $IMG"
RUN="docker run --rm --platform linux/arm64 --network none --init"
# ---- 4. PLONK keys: regenerate once (untimed), then hash-check against KEYS-SHA256SUMS ----
if ! ( cd "$OUT/keys" && shasum -a 256 -c "$ART/KEYS-SHA256SUMS" > /dev/null 2>&1 ); then
  log "regenerating PLONK keys (untimed)"
  $RUN --cpuset-cpus 1-8 --memory 12g --memory-swap 12g -e NODE_OPTIONS="--max-old-space-size=7000" -v "$ART:/d1art:ro" -v "$POT:/pot16.ptau:ro" -v "$OUT/keys:/d1keys" "$TAG" node /opt/zcorp-d1/d1_regen.js >> "$LOG" 2>&1 || fail "key regeneration"
fi
( cd "$OUT/keys" && shasum -a 256 -c "$ART/KEYS-SHA256SUMS" > "$OUT/sessions/$SID/keys-check.txt" 2>&1 ) || fail "regenerated PLONK keys differ from KEYS-SHA256SUMS"
BASE="$RUN --cpuset-cpus 1-8 --memory 8g --memory-swap 8g -e ZCORP_CPUS=8 -e ZCORP_PROFILE=cpu8 -e ZCORP_SESSION_ID=$SID -e ZCORP_IMAGE_ID=$IMG -v $ART:/d1art:ro -v $OUT/keys:/d1keys:ro -v $OUT:/results"
# ---- 5. adapter controls (must be refused with exit 97) ----
$RUN --cpuset-cpus 1-8 -e ZCORP_CPUS=4 "$TAG" node -e 0 > /dev/null 2>&1; [ $? = 97 ] || fail "adapter control (mismatched ZCORP_CPUS) not refused"
$RUN --cpus 8 -e ZCORP_CPUS=8 "$TAG" node -e 0 > /dev/null 2>&1; [ $? = 97 ] || fail "adapter control (quota without cpuset) not refused"
log "adapter controls refused as required"
# ---- 6. container preflight (assertions, hash checks, warm-up; untimed) ----
$BASE "$TAG" node --expose-gc /opt/zcorp-d1/d1_harness.js --kind preflight --round 0 --attempt 1 >> "$LOG" 2>&1 || fail "container preflight"
log "PREFLIGHT PASS"; [ "$MODE" = preflight ] && { echo "$SID,preflight-pass,$(date -u +%FT%TZ)," >> "$OUT/sessions.csv"; exit 0; }
# ---- 7. untimed dry run (one container, all 8 configurations; timings not interpreted) ----
if ! grep -q '^dryrun,0,.*,complete' "$OUT/ledger.csv"; then
  p9 dryrun || fail "host conditions before dry run"
  $BASE "$TAG" node --expose-gc /opt/zcorp-d1/d1_harness.js --kind dryrun --round 0 --attempt 1 >> "$LOG" 2>&1 && st=complete || st=failed
  echo "dryrun,0,1,$SID,$st,$(date -u +%FT%TZ)" >> "$OUT/ledger.csv"; [ $st = complete ] || fail "dry run"
fi
# ---- 8. rounds 0 (warm-up, discarded, kept) .. 20, one fresh container each, frozen order ----
for r in $(seq 0 20); do
  grep -q "^primary,$r,[0-9]*,[^,]*,complete" "$OUT/ledger.csv" && continue
  a=$(( $(grep -c "^primary,$r," "$OUT/ledger.csv") + 1 ))
  p9 "round-$r" || fail "host conditions before round $r"
  $BASE "$TAG" node --expose-gc /opt/zcorp-d1/d1_harness.js --kind primary --round $r --attempt $a >> "$LOG" 2>&1 && st=complete || st=failed
  p9 "after-$r" || st=failed
  echo "primary,$r,$a,$SID,$st,$(date -u +%FT%TZ)" >> "$OUT/ledger.csv"; log "round $r attempt $a $st"
  [ $st = complete ] || fail "round $r attempt $a failed (rerun as a new attempt with: run-d1.sh resume)"
done
echo "$SID,campaign-complete,$(date -u +%FT%TZ)," >> "$OUT/sessions.csv"; log "CAMPAIGN COMPLETE (21 rounds; round 0 is the discarded warm-up)"
