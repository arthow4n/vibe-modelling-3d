# Space-first closure research — four unprinted experiments

The user requests a fresh comparison of minimal retention mechanisms, including
their idea of using the free shell near the overlap tip. Interior access and flat
walls take priority over preserving the M5 cantilever architecture. The authorized
deliverable is visual research and one representative test piece per idea, not a
new adopted full case. Full reference geometry is built only to derive samples
and check the space/assembly consequences. M5 and the printed failed M1 remain
unchanged references. No new print has been reported or requested.

The user explicitly requests **no sub-agents unless they ask for them**. This
phase uses implementation and self-review only.

**Current lower-material print option:** the user subsequently requested shorter
retention-only trials. Use the [four short R1-S–R4-S pairs](closure_short.md) for
that purpose: full XY shape, shorter axial walls and recessed pull gaps. The long
specimens below remain the reference for the earlier stiffness/force studies;
their force estimates do not transfer to the shortened trials.

For the later question “how much weight could hang from the cap?”, see the
[straight-pull force investigation](closure_pull.md) and its
[section/force drawing](closure_research/pull_estimate.svg). It adds a conditional
R1/R2 spring/ramp estimate using both cap and body compliance; it does not turn
the original radial bending tests into holding-force measurements. R3 bead
pull-off and R4 rail-lifting capacities remain unresolved. The four specimen
sources, paired exports and slice receipts are unchanged by this continuation.

## Questions and scope before computation

Compare the user's broad-wall tip snap (R1), the same tip snap on the end walls
(R2), a continuous perimeter bead (R3), and a sliding broad-face lid with sidewall
detents (R4). R1–R3 preserve the whole 77 × 51.2 mm circumference, 78 mm guide and
complete 90 mm cap; their body crops retain 16 mm below the joint. A small isolated
clip would not represent the shell's deformation. R4 keeps the full width/depth
and both ends in a 70 mm long sample; a 264 mm reference establishes packaging and
travel, but the short specimen cannot establish full-length sliding friction or
warping. All four use plastic wall bending rather than a guarded internal arm.

First check real capture, the entire released path and whether nominal central
storage space actually grows. A tip catch without a runout is a negative control:
after popping out of its pocket, it would rub along most of the long cap. Keep a
short retaining lip, with a recessed clearance track below it, so the shell can
recover after the initial snap. For the slider, prove that rails independently
block lifting and that removing the detents removes the axial obstruction.

Use direct CAD for these questions. Then use a small no-contact CalculiX study
to see whether broad/end walls bend differently under the same radial traction.
The sample bottom is clamped as a declared bench fixture, not a simulated hand.
Run at assumed isotropic E1200 MPa/nu .38, without claiming printed PETG calibration;
inspect mesh sensitivity of deflection at the loaded wall and strain location.
Equal-material linear comparisons can be scaled over E900–1800, but that does not
cover anisotropy or a material law outside small deformation. Stop when the
orientation/feasibility comparison is resolved, or record the actual numerical
limitation. Do not build an assembly-contact solver to give these samples an
unearned holding-force rating. Measured pull-off, feel, recovery and wear remain
the questions for the specimens.

## Start with the drawings and matching specimens

[Four concepts](closure_research/concepts.svg) ·
[Tip catch: seated, blocked pull, then recovery](closure_research/tip_motion.svg) ·
[Actual shell deformation](closure_research/wall_flexure.svg) ·
[Sliding rail/detent section](closure_research/slide_section.svg)

