# Retention review question

The user requests an actual force estimate and a pragmatic recheck of sideways retention for smooth C, with authority to improve it. This reopens relevant investigation for C; it does not turn old incomplete contact studies into evidence or justify another solver-development campaign.

Before solving: use actual C shell radial compliance and exact catch/receiver clearance to estimate centered slow pull and an ideal undamped energy threshold. Solve opposed and single-end load fixtures to expose shell coupling. Retain the previous E1200 MPa / nu .38 hypothesis for comparison, with E900–2200 MPa and ±0.15 mm radial-fit scenarios. These are sensitivity assumptions, not measured bounds. No friction is credited. Use 10% mesh change in compliance / derived side movement and 10% withdrawal-step force change as the numerical stopping screens.

The prior 8–18 N centered slow-pull range is an agent-selected prototype design target, not a user requirement or ergonomics standard. A result substantially below it would support strengthening the flexible sleeve / receiving walls while keeping the smooth form. A result above it would support reducing local engagement or increasing compliance. Check energy as well as peak force: axial play permits acceleration before the catches load. Single-end opening and sideways peel remain separate from centered pull. Once a reasonable geometry decision is supported, finish the prototype recommendation without chasing a false impact rating.

After that decision, recheck both principal side-bearing directions with bands inside C's actual 27 mm coverage. This is a comparative weakness screen at the historical 2 N / 180 Nmm setup, not a pass threshold for a bag hit. Revisit rigid contact order and adverse guide play. Actual loaded knocks and useful grip/opening effort remain physical observations.

## First decision: strengthen C

The original C sleeve's paired-load compliance is about 0.254 mm/N. Its actual profile and this body compliance alone, assuming an infinitely stiff cap, give only 3.04 N centered slow pull and 1.25 N ideal undamped threshold at E1200. This optimistic model is already too weak relative to the retained prototype target. Completed paired/single body studies are retained. Cap jobs were deliberately interrupted because their completion could only lower this estimate and could no longer change the strengthening decision; they are not failures or completed evidence.

Selected correction: 1.8 mm sleeve walls instead of 1.2 mm, a 0.75 mm bite instead of 0.6 mm, and 2.0 mm continuous main end walls to retain 1.2 mm pocket backing. Exterior width becomes 75.8 mm, only 0.3 mm above the first C; depth and length stay unchanged. The main cavity and guide envelope stay unchanged, with the sleeve bore reduced by 1.2 mm overall in each axis. Recheck actual contents passage, collar/stop fit and withdrawal before adopting it.

The strengthened CAD check passes: the guide envelope remains at the previous mating size, all six sampled sleeve sections are 1.8 mm, the changed catches obstruct initial pull at both ends across guide play, the internal stop seats without nominal interference, and the sampled withdrawal clears after 6 mm. Actual individual brush/tube passages still pass. The first new body solve reduces radial compliance from about 0.254 to 0.081 mm/N; cap compliance is being resolved separately before interpreting a complete pull-force estimate.

## Cap meshing correction

The full cap's coarse quadratic mesh spent repeated 100-iteration high-order optimization passes on its curved surfaces. It had not reached a native structural result. A targeted CAD edge query ruled out microscopic sliver edges (smallest edges were the intended roughly 0.275 mm roof arcs). The productive correction is to resolve curvature, rather than remove the cap, call it rigid or pretend the incomplete jobs establish retention.

Fresh cap questions use the existing case-level mesh controls: 0.2 mm allowed minimum and 16 curvature samples, with 2.5 / 1.75 mm nominal mesh levels. `StructuralQuestion` now forwards those existing controls; a focused contract test checks defaults, explicit forwarding and rejected partial settings. Completed body studies retain their unchanged physical inputs. Cap meshes are reused through the native identity guard for the different force fixtures, with fresh load solutions; interrupted coarse cap jobs remain incomplete.

The 0.2 mm minimum cap mesh optimized successfully but produced a 140 MB solver deck. CalculiX then exited -9 without a loading result; substantial memory use was observed, but the exit alone does not identify a physical failure. That failed record is retained separately. The next cap setup allows a 0.5 mm minimum with the same 16 curvature samples and the same geometry, fixture and 10% response comparison. This targets adequate curved-surface resolution without the excessive local density. A failed study now exits nonzero before dependent mesh/load jobs can start; it cannot be counted as an acceptable prerequisite.

## Side-bearing decision: reinforce the broad walls

