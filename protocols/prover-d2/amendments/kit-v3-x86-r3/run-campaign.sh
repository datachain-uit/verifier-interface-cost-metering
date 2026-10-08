#!/bin/bash
# Z-CORP rerun protocol v3, kit v3-x86: Host-B runner for V2-PRV-D2-01 (Dell Precision 7920, Ubuntu 24.04, native
# Docker Engine, linux/amd64). Procedure identical to research/bench/run-campaign.sh (v3) except the host adaptation
# listed in ../D2-PREREGISTRATION.md §4.2. Started only by owner-authorized relay jobs.
#
#   bash bench/run-campaign.sh setup                       untimed setup: image build, PLONK keys, manifests (setup window)
#   bash bench/run-campaign.sh preflight                   host + container pre-flight, P7; no rounds
#   bash bench/run-campaign.sh dryrun [--plan resumetest]  engineering dry run (v3 §3.9); timings not interpreted
#   bash bench/run-campaign.sh campaign                    timed campaign; needs ZCORP_ALLOW_FULL_CAMPAIGN=1 and
#                                                          ZCORP_D2_WINDOW=<owner window id> (dedicated quiet window)
#   bash bench/run-campaign.sh resume <campaign-dir>       continue at the next round unit without an accepted attempt
#
# Host conditions (replace the macOS P9 rules; D2-PREREGISTRATION.md §5): a sleep inhibitor (systemd-inhibit) held by
# this runner; the frozen frequency / NUMA / THP state (recorded, never changed); no other container; quiet CPUs before
# every container and during it (hostb_quiet.py). A violation before a container stops the session (the unit stays
# without outcome and is rerun whole); a violation during a container records the attempt as failed and stops.
# Allocation: cpu2 = CPUs 1-2, cpu4 = 1-4, cpu8 = 1-8 (one hardware thread per physical core, socket 0), memory NUMA
# node 0 (--cpuset-mems 0); SMT siblings (57-64) and CPU 0 / 56 are not allocated. bash >= 4.4.
set -u

usage() { echo "usage: $0 setup | preflight | dryrun [--plan dryrun|resumetest] | campaign | resume <campaign-dir>"; exit 2; }
MODE="${1:-}"; [ $# -gt 0 ] && shift
PLAN=""; RESUME_DIR=""
case "$MODE" in
  setup|preflight|campaign) ;;
  dryrun) if [ "${1:-}" = "--plan" ]; then PLAN="${2:-}"; [ -n "$PLAN" ] || usage; fi ;;
  resume) RESUME_DIR="${1:-}"; [ -n "$RESUME_DIR" ] || usage ;;
  *) usage ;;
esac

KIT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$KIT/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SESSION_ID="S${STAMP}"
PROTOCOL_VERSION=v3
KIT_VERSION=v3-x86
IMAGE_TAG="${ZCORP_IMAGE_TAG:-zcorp-bench:v3-x86}"
PLATFORM=linux/amd64
EXPECT_DOCKER_ARCH=x86_64
PROFILES="cpu2:1-2,cpu4:1-4,cpu8:1-8"
CPUSET_MEMS=0
EXPECT_CPU_MODEL="Intel(R) Xeon(R) Platinum 8173M CPU @ 2.00GHz"
FROZEN_STATE="intel_pstate=active governor=powersave no_turbo=0 numa_balancing=1 thp=madvise"
EXPECT_SIBLINGS="57 58 59 60 61 62 63 64 "    # SMT siblings of CPUs 1-8 (records workstation-20261004)
HOST_A_SCHEDULE_SHA256=f7e6de3bbd1c9d24b0c41909414014c4e9cd1ee2ff2179c845aec8b9464fbb95
HOST_A_PLAN_SHA256=99fb360ccb801606ee13a7aa03705522aceb5845a0d62affd647d9a2b0badc94
BASE_REF="node:18.20.8-bookworm-slim@sha256:f9ab18e354e6855ae56ef2b290dd225c1e51a564f87584b9bd21dd651838830e"
MIN_NCPU=9
MIN_MEM_GIB=11.0
TREE_PATHS="bench scripts/setup ARTIFACTS.sha256 SYNTHETIC-CORPUS.sha256"

jget() { sed -n "s/.*\"$1\": \"\([^\"]*\)\".*/\1/p" "$OUT/CAMPAIGN.json" | head -1; }
sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }
tree_sha() { ( cd "$REPO" && find $TREE_PATHS -type f -print0 | sort -z | xargs -0 sha256sum ) | sha256sum | cut -d' ' -f1; }