| Specimen | Source | STEP | STL | What this comparison can decide |
| --- | --- | --- | --- | --- |
| **R1 broad-wall tip snap — user's idea** | [Python](../shell_broad_test.py) | [R1 pair](../shell_broad_test.step) | [R1 pair](../shell_broad_test.stl) | Can an existing broad sleeve wall give enough snap while keeping opening practical? |
| **R2 end-wall tip snap — orientation control** | [Python](../shell_end_test.py) | [R2 pair](../shell_end_test.step) | [R2 pair](../shell_end_test.stl) | Same dimensions/tooth but shorter wall span: is the firmer spring more useful? |
| **R3 continuous perimeter bead** | [Python](../perimeter_bead_test.py) | [R3 pair](../perimeter_bead_test.step) | [R3 pair](../perimeter_bead_test.stl) | Does distributed capture help, or make insertion/opening too stiff or prone to peeling? |
| **R4 sliding broad-face lid** | [Python](../slide_wall_test.py) | [R4 pair](../slide_wall_test.step) | [R4 pair](../slide_wall_test.stl) | Is broad-face loading worth the sliding travel and rail/warping sensitivity? |

Use each matching pair; do not mix these caps or any M5 parts. R1–R3 bodies print
upright and caps inverted, with separate pieces on one plate. Each crop is 94 mm
high; its cap is the complete 90 mm production-reference cap. Their closed sample
is 106 mm long. R4 prints as a tray on its broad floor with the lid outside-face
down beside it. Its sample is 70 mm long, full width/depth. Individual source
names, visible detent locations and the drawings distinguish the pairs.

[R1 print view](../renders/tests/closure_research/shell_broad_test_front.png) ·
[R2 print view](../renders/tests/closure_research/shell_end_test_front.png) ·
[R3 print view](../renders/tests/closure_research/perimeter_bead_test_front.png) ·
[R4 print view](../renders/tests/closure_research/slide_wall_test_isometric.png)

No new full-case STEP/STL is published or adopted. The authoritative shared
[builder](../closure_research_design.py) makes full reference shells because that
is simpler and more faithful than drawing unrelated little clips, then produces
the specified samples. This follows the user's explicit permission to build full
geometry when it simplifies representative crops.

## What is physically different

**R1 and R2:** the enclosure wall itself is the spring. Two small outward bumps
sit 3 mm below the free sleeve tip, engaging recesses in the cap. The guide wall
is 1.6 mm; there are no slots, separate leaves, closed inward guards or buttons.
The bumps project .65 mm across a .15 mm side clearance, giving .50 mm nominal
radial capture. Both faces are ramps: these are intentional push-on/pull-off
closures, unlike the previous press-to-release architecture. An external pull
can therefore open them if it overcomes the same elastic barrier used deliberately.
That tradeoff must be assessed, not excused because commercial boxes also snap.

The lower runout track is a recess in the cap wall, not another inward channel
box. A short solid retaining lip remains between the receiving pocket and that
track. The nominal seated parts are clear and unstrained in CAD. During the
first few millimetres of withdrawal the lip demands wall deformation; after 6 mm
the catch can recover into the track, and all sampled lifts to full withdrawal
are clear. The version without a track still collides at 30 mm lift. This was a
consequential correction discovered before handing over the samples.

**R3:** the same idea becomes a continuous rounded-rectangle bead. It has the
same storage gauge and radial capture, but requires a coupled change of the
whole perimeter. Its cap runout is a broad internal rebate, leaving about 1.35 mm
of cap skin. It is not a circular annular-joint formula transplanted to a rectangle.
No native full-perimeter snap-force study is claimed. R3 is retained as an
informative print comparison, not a predicted winner.

**R4:** the case opens along a broad face. Sloping keys underneath the lid run
under the sidewalls. Rails retain the lid against lifting even if the two small
side detents are removed; the detents resist sliding. The sidewalls bend locally
as their bumps cross receiving lips, then recover into clearance tracks. There
is no separate release spring. The first steep tooth was revised to a longer
lead/return ramp: .55 mm radial projection over 1.75 mm of axial travel, rather
than forcing a steep shoulder through an already stiff wall. The 1 mm high tooth
root is not a single .2 mm printed layer. The earlier steep-CAD option remains
reproducible with `slide(70, gentle_ramps=False)`; its local wall study is retained
under `flex/slide_wall_steep_cam` without relabelling it as the current geometry.

