#!/bin/bash
cd /root/full/harness
date -u +%Y-%m-%dT%H:%M:%SZ > /root/ffc/V2-MPI-FULL-01-FFLONK/RUNNER-START-UTC.txt
env -u SELFTEST_FOREIGN_JSON -u C1_KEYS RUN_ID=V2-MPI-FULL-01-FFLONK-run1 python3 run_campaign.py FULL-IF-FFLONK-GATE-PASSES /root/ffc/V2-MPI-FULL-01-FFLONK/fflonk --compiled /root/ffc/V2-MPI-FULL-01-FFLONK/compiled-fflonk --proofs /root/ffc/V2-MPI-FULL-01-FFLONK/proofs-fflonk > /root/ffc/V2-MPI-FULL-01-FFLONK/fflonk-orchestrator.stdout 2>&1 || { echo FFLONK-STOPPED > /root/ffc/V2-MPI-FULL-01-FFLONK/RUNNER-STATUS; exit 2; }
echo ALL-DONE > /root/ffc/V2-MPI-FULL-01-FFLONK/RUNNER-STATUS