if [ "$MODE" = resume ]; then
  OUT="$(cd "$RESUME_DIR" 2>/dev/null && pwd)" || { echo "ABORT: no such campaign directory: $RESUME_DIR"; exit 2; }
  [ -f "$OUT/CAMPAIGN.json" ] || { echo "ABORT: $OUT has no CAMPAIGN.json"; exit 2; }
  CAMPAIGN_ID="$(jget campaign_id)"; CMODE="$(jget mode)"
  if [ "$CMODE" = campaign ] && { [ "${ZCORP_ALLOW_FULL_CAMPAIGN:-0}" != 1 ] || [ -z "${ZCORP_D2_WINDOW:-}" ]; }; then
    echo "ABORT: resuming the timed campaign needs ZCORP_ALLOW_FULL_CAMPAIGN=1 and ZCORP_D2_WINDOW=<owner window id>"; exit 2
  fi
else
  if [ "$MODE" = campaign ]; then
    if [ "${ZCORP_ALLOW_FULL_CAMPAIGN:-0}" != 1 ] || [ -z "${ZCORP_D2_WINDOW:-}" ]; then
      echo "ABORT: the timed campaign needs ZCORP_ALLOW_FULL_CAMPAIGN=1 and ZCORP_D2_WINDOW=<owner window id> (dedicated quiet window)"; exit 2
    fi
    CAMPAIGN_ID="${ZCORP_CAMPAIGN_ID:-V2-PRV-D2-01-run1}"
    OUT="${ZCORP_OUT:-$REPO/results/V2-PRV-D2-01}"; CMODE=campaign; PLAN=campaign
  else
    CAMPAIGN_ID="${ZCORP_CAMPAIGN_ID:-${MODE}-${STAMP}}"
    OUT="${ZCORP_OUT:-$REPO/build/campaigns/$CAMPAIGN_ID}"; CMODE=dryrun; [ -n "$PLAN" ] || PLAN=dryrun
  fi
  if [ -e "$OUT/CAMPAIGN.json" ]; then echo "ABORT: $OUT already holds a campaign (use: resume $OUT)"; exit 2; fi
fi
if [ -n "${ZCORP_TEST_INTERRUPT_AFTER_CONTAINERS:-}" ] && [ "$CMODE" != dryrun ]; then
  echo "ABORT: simulated interruptions are allowed in dry runs only"; exit 2
fi

mkdir -p "$OUT/environment/preflight/$SESSION_ID" "$OUT/prover" "$OUT/environment/quiet/$SESSION_ID"
E="$OUT/environment"; Q="$E/quiet/$SESSION_ID"
LOG="$E/run-campaign.log"
exec > >(tee -a "$LOG") 2>&1
echo "== Z-CORP $PROTOCOL_VERSION ($KIT_VERSION) $MODE: campaign $CAMPAIGN_ID, session $SESSION_ID -> $OUT"

# Sleep inhibitor (replaces caffeinate): held while this runner lives; verified by name in systemd-inhibit --list.
INH_PID=""
if command -v systemd-inhibit >/dev/null 2>&1; then
  systemd-inhibit --what=sleep:idle --who=zcorp-d2 --why="V2-PRV-D2-01 session $SESSION_ID" --mode=block tail --pid=$$ -f /dev/null &
  INH_PID=$!; sleep 2
fi
inh_ok() { [ -n "$INH_PID" ] && kill -0 "$INH_PID" 2>/dev/null && systemd-inhibit --list --no-pager --no-legend 2>/dev/null | grep -q zcorp-d2; }