R4 has a real operational cost: the full reference needs roughly a case length
of clear space to slide the lid completely off. A 70 mm coupon does not establish
that 264 mm travel is convenient in a bag or that long rails stay straight. Its
small volume advantage over R1 is not sufficient reason by itself to adopt it.

## Space recovered and what “flat” means here

All full references keep the M5 **77 × 51.2 × 264 mm** maximum envelope, with
flat exteriors. There is no increase in broad-body width in this comparison.

| Quantity | M5 reference | R1/R2/R3 tip-snap references | R4 sliding reference |
| --- | --- | --- | --- |
| Restrictive central width | 56.9 mm at catch guards | **69.5 mm** through the sleeve | 70.6 mm open-tray width; lid keys occupy only the upper strip |
| Central area through the long joint | 2866 mm² above catches; 2691 at catches | **3033 mm²**, without guard projections | Broad-face opening instead of an end aperture |
| Approximate central connected void | 833.8 mL | **859.7 mL**, about +26 mL / 3.1% | About 864.8 mL; includes connected rail clearances |

The important gain is removing the narrow catch bottleneck: **12.6 mm / 22% more
clear width**. The total volume gain is more modest. The three tip-snap versions
have the same central sections; the body's uniform inner rounded rectangle is
69.5 × 43.7 mm. Its four broad inside faces are flat; a smooth 6 mm transition
still joins that sleeve to the wider lower cavity. The cap has recesses outside
this storage envelope, and the overlap still needs two walls. This is not a
claim of one perfectly constant, featureless cavity over the entire case length.

R4's tray walls/floor are plain. The lid keys encroach near the top opening,
rather than forming deep boxes down the contents column. Its connected-volume
estimate includes small air slits at the rails that are not useful packing space;
do not interpret the roughly 5 mL difference from R1 as a proven usable-capacity
advantage. The broad opening is the meaningful distinction.

[CAD evidence](closure_research/cad.json) comes from actual solid sections and
the same central-void routine as M5. For R1, 4 mm and 2 mm station spacing give
860.34 and 859.70 mL; this is an approximate geometric estimate, not liquid
capacity or simultaneous contents packing. R4 gives 864.82 mL at both spacings
to the shown precision. The uniform storage gauge and full paths are checked
separately from these approximate totals. Existing liners are out of scope.

## What the computation established

[Shell study source](../closure_research_flex.py) ·
[Native summary](closure_research/flex_summary.json) ·
[Actual deformed-node witness](closure_research/deformation_witness.json) ·
[Diagram generator](../closure_research_drawings.py) and
[native-field plotting source](../closure_research_flex_report.py)

