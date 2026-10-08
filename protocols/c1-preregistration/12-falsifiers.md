# 12 — Pre-registered falsifiers (V2-C1, frozen)

Each falsifier is evaluated by `scoring/score_c1.py` with the criteria of `13-criteria.md`. "Falsified" means the
stated hypothesis is reported as not supported, with the failing cells; it is not repaired by changing the model,
the tolerance or the cell roles (`20-…` §3).

| ID | Hypothesis | Falsified if (any of) | Scorer section |
|---|---|---|---|
| F1a | H1 structure | any trace or frame shows EC-call counts or transcript rounds different from the template formulas | AC (L1-STRUCT) |
| F1b | H1 monotone ratio | in a CORE regime, r_E(k₂) > r_E(k₁) + ε_E for some grid k₂ > k₁ with both cells outside the band | SG |
| F2a | H2 crossover location | the measured crossover interval of a CORE regime does not intersect its frozen interval | XO |
| F2b | H2 signs | any decided predicted sign is measured as the opposite decided class (FALSIFIED) | SG |
| F3 | H3 explanation | F1a or F2a in that regime, or the accounting identities fail there | AC, XO |
| F4 | H4 Level-4 ZKsync OS | any held-out G16 / PLONK proof (k ≠ 1, k ≤ 32, anchors) outside τ_cond; or an opcode in a trace without a v0.4.0 native price | ZC |
| F5a | H5 meter switch | any scored (k, level, template) with a binding meter other than predicted | NPG |
| F5b | H5 gas rule | L1-ZK fails beyond ±1 gas | AC |
| F5c | H5 ranking | at k = 4 the ranking does not reverse between the two levels bracketing its predicted switch (full design) | NPG + SG |
| F6 | H6 semantic invariance | an anchor / disclosure cell differs from the context-tag cell at the same k by more than ε_E | SEM |
| F7 | H7 v27 transfer | a v27 held-out cell outside its interval, or the v27 crossover outside its frozen interval | R, XO |
| F8 | H8 FFLONK (conditional) | any FFLONK proof outside τ_cond(F) | ZC |
| FP | prediction set P | a strictly-unseen held-out cell outside [lo, hi] in `09-numeric-predictions/predictions_cells.csv` | P |

**Interpretation rules fixed now**

1. If P fails but R passes for the same cells, the a-priori calibration source (P0 / smoke check) did not transfer to
   the registered setup; the structural claim may still stand under R and is worded "calibrated on the registered
   k ∈ {1, 4} cells".
2. If R fails on strictly-unseen k in a regime, no held-out-k predictive claim is made for that regime; the explanatory
   (Level 2/3) claim is judged separately by F3.
3. If F4 fails, the ZKsync OS claim is restated as explanatory only; observed errors are reported. Any tighter or looser
   tolerance proposed afterwards is a labelled post-hoc analysis.
4. A failed infrastructure check (AC controls, D-ACCEPT, D-HASH) stops interpretation of the affected regime until
   adjudicated; it is not a falsification of a hypothesis.
5. If the pilot falsifies a hypothesis, the full factorial still runs as registered (falsification is a result). A
   change of design after the pilot needs an amendment record with a reason that does not depend on the direction of
   the pilot outcome.