# Profile -> docker run (same limits as v3 compose.yaml, plus --cpuset-mems; compose has no cpuset-mems key).
svc_cpuset() { case "$1" in cpu1) echo 1 ;; cpu2) echo 1-2 ;; cpu4) echo 1-4 ;; cpu8|tools) echo 1-8 ;; *) return 1 ;; esac; }
svc_cpus() { case "$1" in cpu1) echo 1 ;; cpu2) echo 2 ;; cpu4) echo 4 ;; cpu8|tools) echo 8 ;; *) return 1 ;; esac; }
drun() { # drun <profile> [docker options ...] -- <command ...>
  local svc="$1"; shift; local opts=()
  while [ $# -gt 0 ] && [ "$1" != -- ]; do opts+=("$1"); shift; done; [ "${1:-}" = -- ] && shift
  docker run --rm --init --network none --platform "$PLATFORM" \
    --cpuset-cpus "$(svc_cpuset "$svc")" --cpuset-mems "$CPUSET_MEMS" --memory 8g --memory-swap 8g -w /work \
    --mount "type=bind,source=$REPO,target=/work,readonly" --mount "type=bind,source=$OUT,target=/results" \
    -e ZCORP_PROFILE="$svc" -e ZCORP_CPUS="$(svc_cpus "$svc")" -e ZCORP_IMAGE_ID="$ZCORP_IMAGE_ID" -e ZCORP_SESSION_ID="$SESSION_ID" \
    "${opts[@]}" "$ZCORP_IMAGE" "$@" </dev/null
}

# ------------------------------------------------------------------ session records
NCPU=""; MEMB=""; ENGINE=""; KERNEL=""; IMAGE_ID="${IMAGE_ID:-}"; INH=0
session_event() { # event detail
  local f="$E/sessions.csv"
  [ -f "$f" ] || echo "campaign_id,session_id,event,utc,mode,git_head,image_id,docker_desktop,engine,kernel,vm_ncpu,vm_mem_bytes,power_source,low_power_mode,caffeinated,detail" > "$f"
  echo "$CAMPAIGN_ID,$SESSION_ID,$1,$(date -u +%Y-%m-%dT%H:%M:%SZ),$MODE,none,$IMAGE_ID,n/a (native Engine),$ENGINE,$KERNEL,$NCPU,$MEMB,\"n/a (desktop)\",n/a,$INH,\"window ${ZCORP_D2_WINDOW:-none}; $2\"" >> "$f"
}
fail() {
  echo "ABORT: $*"
  echo "result: FAIL ($*)" > "$E/RESULT-$SESSION_ID.txt"; cp "$E/RESULT-$SESSION_ID.txt" "$E/RESULT.txt"
  session_event end "FAIL: $*"
  exit 1
}

# ------------------------------------------------------------------ 1. host facts, frozen state, Docker Engine
{
  echo "session_id=$SESSION_ID"; echo "kit=$KIT_VERSION"; echo "window=${ZCORP_D2_WINDOW:-}"
  echo "hostname=$(hostname)"; echo "kernel=$(uname -r)"; echo "os=$(. /etc/os-release && echo "$PRETTY_NAME")"
  echo "cpu_model=$(awk -F': ' '/^model name/{print $2; exit}' /proc/cpuinfo)"
  echo "nproc=$(nproc --all)"; echo "mem_total_kb=$(awk '/MemTotal/{print $2}' /proc/meminfo)"
  echo "intel_pstate=$(cat /sys/devices/system/cpu/intel_pstate/status 2>/dev/null)"
  echo "no_turbo=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null)"
  echo "hwp_dynamic_boost=$(cat /sys/devices/system/cpu/intel_pstate/hwp_dynamic_boost 2>/dev/null)"
  echo "governors=$(cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null | sort | uniq -c | tr -s ' ' | tr '\n' ';')"
  echo "epp_cpu1_8=$(for c in 1 2 3 4 5 6 7 8; do cat /sys/devices/system/cpu/cpu$c/cpufreq/energy_performance_preference 2>/dev/null; done | tr '\n' ' ')"
  echo "numa_balancing=$(cat /proc/sys/kernel/numa_balancing 2>/dev/null)"
  echo "thp=$(cat /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null)"
  echo "smt=$(cat /sys/devices/system/cpu/smt/control 2>/dev/null)"
  echo "siblings_cpu1_8=$(for c in 1 2 3 4 5 6 7 8; do cat /sys/devices/system/cpu/cpu$c/topology/thread_siblings_list; done | tr '\n' ' ')"
  echo "node0_cpus=$(cat /sys/devices/system/node/node0/cpulist 2>/dev/null)"
  echo "cmdline=$(cat /proc/cmdline)"
  echo "loadavg=$(cat /proc/loadavg)"
  echo "sleep_inhibitor_pid=$INH_PID"; echo "sleep_inhibitor_ok=$(inh_ok && echo 1 || echo 0)"
} > "$E/host-$SESSION_ID.txt"
{ lscpu; echo; numactl -H; echo; free -b; echo; df -B1 "$REPO"; } > "$E/host-detail-$SESSION_ID.txt" 2>&1
cp "$E/host-$SESSION_ID.txt" "$E/host.txt"; cat "$E/host-$SESSION_ID.txt"
INH=$(sed -n 's/^sleep_inhibitor_ok=//p' "$E/host-$SESSION_ID.txt")
CPU_MODEL=$(sed -n 's/^cpu_model=//p' "$E/host-$SESSION_ID.txt")
[ "$CPU_MODEL" = "$EXPECT_CPU_MODEL" ] || fail "CPU model '$CPU_MODEL' is not the registered Host B"
SIBS=$(for c in 1 2 3 4 5 6 7 8; do cut -d, -f2 /sys/devices/system/cpu/cpu$c/topology/thread_siblings_list; done | tr '\n' ' ')
[ "$SIBS" = "$EXPECT_SIBLINGS" ] || fail "SMT sibling map of CPUs 1-8 is '$SIBS', registered '$EXPECT_SIBLINGS'"
python3 "$KIT/hostb_quiet.py" selftest > "$E/quiet-selftest-$SESSION_ID.txt" 2>&1 || fail "host-condition check self-test failed"
if [ "$MODE" != setup ]; then [ "$INH" = 1 ] || fail "sleep inhibitor (systemd-inhibit) not held"; fi

docker version --format '{{json .}}' > "$E/docker-version-$SESSION_ID.json" 2>&1
docker info --format '{{json .}}' > "$E/docker-info-$SESSION_ID.json" 2>&1 || fail "docker daemon not reachable"
NCPU=$(docker info --format '{{.NCPU}}'); MEMB=$(docker info --format '{{.MemTotal}}')
DARCH=$(docker info --format '{{.Architecture}}'); KERNEL=$(docker info --format '{{.KernelVersion}}')
ENGINE=$(docker version --format '{{.Server.Version}}'); CGV=$(docker info --format '{{.CgroupVersion}}')
echo "docker: engine=$ENGINE ncpu=$NCPU mem_bytes=$MEMB arch=$DARCH cgroup=v$CGV kernel=$KERNEL"
session_event start "$([ "$MODE" = resume ] && echo resume || echo new)"
awk -v n="$NCPU" -v m="$MEMB" -v mn="$MIN_NCPU" -v mm="$MIN_MEM_GIB" 'BEGIN{exit !(n>=mn && m/1073741824>=mm)}' || fail "Docker host has $NCPU CPUs / $MEMB bytes"
[ "$DARCH" = "$EXPECT_DOCKER_ARCH" ] || fail "Docker architecture $DARCH, expected $EXPECT_DOCKER_ARCH"
[ "$CGV" = 2 ] || fail "cgroup v$CGV, expected v2"

# Frozen state: checked, never changed (record-as-is policy, D2-PREREGISTRATION.md §5.2).
python3 "$KIT/hostb_quiet.py" snap "$Q/session-a.json"; sleep 2; python3 "$KIT/hostb_quiet.py" snap "$Q/session-b.json"
python3 "$KIT/hostb_quiet.py" check "$Q/session-a.json" "$Q/session-b.json" --mode pre --alloc 1-8 --frozen "$FROZEN_STATE" > "$Q/session-check.json"; SRC=$?
echo "host conditions at session start: $(cat "$Q/session-check.json")"
if [ "$MODE" != setup ] && [ $SRC != 0 ]; then fail "host conditions not met at session start"; fi

# ------------------------------------------------------------------ 2. repository state (frozen manifests; no git on Host B)
( cd "$REPO" && sha256sum -c ARTIFACTS.sha256 > "$E/manifest-before-$SESSION_ID.txt" 2>&1 ); MAN_BEFORE=$?
( cd "$REPO" && sha256sum -c SYNTHETIC-CORPUS.sha256 > "$E/corpus-before-$SESSION_ID.txt" 2>&1 ); CORPUS_BEFORE=$?
TREE_SHA=$(tree_sha)
echo "manifest before: $(grep -c ': OK$' "$E/manifest-before-$SESSION_ID.txt") OK, exit $MAN_BEFORE; corpus: $(grep -c ': OK$' "$E/corpus-before-$SESSION_ID.txt") OK, exit $CORPUS_BEFORE; tree $TREE_SHA"
[ "$CORPUS_BEFORE" = 0 ] || fail "SYNTHETIC-CORPUS.sha256 check failed"
if [ "$MODE" != setup ]; then [ "$MAN_BEFORE" = 0 ] || fail "ARTIFACTS.sha256 check failed before the run (PLONK keys: run 'setup' first)"; fi

integrity_after() {
  ( cd "$REPO" && sha256sum -c ARTIFACTS.sha256 > "$E/manifest-after-$SESSION_ID.txt" 2>&1 ); local man_after=$?
  ( cd "$REPO" && sha256sum -c SYNTHETIC-CORPUS.sha256 > "$E/corpus-after-$SESSION_ID.txt" 2>&1 ); local cor_after=$?
  local t_after; t_after=$(tree_sha)
  printf '{\n  "session_id": "%s",\n  "manifest_before_ok": %s,\n  "manifest_after_ok": %s,\n  "corpus_after_ok": %s,\n  "manifest_entries_ok_after": %s,\n  "tree_sha256_before": "%s",\n  "tree_sha256_after": "%s",\n  "tree_unchanged": %s\n}\n' \
    "$SESSION_ID" "$([ "$MAN_BEFORE" = 0 ] && echo true || echo false)" "$([ "$man_after" = 0 ] && echo true || echo false)" \
    "$([ "$cor_after" = 0 ] && echo true || echo false)" "$(grep -c ': OK$' "$E/manifest-after-$SESSION_ID.txt")" "$TREE_SHA" "$t_after" \
    "$([ "$TREE_SHA" = "$t_after" ] && echo true || echo false)" > "$E/integrity-$SESSION_ID.json"
  cp "$E/integrity-$SESSION_ID.json" "$E/integrity.json"; cat "$E/integrity-$SESSION_ID.json"
}

# ------------------------------------------------------------------ 3. image and campaign identity
RUNNING=$(docker ps -q | wc -l | tr -d ' ')
if [ "$MODE" = setup ]; then echo "running containers at setup: $RUNNING (recorded; setup is untimed)";
elif [ "$RUNNING" != 0 ]; then fail "$RUNNING other container(s) running on Host B (dedicated quiet window required)"; fi
if [ "$MODE" = resume ]; then
  IMAGE_ID="$(jget built_image_id)"; RTAG="zcorp-bench:$CAMPAIGN_ID"; MISMATCH=""
  chk() { [ "$2" = "$3" ] || MISMATCH="$MISMATCH; $1 (recorded '$2', now '$3')"; }
  chk "protocol version" "$(jget protocol_version)" "$PROTOCOL_VERSION"
  chk "kit" "$(jget kit)" "$KIT_VERSION"
  chk "tree (kit, generator, manifests)" "$(jget campaign_paths_status_sha256)" "$TREE_SHA"
  chk "artifact manifest" "$(jget manifest_sha256)" "$(sha "$REPO/ARTIFACTS.sha256")"
  chk "synthetic corpus" "$(jget synthetic_corpus_sha256)" "$(sha "$REPO/SYNTHETIC-CORPUS.sha256")"
  chk "adapter" "$(jget adapter_sha256)" "$(sha "$KIT/lib/cpu-visibility.js")"
  chk "runner" "$(jget 'bench\/run-campaign.sh')" "$(sha "$KIT/run-campaign.sh")"
  chk "compose file" "$(jget 'bench\/compose.yaml')" "$(sha "$KIT/compose.yaml")"
  chk "Dockerfile" "$(jget 'bench\/Dockerfile')" "$(sha "$KIT/Dockerfile")"
  chk "benchmark image" "$IMAGE_ID" "$(docker image inspect --format '{{.Id}}' "$RTAG" 2>/dev/null)"
  chk "Docker Engine" "$(jget engine)" "$ENGINE"
  chk "kernel" "$(jget kernel)" "$KERNEL"
  chk "host CPUs" "$(jget vm_ncpu)" "$NCPU"
  chk "host memory" "$(jget vm_mem_bytes)" "$MEMB"
  chk "frozen host state" "$(jget host_frozen_state)" "$FROZEN_STATE"
  if [ -n "$MISMATCH" ]; then fail "REFUSE resume: campaign identity differs${MISMATCH}"; fi
  echo "resume identity: all recorded identities match"
  export ZCORP_IMAGE="$RTAG" ZCORP_IMAGE_ID="$IMAGE_ID"
else
  docker build --platform "$PLATFORM" -f "$KIT/Dockerfile" -t "$IMAGE_TAG" "$KIT" > "$E/docker-build-$SESSION_ID.log" 2>&1 || fail "image build failed"
  IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$IMAGE_TAG")
  IMAGE_REF="zcorp-bench:$CAMPAIGN_ID"
  docker tag "$IMAGE_ID" "$IMAGE_REF" || fail "could not tag the campaign image"
  IMAGE_PLATFORM=$(docker image inspect --format '{{.Os}}/{{.Architecture}}' "$IMAGE_ID")
  docker buildx imagetools inspect --raw "$BASE_REF" > "$E/base-image-index.json" 2>/dev/null || echo '{}' > "$E/base-image-index.json"
  echo "image $IMAGE_REF id=$IMAGE_ID platform=$IMAGE_PLATFORM"
  export ZCORP_IMAGE="$IMAGE_REF" ZCORP_IMAGE_ID="$IMAGE_ID"
  if [ "$MODE" = setup ]; then
    # Untimed: regenerate the 11 PLONK proving keys (deterministic from the R1CS and pot16_final.ptau), then the full manifest.
    mkdir -p "$REPO/data/plonk-zkeys"
    docker run --rm --init --network none --platform "$PLATFORM" --cpuset-cpus 1-8 --cpuset-mems "$CPUSET_MEMS" --memory 12g --memory-swap 12g \
      -e ZCORP_CPUS=8 -e NODE_OPTIONS="--require /opt/zcorp/lib/cpu-visibility.js --max-old-space-size=7000" \
      --mount "type=bind,source=$REPO,target=/work,readonly" --mount "type=bind,source=$REPO/data/plonk-zkeys,target=/out" -w /work "$IMAGE_ID" node /opt/zcorp/setup_plonk_zkeys.js </dev/null \
      > "$E/setup-plonk-$SESSION_ID.log" 2>&1 || fail "PLONK key regeneration failed"
    ( cd "$REPO" && sha256sum -c ARTIFACTS.sha256 > "$E/manifest-setup-$SESSION_ID.txt" 2>&1 ) || fail "ARTIFACTS.sha256 check failed after setup"
    MAN_BEFORE=0; integrity_after
    echo "result: SETUP PASS (image $IMAGE_ID; ARTIFACTS.sha256 $(grep -c ': OK$' "$E/manifest-setup-$SESSION_ID.txt") OK)" | tee "$E/RESULT-$SESSION_ID.txt"
    cp "$E/RESULT-$SESSION_ID.txt" "$E/RESULT.txt"; session_event end "SETUP PASS"; exit 0
  fi
  SCHED_ENV=(); if [ "$CMODE" = campaign ]; then SCHED_ENV=(-e "ZCORP_EXPECT_SCHEDULE_SHA256=$HOST_A_SCHEDULE_SHA256" -e "ZCORP_EXPECT_PLAN_SHA256=$HOST_A_PLAN_SHA256"); fi
  P7ENV=(); [ -n "${ZCORP_P7_DEPTHS:-}" ] && P7ENV=(-e "ZCORP_P7_DEPTHS=$ZCORP_P7_DEPTHS")
  drun tools -e ZCORP_PROFILES="$PROFILES" -e ZCORP_BASE_ARCH=amd64 \
    -e ZCORP_EXPECT_ARCH=x64 -e ZCORP_EXPECT_MACHINE=x86_64 -e ZCORP_EXPECT_CPU_IMPLEMENTER= -e ZCORP_EXPECT_CGROUP=2 \
    -e "ZCORP_EXPECT_CPU_MODEL=$EXPECT_CPU_MODEL" -e ZCORP_EXPECT_CPUSET_MEMS="$CPUSET_MEMS" "${SCHED_ENV[@]}" "${P7ENV[@]}" \
    -e ZCORP_META_GIT_COMMIT=none -e ZCORP_META_GIT_DIRTY=false -e ZCORP_META_GIT_STATUS_SHA256="$TREE_SHA" \
    -e "ZCORP_META_CAMPAIGN_PATHS=$TREE_PATHS" -e ZCORP_META_CAMPAIGN_PATHS_STATUS_SHA256="$TREE_SHA" \
    -e ZCORP_META_IMAGE_ID="$IMAGE_ID" -e ZCORP_META_IMAGE_TAG="$IMAGE_REF" -e ZCORP_META_BASE_IMAGE_REF="$BASE_REF" \
    -e ZCORP_META_PLATFORM="$IMAGE_PLATFORM" -e "ZCORP_META_DOCKER_DESKTOP=n/a (native Engine)" -e ZCORP_META_ENGINE="$ENGINE" \
    -e ZCORP_META_KERNEL="$KERNEL" -e ZCORP_META_VM_NCPU="$NCPU" -e ZCORP_META_VM_MEM_BYTES="$MEMB" -e ZCORP_META_CONFIGURED_MEMORY_MIB= \
    -e "ZCORP_META_HOST_FROZEN_STATE=$FROZEN_STATE" \
    -e ZCORP_META_RUNNER_SHA256="$(sha "$KIT/run-campaign.sh")" -e ZCORP_META_COMPOSE_SHA256="$(sha "$KIT/compose.yaml")" \
    -e ZCORP_META_DOCKERFILE_SHA256="$(sha "$KIT/Dockerfile")" \
    -- node /opt/zcorp/make_schedule.js --campaign-id "$CAMPAIGN_ID" --mode "$CMODE" --plan "$PLAN" || fail "campaign initialisation failed"
  drun tools -- node /opt/zcorp/provenance.js || fail "P7 provenance failed (see provenance/p7.json)"
fi

# ------------------------------------------------------------------ 4. container pre-flight and adapter controls (every session)
for spec in $(echo "$PROFILES" | tr ',' ' '); do
  pid=${spec%%:*}
  drun "$pid" -- node /opt/zcorp/preflight.js || fail "container pre-flight failed for $pid"
done
P="$E/preflight/$SESSION_ID"; CTRL_CPUSET=1-2; CTRL_N=2
echo "size $CTRL_N" > "$P/controls-exit.txt"
docker run --rm --platform "$PLATFORM" --network none --cpuset-cpus="$CTRL_CPUSET" --memory=8g --memory-swap=8g \
  -e ZCORP_CPUS="$CTRL_N" -e ZCORP_PROFILE=control -e NODE_OPTIONS="--max-old-space-size=4096" \
  -v "$REPO":/work:ro "$IMAGE_ID" node /opt/zcorp/preflight.js --probe </dev/null > "$P/control-no-adapter.out" 2> "$P/control-no-adapter.err"
echo "no-adapter $?" >> "$P/controls-exit.txt"
docker run --rm --platform "$PLATFORM" --network none --cpuset-cpus="$CTRL_CPUSET" --memory=8g --memory-swap=8g \
  -e ZCORP_CPUS="$((CTRL_N * 2))" -e ZCORP_PROFILE=control -v "$REPO":/work:ro "$IMAGE_ID" node /opt/zcorp/preflight.js --probe </dev/null \
  > "$P/control-mismatch.out" 2> "$P/control-mismatch.err"
echo "mismatch $?" >> "$P/controls-exit.txt"
docker run --rm --platform "$PLATFORM" --network none --cpus="$CTRL_N" --memory=8g --memory-swap=8g \
  -e ZCORP_CPUS="$CTRL_N" -e ZCORP_PROFILE=control -v "$REPO":/work:ro "$IMAGE_ID" node /opt/zcorp/preflight.js --probe </dev/null \
  > "$P/control-quota-only.out" 2> "$P/control-quota-only.err"
echo "quota-only $?" >> "$P/controls-exit.txt"
drun tools -- node /opt/zcorp/record_controls.js || fail "adapter controls did not behave as expected"

if [ "$MODE" = preflight ]; then
  integrity_after
  echo "result: PREFLIGHT PASS (no rounds run; session $SESSION_ID)" | tee "$E/RESULT-$SESSION_ID.txt"; cp "$E/RESULT-$SESSION_ID.txt" "$E/RESULT.txt"
  session_event end "PREFLIGHT PASS"; exit 0
fi

# ------------------------------------------------------------------ 5. resume bookkeeping and round units
drun tools -- node /opt/zcorp/campaign_state.js --session "$SESSION_ID" || fail "REFUSE: campaign state check failed"
UNITS="$OUT/prover/sessions/$SESSION_ID/units.csv"
HS="$OUT/prover/host_samples.csv"
[ -f "$HS" ] || echo "campaign_id,session_id,seq,kind,round,round_attempt,profile_id,phase,utc,loadavg,running_containers,busy_alloc_max,busy_siblings_max,busy_other_cpu_equiv,mhz_alloc,pkg_temp_c,core_throttle_alloc,pkg_throttle,governor,no_turbo,numa_balancing,thp,inhibit,accepted,violations" > "$HS"
sample_row() { # seq kind round attempt profile phase check-json
  python3 - "$7" "$CAMPAIGN_ID,$SESSION_ID,$1,$2,$3,$4,$5,$6" >> "$HS" <<'PY'
import json, sys
try:
    r = json.loads(open(sys.argv[1]).read())
except Exception:
    r = {}
q = lambda x: '"' + str('' if x is None else x).replace('"', "'") + '"'
print(sys.argv[2] + ',' + ','.join(q(r.get(k)) for k in ('utc_b', 'loadavg', 'running_containers', 'busy_alloc_max', 'busy_siblings_max',
      'busy_other_cpu_equiv', 'mhz_alloc', 'pkg_temp_c', 'core_throttle_alloc', 'pkg_throttle', 'governor', 'no_turbo', 'numa_balancing',
      'thp', 'inhibit', 'accepted')) + ',' + q('; '.join(r.get('violations') or [])))
PY
}
violations() { python3 -c 'import json,sys
try: v = json.load(open(sys.argv[1])).get("violations") or []
except Exception: v = ["check output unreadable"]
print("; ".join(v) or "sleep inhibitor lost")' "$1"; }

ACCEPTED=0; CONTAINERS=0; STOPPED=0
exec 3< <(tail -n +2 "$UNITS")
while IFS=, read -r kind round attempt profiles <&3; do
  if [ -n "${ZCORP_STOP_AFTER_ROUNDS:-}" ] && [ "$ACCEPTED" -ge "$ZCORP_STOP_AFTER_ROUNDS" ]; then STOPPED=1; break; fi
  echo "== round unit: $kind round $round attempt $attempt ($profiles)"
  for pid in $(echo "$profiles" | tr ';' ' '); do
    CONTAINERS=$((CONTAINERS + 1)); alloc=$(svc_cpuset "$pid"); tag="c$(printf %04d $CONTAINERS)"
    echo "== [$CONTAINERS] $kind round $round attempt $attempt: $pid (CPUs $alloc, mems $CPUSET_MEMS)"
    # pre: 2 s quiet window right before the container (violation -> unit stays without outcome, rerun whole on resume)
    python3 "$KIT/hostb_quiet.py" snap "$Q/$tag-pre-a.json"; sleep 2; python3 "$KIT/hostb_quiet.py" snap "$Q/$tag-pre-b.json"
    python3 "$KIT/hostb_quiet.py" check "$Q/$tag-pre-a.json" "$Q/$tag-pre-b.json" --mode pre --alloc "$alloc" --frozen "$FROZEN_STATE" > "$Q/$tag-pre.json"; prc=$?
    sample_row "$CONTAINERS" "$kind" "$round" "$attempt" "$pid" before "$Q/$tag-pre.json"
    inh_ok || prc=1
    [ $prc = 0 ] || fail "host conditions not met before container $CONTAINERS ($(violations "$Q/$tag-pre.json")); $kind round $round attempt $attempt stays without outcome and is rerun whole on resume"
    python3 "$KIT/hostb_quiet.py" snap "$Q/$tag-run-a.json"
    drun "$pid" -- node --expose-gc /opt/zcorp/harness.js --kind "$kind" --round "$round" --attempt "$attempt"
    rc=$?
    python3 "$KIT/hostb_quiet.py" snap "$Q/$tag-run-b.json"
    python3 "$KIT/hostb_quiet.py" check "$Q/$tag-run-a.json" "$Q/$tag-run-b.json" --mode during --alloc "$alloc" --frozen "$FROZEN_STATE" > "$Q/$tag-during.json"; drc=$?
    sample_row "$CONTAINERS" "$kind" "$round" "$attempt" "$pid" during "$Q/$tag-during.json"
    inh_ok || drc=1
    if [ $rc -ne 0 ]; then
      drun tools -- node /opt/zcorp/validate_round.js --kind "$kind" --round "$round" --attempt "$attempt"
      fail "container for $pid exited $rc; $kind round $round attempt $attempt recorded as failed (rerun as a new attempt on resume)"
    fi
    if [ $drc -ne 0 ]; then
      drun tools -- node /opt/zcorp/validate_round.js --kind "$kind" --round "$round" --attempt "$attempt" --host-violation "container $CONTAINERS ($pid): $(violations "$Q/$tag-during.json")"
      fail "host conditions violated during container $CONTAINERS; $kind round $round attempt $attempt recorded as failed (rerun as a new attempt on resume)"
    fi
    if [ -n "${ZCORP_TEST_INTERRUPT_AFTER_CONTAINERS:-}" ] && [ "$CONTAINERS" -ge "$ZCORP_TEST_INTERRUPT_AFTER_CONTAINERS" ]; then
      echo "SIMULATED INTERRUPTION (dry-run test) after $CONTAINERS container(s), inside $kind round $round attempt $attempt"
      echo "result: INTERRUPTED (simulated, session $SESSION_ID)" > "$E/RESULT-$SESSION_ID.txt"; cp "$E/RESULT-$SESSION_ID.txt" "$E/RESULT.txt"
      exit 3
    fi
  done
  drun tools -- node /opt/zcorp/validate_round.js --kind "$kind" --round "$round" --attempt "$attempt" \
    || fail "$kind round $round attempt $attempt failed round validation (rerun as a new attempt on resume)"
  ACCEPTED=$((ACCEPTED + 1))
done
exec 3<&-

# ------------------------------------------------------------------ 6. integrity (after) and summary
integrity_after
REMAINING=$(( $(tail -n +2 "$UNITS" | wc -l) - ACCEPTED ))
if [ "$STOPPED" = 1 ] || [ "$REMAINING" -gt 0 ]; then
  drun tools -- node /opt/zcorp/summarize_prover.js --allow-partial; SUMRC=$?
  if [ $SUMRC -eq 0 ]; then
    echo "result: STOPPED after $ACCEPTED accepted round(s) this session; $REMAINING remaining; resume with: bash bench/run-campaign.sh resume $OUT" | tee "$E/RESULT-$SESSION_ID.txt"
    cp "$E/RESULT-$SESSION_ID.txt" "$E/RESULT.txt"; session_event end "STOPPED ($ACCEPTED accepted, $REMAINING remaining)"; exit 0
  fi
  fail "partial validation failed (see derived/validation.json)"
fi
drun tools -- node /opt/zcorp/summarize_prover.js; SUMRC=$?
if [ $SUMRC -eq 0 ]; then
  echo "result: PASS ($CMODE $CAMPAIGN_ID; session $SESSION_ID; see derived/validation.json)" | tee "$E/RESULT-$SESSION_ID.txt"
  cp "$E/RESULT-$SESSION_ID.txt" "$E/RESULT.txt"; session_event end "PASS"
else
  fail "validation (see derived/validation.json)"
fi
