# 08 — Deviations and amendments (V2-C2)

1. After the stage-1 freeze no file of this package changes. A correction is an appended amendment record outside the
   package (`V2-C2-amendments/AMD-C2-n.md`, hashed, with UTC), allowed only before the stage-2 numeric predictions exist,
   and only for errors that do not depend on any FFLONK quantity (e.g. a crash of the structural tool, a path).
2. After the stage-2 freeze nothing that affects a prediction may change. Problems found later are reported as
   deviations; the affected proofs become NOT EVALUABLE; predictions are never recomputed after a FFLONK measurement.
3. Stage-2 events that must be recorded: tool reruns (with reason), gate failures, artifact hashes, tool versions, any
   difference between the stage-2 manifest and the registered FFLONK cell definitions.
4. If the C1 doc-21 path changes (e.g. RETAIN-REDUCED or DROP), C2 is NOT RUN for d = 11; a reduced family is not a C2
   target.
5. C1's deviations policy (`V2-C1-preregistration/20-deviations-policy.md`) governs the registered FFLONK cells
   themselves; C2 never alters them.
