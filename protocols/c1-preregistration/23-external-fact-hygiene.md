# 23 — External-fact hygiene (anvil-zksync release)

**Rule:** a statement about a third-party release enters V2 records only with primary evidence (repository, tag,
commit, date, URL). It is never used as a scientific premise.

| Item | Primary evidence obtained (2026-10-04) | Status |
|---|---|---|
| Repository | `https://github.com/matter-labs/anvil-zksync.git` | verified (git over HTTPS) |
| Tag `v0.7.1` | `git ls-remote` → lightweight tag → commit `af51110401b98a187481ff2022aeb9d4e5fa5b0b` | verified |
| Commit date of that tag | committer / author date 2026-09-14T14:45:13-05:00 (subject "feat: add --evm-emulator-path …", #780) | verified |
| GitHub *release* publication time | An earlier session read 2026-10-02T15:29:20Z from the GitHub releases API; the API is not reachable from this session, so it was **not re-verified** | unverified — do not propagate |
| Tag `v0.6.11` (pinned) | commit `5cafc9ab6e16594f2fa85959ecf7b892425f48c5`; binary sha256 equals the V1 pin | verified |

**Consequence for V2:** none. The EraVM campaign keeps anvil-zksync **0.6.11**. Correct wording, if ever needed:
"anvil-zksync tag v0.7.1 (commit af51110, committed 2026-09-14)". The phrase "v0.7.1 released 2026-10-02" is withdrawn
from V2 records unless the owner re-verifies it.