The first strengthened version's widthwise 2 N fixture gives about 0.59 mm relative upper-band motion and 3.97 mm extrapolated extra roof movement on the finer meshes (4.34 mm coarse). This is a conditional load-path response, not measured tooth opening or an impact result. Compared with the earlier reinforced shell's 1.23 mm X extrapolation, it identifies a plausible remaining flexible route. It does not justify claiming the catch has released, but it does justify an economical stiffness improvement.

The final direction retains the 0.75 mm bite and smooth outline, increases sleeve walls from 1.8 to 2.0 mm and main broad walls from 1.2 to 1.8 mm, and preserves the main cavity and guide envelope. Depth grows from 51.2 to 52.4 mm; width stays 75.8 mm and length 264 mm. This addresses the bending route rather than micro-tuning a ramp to pass the old agent-selected 3.5 N energy screen. That old scalar is not a universal travel-box criterion, and a fractional change around it cannot establish impact resistance.

The minimum cap force patches are nominal pressure windows, not measured uniform contact areas. The actual tooth crest is fully loaded (5 mm²). Mirror-reduced cap meshes sampled about 92% of the nominal lip window on the coarser mesh, but their mean response agrees with the full-cap fixture within 1%; selected areas and mesh sensitivity are retained. No peak stress or exact contact-pressure claim follows.

The completed first strengthened candidate also gave 12.56 mm extrapolated Y roof motion in the same conditional fixture. This supports using **2.0 mm uniform main walls**, rather than the initially proposed 1.8 mm broad walls, for the final candidate. Final exterior: **75.8 × 52.8 × 264 mm**. Final sleeve: **2.0 mm**, bite **0.75 mm**, main cavity unchanged, sleeve bore **67.6 × 44.6 mm**. Both ordinary main-wall directions are now 2.0 mm; pocket/runout backing remains 1.2 mm. The 3 mm exposed collar, axial stop and rounded ends are retained.

The alternative iterative linear solver was stopped after its residual reduction progressed poorly; it supplies no qualified force result. No new backend-selection interface is retained. The completed direct full-cap studies remain valid. Exact mirror reductions were then checked against them: mean cap compliance differs by 0.60% coarse and 0.18% fine, below the 5% comparison limit. The same mirrored geometry and principal-plane load symmetry apply to the final candidate. Loads are halved on half domains and normal displacement alone is fixed on each symmetry plane. This excludes asymmetric/diagonal impacts and does not constrain them by pretending a half model covers them. Completed native meshes are reused only for identical half-cap geometry/settings with fresh load solutions.

The final candidate's 2.5 mm nominal cap mesh completed, but the 1.75 mm nominal refinement failed Gmsh's high-order ScaledJac quality target. This is a rejected numerical mesh, not a product failure or a valid second response. The existing completed baseline is reused through QuestionStudy; one new 1.5 mm nominal cap refinement (factor 0.6) is requested with unchanged 0.5 mm curvature minimum and 16 samples. Body mesh levels remain 2.5 / 1.75 mm. No failed mesh is used for downstream force fixtures.

## Delivered C2 result

The completed final centered elastic estimate is 11.04 N opening and 6.76 N closing; the single-end fixture gives 6.00 N. The paired energy barrier is 3.86 Nmm, with a 4.65 N ideal undamped seated-release threshold. The material/fit scenarios span 6.33–25.02 N centered opening; these are assumptions, not measured limits or a confidence interval. Both shell compliances change less than 0.7% across their checked meshes. See `final/pull.json` for the complete fixtures, sensitivity and zero-bite control.

Final side-bearing roof proxies decrease by about 30% X and 56% Y relative to C1. Coarse/fine ranges are separated in both directions, supporting the reinforcement decision. X retains 11.6% mesh variation, so `final/side.json` deliberately retains `INCONCLUSIVE` for its original 10% precision screen. The comparison establishes a consistent improvement, not a release force or impact rating.

The final matching pair was exported together and accepted by OrcaSlicer 2.4.2 using the linked Q2C PETG profile, with no notices or generated support. The guarded source/export/slice association is in `../publication.json`; the selected checks and physical unknowns are in `../verification.json`. No printed force, loaded bump resistance, grip comfort or durability has been measured.

Regenerate the concise reports from completed native evidence with:

```sh
./execute.py --threads 1 model/dental_travel_case/smooth_retention_study.py retention-c2 report-pull
./execute.py --threads 1 model/dental_travel_case/smooth_retention_study.py retention-c1 report-side
./execute.py --threads 1 model/dental_travel_case/smooth_retention_study.py retention-c2 report-side
```