The native study uses Gmsh 4.15.2 and CalculiX 2.21 (version visible in solver
logs; the backend's separate version probe reports unknown). Quadratic C3D10
tetrahedra use 2.5 mm and 1.75 mm target sizes; the actual thin features create
additional local elements. All retained Jacobians are positive. The refined R1
and R2 cases each contain about 113,000 nodes. Full native inputs, fixture BREPs,
regions, logs, reactions and histories are retained for replay, with no native
computation deadline.

Each R1/R2 body's bottom cut ring is fully clamped. A **1 N radial traction** is
applied over the actual 5 mm² crest of one detent; the rest can deform. This is
a declared bench comparison, not an artificial assertion that the complete case
is rigid. The R4 sample has its floor clamped and a 1 N outward load on a local
outer-wall patch near its detent. These are separate no-contact shell questions.

| Native response, E1200 MPa / nu .38 | R1 broad wall | R2 end wall | R4 local slider wall |
| --- | --- | --- | --- |
| Mean radial motion of loaded patch at 1 N | .307 mm | .123 mm | .0174 mm |
| Patch response change under mesh refinement | .36% | .58% | 1.91% |
| Peak mechanical principal strain at 1 N | .125% | .103% | .053% |

The broad wall is about **2.5× more compliant** in the declared fixture. Under
the linear E900–1800 sensitivity, R1 moves about .205–.410 mm and R2 about
.082–.164 mm at the same load. That supports a real orientation comparison, not
one favorable modulus. The isotropic range does not bound every anisotropic
printed shell. Strain peaks near sharp features are retained as observations;
no printed strength or recovery limit was assigned.

Force-balance residuals are below 3e-8 relative in the refined runs. The selected
mesh-stability screen is 10% for orientation ranking; actual displacement changes
are much smaller. Peak strain was not the convergence acceptance quantity, so
do not promote it to a mesh-qualified failure stress. The deformation drawing
uses actual native nodes, with **radial movement enlarged 10× and heights left
undeformed**, rather than a schematic curve pretending to be a solve.

These radial loads are **not cap pull-off loads**. The cap also moves, both catches
can share or lose load, sliding/contact friction matters, and the whole guide can
rock or spread. R3's full perimeter response is not supplied by either local load.
None of these studies measures closing effort, pull-off force, impact resistance,
elastic recovery, creep or fatigue. They answer whether the existing shell can
provide useful spring travel and how orientation changes that response. That is
enough to justify the controlled specimens, not a new travel-retention rating.

## Manufacturing, sample scope and what to observe

Use the same intended PETG / .4 mm nozzle / .2 mm layers. Current reference
slices use the diagnostic QIDI Q2C profile, two walls and 7% adaptive cubic.
All four primary slices complete without notices; their automatic-support probes
generate no support. This is selected-profile toolpath acceptance, not physical
support-free, strength or Orca GUI STEP-import qualification. R1/R2 have local
cap tracks; R3's broad rebate changes its cap stiffness. Preserve those complete
caps and do not shorten them merely to save a little plastic.

The tip-snaps' bumps and lips are ramped; their 1.6 mm guide is retained rather
than thinning an existing arm. The open body crops stand on continuous annular
cut faces. Their complete caps retain the closed-end foot and rounded exterior.
R4 stands on its broad floor, lid outside-face down; the sloped rail profiles
avoid a horizontal rail roof that would need inaccessible support. The critical
1.2 mm rail necks were inspected in the actual slice at Z2.2: both have three
crossing paths and no uncovered interval in the local width approximation.
[Path view](closure_research/rail_paths.svg) and
[receipt](closure_research/rail_paths.json) retain the selected layer/locations;
this does not calibrate deposited polymer or layer strength.

If printing, start with **R1 and R2 as a matched comparison**. Keep material and
settings the same, seat fully, then compare centered pulling, gentle corner
peeling/rocking and repeated closing. Confirm that both catches engage and that
the wall returns after the first few millimetres. If R1 is too light but R2 binds,
that brackets a useful wall/engagement revision rather than a reason to add the
old guard boxes. R3 tests distributed capture; abandon it if it is impractically
stiff, fails to recover, or peels off just as easily. R4 tests rails and its detent
separately: it should slide intentionally, resist lifting, and recover after the
snap. Whitening, damage, binding, absent retention or residual distortion directs
revision. No result from these unprinted samples is currently marked physically
accepted. A click is not sufficient evidence of useful holding.
Keep fingers outside the open crop during retention comparisons; pressing a wall
from inside would introduce a release action unavailable in the complete case.

The tip samples omit the lower 158 mm of body and remote grips. They represent
the local closed perimeter, complete cap and guide span, not full-case bending
or backpack leverage. R4 preserves the rail/end-wall/locking geometry and print
directions but omits most of the 264 mm sliding span. Full-length drag, warping,
contents handling, access and travel retention remain open for any later adopted
case. No new print or full-case adoption is required to finish this research phase.

## Reproduce, check and preserve the work

The [CAD experiment](../closure_research_checks.py) records 66 actual poses across
the four concepts, separate detent-removal controls, the long-rubbing counterexample,
current sample crops and space comparisons. The [publication record](closure_research/publication.json)
ties each STEP/STL pair and slice to the shared current builder. A production-source
edit invalidates all four pairs. The existing [verification entry point](../verification.py)
exposes `--variant research-minimal-closures`; original product intent is preserved
with full-case/physical questions still UNKNOWN for this specimen-only phase.

```sh
./execute.py --threads 1 model/dental_travel_case/closure_research_checks.py
./execute.py --threads 1 model/dental_travel_case/closure_research_drawings.py
./execute.py --threads 1 model/dental_travel_case/closure_research_flex.py shell_broad NEW_NATIVE_DIRECTORY NEW_COMPACT_DIRECTORY
# Repeat the local structural study for shell_end and slide_wall.
./execute.py --threads 1 model/dental_travel_case/closure_research_flex_report.py BROAD_STUDY END_STUDY SLIDE_STUDY
./evaluate_model.py model/dental_travel_case/shell_broad_test.py --slice --report model/dental_travel_case/notes/closure_research/shell_broad_slice.json --summary
# Repeat evaluation for shell_end_test.py, perimeter_bead_test.py and slide_wall_test.py.
# Retain the slider slice to review its rail paths; Python remains frozen during publication.
./execute.py model/dental_travel_case/closure_research_toolpaths.py RETAINED_SLIDER_SLICE_DIRECTORY
./execute.py model/dental_travel_case/closure_research_delivery.py
./execute.py model/dental_travel_case/verification.py --variant research-minimal-closures
```

Native run directories must be new; retained compact evidence directories must
also be new. For reproduction in this checkout, choose an explicit new evidence
destination instead of overwriting the historical native archives. The field
report's `read_evidence` checks actual current geometry, material, fixture and
mesh identities before reusing the unchanged R1/R2 solves after the separate
slider revision. Old fields were not rebound by changing source hashes alone.

Self-review found and corrected the long post-snap rubbing path, the slider's
entry clearance and steep tooth ramps, and distinguished connected void from
actual loading access. The workflow lesson belongs in the existing design
guidance; no generic retention API, solver framework, score or approval gate was
introduced. The deliverable includes all drawings and exploration sources. No independent
reviewer or other sub-agent was invoked, following the user's latest instruction.

The relevant regression suite completed **142 passing tests**; the four new
research tests were rechecked after the numerical-script reproduction change.
[Current verification](closure_research/verification.json) reports PASS for the
research CAD, shell study and four diagnostic slices, with physical/full-product
questions UNKNOWN. `unresolved_evidence` is the expected product-level result for
unprinted specimens, not a failed command or an unfinished specimen deliverable.

## Print status and attribution

| Category | Status | Evidence / scope |
| --- | --- | --- |
| R1–R4 test pieces | Not reported printed; physical outcome UNKNOWN | Current paired STEP/STL and diagnostic slices; fit, holding, effort, recovery and wear unmeasured |
| New full product | N/A — research phase | Only full reference construction for space and sample fidelity; no new full-case print files adopted |
| Earlier M5 | Unprinted prototype | Source/exports unchanged; comparison reference |
| Original M1 | Printed; retention failed | Historical observations and geometry remain authoritative |

Primary model GPT-6 (developer-provided identity), reasoning effort not exposed;
Codex CLI harness, provider OpenAI. Historical contributors retain their attribution.

## Research basis

[Covestro's snap-fit design guide](https://solutions.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1557220896.pdf)
distinguishes bending, torsional and annular mechanisms and discusses both mating
parts being elastic. Its circular annular equations do not directly represent
this rectangular case. The [Protolabs printing guidance](https://www.hubs.com/knowledge-base/how-design-snap-fit-joints-3d-printing/)
also distinguishes manufacturing effects. These are mechanism references, not
material calibration: an injection-moulded polypropylene box and this PETG FDM
shell need not flex, recover or wear alike. The useful principle is to put the
elasticity into walls already needed for the enclosure, while retaining a real
geometric obstruction and an intentional opening path.
