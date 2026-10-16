# Flat-faced TPU damping box experiment

**I is approved by the user (2026-10-16).** In the tested **PLA** enclosure,
E, H and I all damped sound, but I was clearly best; solid A remained noisy.
The approved 4 mm I source and exports are preserved. This does not establish
equal acoustic performance with a PETG shell.

The next experiment is three much thinner I-derived cup/pad pairs for the same
shell. Keep the printed I as the reference. Thin variants are untested.

![Focused core sections](renders/selected_core_sections.png)

## Thinner I experiment

**Next print: [liners_thin.step](liners_thin.step)** — six parts, one matching
cup and roof pad per thickness. [STL](liners_thin.stl) ·
[parametric entry](liners_thin.py) · [builders](thin_design.py).
Reuse your PLA box, lid, screws and printed original I. No rigid-shell reprint.
All object-contact faces remain flat, with CAD chevrons behind all six faces.

| Recessed ID | Total lining | Reduction vs I | Outer backing / core / contact skin | Web normal thickness | Clear cavity |
| --- | --- | --- | --- | --- | --- |
| Original I, approved | 4.0 mm | Reference | 0.8 / 2.6 / 0.6 mm | 0.6 mm | 26 mm cube |
| I30 | 3.0 mm | 25% | 0.6 / 1.8 / 0.6 mm | 0.5 mm | 28 mm cube |
| I24 | 2.4 mm | 40% | 0.4 / 1.4 / 0.6 mm | 0.4 mm | 29.2 mm cube |
| I20 | 2.0 mm | 50% | 0.4 / 1.2 / 0.4 mm | 0.4 mm | 30 mm cube |

I30 is the conservative first candidate, I24 the middle challenge and I20 the
most aggressive. These are test priorities, not a measured acoustic ranking.
They preserve I's 3.6 mm web pitch and chevron centreline slope. Chevron amplitude
scales with core depth (0.346 / 0.269 / 0.231 mm). Thinner webs partly offset
shorter, potentially stiffer folded arms. Less available crush stroke, membrane
thickness, direct corner load paths and printing can change the result; no new
stiffness screen is promoted to an acoustic prediction.

All cups retain the accepted **34 × 34 × 34 mm** outer envelope and 0.2 mm per-side
shell allowance. Pads widen to 32.4 / 32.8 / 32.8 mm to retain 0.2 mm per-side
clearance in their own pockets. Each pad retains the original **0.2 mm axial
preload**: printed pad thickness is nominal lining plus 0.2 mm. Match cup and pad
IDs; do not mix thicknesses. The upper pocket is deeper for I30 than I20.
Recessed 6 mm labels are 0.2 mm deep, on exterior backing only. I24/I20 cup labels
leave 0.2 mm backing locally; label integrity is an intentional print challenge.

**Comparison:** use the same shell and nut, first empty, then gentle and firmer
X/Y/Z shakes and tumbling. Compare against the original I between pairs. The
cavity grows as the liner shrinks: more travel can increase impact speed, so this
is a practical same-box thickness experiment, not an isolated material test.
Report each ID's quietness versus I, axis, shake strength, sharp ticks versus dull
thuds, fit and any skin tearing. If I20 loses damping, I24/I30 help locate the
useful thickness limit. Do not infer equal performance from shell material alone.

### Thin-batch manufacturing plan

Use the same TPU filament as approved I if available (95A assumed for the
reference slice), Q2C 0.4 mm nozzle, **0.2 mm layers**, existing
[tpu-selected-process.json](profiles/tpu-selected-process.json), Arachne, two
requested walls, 100% solid fill where CAD contains material, supports off,
explicit **180° external/internal bridge direction**, unrotated components.
Hidden air channels remain CAD voids regardless of infill. The 0.4/0.5 mm webs
are intentional single-bead features, so path retention must be inspected.
Contact skins are three layers on I30/I24 and two on I20. Backings are three or
two layers except the recessed cup labels' one-layer local floor.

Print backing down, cups open upward, pads contact-skin upward. The compound is
118 × 74.4 mm, 34 mm tall, with broad bed contact and separated components.
The chevrons advance 0.154 mm sideways per 0.2 mm layer, preserving I's slope;
periodic roof gaps are about 3.0–3.1 mm and outermost gaps stay below 4 mm.
Both bridge ends land on CAD webs or edge material. Side webs grow vertically;
closed channels cannot be cleaned of support. Slice support proposals therefore
need local review; physical bridging, bonding, flatness and damping remain tests.
Do not add trapped supports merely because an automatic probe proposes them.

### Thin-batch verification and slice result

[Native final receipt](notes/thin_final.json): geometry valid, matching STEP/STL
published from the same selection and print placement; Orca **2.4.2** completed
one centered plate using the supplied TPU triplet. Estimate: **26.90 g / 4 h
20 min 43 s** (not measured). STL review does not verify GUI STEP import.
The receipt retains `review_required`: Orca reports a **floating cantilever** and
the automatic-support probe generates supports. The [headless path view](renders/thin_path_review.png)
locates these proposals inside the shallow floor/pad channels, Z 0.8–2.4 mm.
They would be trapped. The primary slice is intentionally support-free.

[Path inspection](notes/thin_path_review.json) finds transverse paths at all six
first contact-skin layers and retained web paths at **54 local witnesses**:
three depths on each floor and pad, and three depths on each of four side walls
for every variant. This resolves the sampled path-retention/direction questions;
it does not prove deposited thickness, bridging quality or flatness. The native
warning remains visible, and thin skins/labels remain physical print risks.

CAD receipts for [I30](notes/thin_verification_I30.json),
[I24](notes/thin_verification_I24.json), [I20](notes/thin_verification_I20.json)
report PASS for fit/travel, six flat skins, core air/material, labels and the
three-pair selection. Existing closure geometry and its retained checks are
unchanged. Thin-variant quietness, printed integrity and handling remain UNKNOWN.
The [original-I feedback receipt](notes/reported_I.json) separately retains user
approval in the reported PLA scope; the detailed directional protocol remains
UNKNOWN. Original builders and A/E/H/I exports are unchanged. The common CLI
conformance suite passes **87 tests**.

Reproduce the new batch from the repository root:

```sh
./evaluate_model.py model/tpu_damping_box/liners_thin.py --views none --slice --slice-keep-run --slice-printer .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json --slice-process model/tpu_damping_box/profiles/tpu-selected-process.json --slice-filament model/tpu_damping_box/profiles/tpu95a.json --report model/tpu_damping_box/notes/thin_final.json
./execute.py model/tpu_damping_box/review_thin_paths.py
./execute.py model/tpu_damping_box/verification.py --variant I20
```

## Print files

| Print | Primary STEP | Matching STL | Parametric entry point |
| --- | --- | --- | --- |
| New TPU batch: I30/I24/I20 | [liners_thin.step](liners_thin.step) | [liners_thin.stl](liners_thin.stl) | [liners_thin.py](liners_thin.py) |
| Existing shared shell (PLA in user test); no reprint needed | [tpu_damping_box.step](tpu_damping_box.step) | [tpu_damping_box.stl](tpu_damping_box.stl) | [tpu_damping_box.py](tpu_damping_box.py) |
| Retained A/E/H/I set; I approved | [liners_selected.step](liners_selected.step) | [liners_selected.stl](liners_selected.stl) | [liners_selected.py](liners_selected.py) |

[design.py](design.py) and [selection.py](selection.py) own the unchanged baseline.
Its selected plate contains exactly eight named parts:
one cup and one matching pad per ID. Do not print duplicate copies to rank sound:
repeat the shaking comparison with each same pair first.

The PETG enclosure and A/E geometry are unchanged from the first batch.
[Native export reassociation](notes/petg_selected_association.json) rebuilt the
current PETG entry point and reused its unchanged paired exports. An existing
PETG print, if available, needs no redesign for H/I. The original enclosure slice
remains scoped to the same geometry/settings; no print is inferred from it.

The closed box is **48 × 48 × 39.6 mm**, excluding screw heads.
All four baseline variants retain
an identical **26 × 26 × 26 mm clear shaking cavity** and **4 mm nominal lining**.
The cup is 34 mm square × 34 mm tall; its top pocket takes a 32 mm square pad.
The selected plate occupies about **76 × 158 mm** before print aids.
Diagnostic estimates: **25 g / about 1 hour PETG**, and **68 g / 10 h 13 min TPU**
for the four-set plate. These are slicer estimates, not measured prints. The
historical six-set batch was approximately 99 g / 14 h 37 min with its old profile;
part count and process both differ, so this is not an isolated speed comparison.

## Assembly and test object

Use **two M3 × 12 mm screws and two M3 nuts** from recorded stock for closure,
and **one separate M6 nut** as the loose test object. Use the existing driver
matching the actual screw head. Closure-nut proxies assume 5.5 mm across flats
and 2.4 mm thickness; actual stock measurements are unreported. A 12 mm cube
proxy can travel 14 mm on each cavity axis; it is not a measured M6 nut model.

1. Slide the two M3 nuts horizontally into the external corner ports, with flats
   parallel to the slot. The nuts bear beneath PETG roofs outside the chamber.
2. Match the recessed **A, E, H or I** on the cup underside and pad backing. The
   letters are 6 mm high and 0.3 mm recessed; no label interrupts an impact face.
3. Insert the cup and loose nut. Place the matching pad in its top pocket with
   the letter facing upward toward the PETG lid.
4. Fit the lid and tighten both screws evenly, just enough to seat it. The body
   rim is the hard stop. An intentional 0.2 mm axial pad squeeze aims to suppress
   liner movement; actual squeeze, effort and shake retention are unqualified.
5. Remove screws/lid and tip out the loose pad and nut to change sets. Flex/lift
   the cup out. Cup insertion allowance is 0.2 mm per side; retention comes from
   the closed housing, not an assumed friction fit.

The rim seats/stops, screw bores guide alignment, and captured nuts provide
clamping. With the fasteners omitted the parts still seat, but have no designed
closed retention. No glue, hinge, printed driver or multi-material print is needed.

## Retained baseline: why these four

| ID | Hidden structure on all six faces | Role in the focused print |
| --- | --- | --- |
| A | Uniform solid 4 mm TPU | Essential control: cellular structures must outperform actual solid TPU, not just bare PETG. |
| E | Chevron webs, 0.8 mm normal thickness; 0.8 mm contact skin | Retained folded reference with less demanding feature thickness. |
| H | Bowed webs, nominal 0.6 mm normal thickness; 0.6 mm contact skin | New pre-curved load path with a more compliant contact membrane. |
| I | Chevron webs, 0.6 mm normal thickness; 0.6 mm contact skin | New thinner version of E; lowest modeled initial web stiffness in this selected set. |

All use 0.8 mm outer backing and 3.6 mm web pitch. E has a 2.4 mm core; H/I have
2.6 mm core depth so thinning the skin does not change the 4 mm envelope. The
chevron centreline runs −0.5 / +0.5 / −0.5 mm through the depth. H bows 0.65 mm
sideways with a sine centreline, approximated by 32 short CAD segments. Its
thickness is nominally graph-normal; the curved profile is an approximation,
not an exactly offset mathematical surface.

The new skins are intentionally thinner, not perforated. Continuous inner corners
and roof-pad edge frames remain; their direct load paths may dominate some impacts.
The top-pad seam sits over TPU walls away from the PETG rim. Floor/pad cores print
horizontally and side cores vertically; FFF anisotropy remains part of the trial.

<a id="research"></a>

### Grounding and limits

The target is a compliant impact interface that reduces force transmitted into
the rigid shell during **light nut impacts**. High absorbed energy in a much larger
crash/drop test does not establish quietness here. Softness, impact pulse duration,
rebound, membrane vibration, friction and subjective sound remain different outcomes.

- [HSE impact-press case study](https://www.hse.gov.uk/noise/casestudies/soundsolutions/impactpress.htm)
  reports actual impact-noise reduction by cushioning metal contact with an
  elastomer insert. This supports the general contact-cushioning strategy. Its
  industrial press, proprietary materials and 8 mm inserts do not qualify our
  4 mm printed TPU liners or supply a transferable decibel estimate.
- [Agarwal and Jin, Architected Lattices with a Topological Transition](https://doi.org/10.1002/adem.202301192)
  uses experiments and simulations to investigate staged deformation with curved
  members bending before later contact/compaction. It informs the pre-bent H/I
  rationale, not their exact dimensions, initial stiffness or acoustic ranking.
- [TPU sandwich impact study (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8622326/)
  shows that geometry, strut thickness and boundary/collapse effects matter;
  thinner is not universally better. Its much larger impact specimens are not a
  validation of a light-nut test.
- [Buckling metamaterials study (2023)](https://doi.org/10.1002/adma.202301747)
  demonstrates nonlinear vibration damping associated with buckling. We therefore
  avoid assuming that structures successful after buckling will activate under
  a light nut impact. The new candidates have pre-bent load paths from the outset.

[compliance_screen.py](compliance_screen.py) provides a **linear Timoshenko-frame
screen of isolated 1 mm-wide webs**, normalized to E=1. Both end rotations are fixed;
base position is fixed; top normal displacement gives stiffness, with fixed/free
lateral-position sensitivity. Poisson ratio 0.49 and 0.3 are assumptions. The
unit displacement is a linear normalization, not a claimed operating deflection.

With lateral position fixed, relative initial web stiffness is E=1, H≈0.97 and
I≈0.55; C≈4.71, D≈3.43 and G≈2.46. The tiny H/E difference is not a robust ranking:
H mainly adds a different curved geometry and a thinner skin. The skin's idealized
bending-stiffness thickness factor is (0.6/0.8)³≈0.42, not a whole-liner stiffness
or measured material property. Model discretization at 64/128 segments changes H
stiffness by about 0.018%, below the declared 0.5% numerical screen.

The [input-associated result](notes/compliance_screen.json) also reports the free
lateral-end and Poisson-ratio sensitivities. These simplified boundary conditions
cannot establish which restraint the real membrane supplies. G changes from about 2.46×E stiffness with lateral restraint to about 0.54×E
when lateral travel is free; E/H/I are much less sensitive in this screen. That
constraint uncertainty is why G is omitted from the focused plate, not evidence
that G can never be quiet. The model omits the
skins, corners, frames, material rate dependence, contact, trapped/venting air,
printed anisotropy, impact dynamics and acoustics. It supports candidate selection
and explicitly **does not establish printed quietness or an optimum topology**.
No calibrated TPU modulus, loss factor or predicted decibels are reported.

### Screened but not on this plate

B/C are straight compression webs; D is the original inclined web; F has a thin
skin over straight webs; G is a new thin inclined concept retained in source for
comparison. The fixed-lateral screen gives less promising compliance than folded
members, so the focused plate spends its prints on E/H/I. Boundary sensitivity
and missing acoustic evidence mean this is a provisional selection, not proof
that every omitted design is worse.

Other possible future directions are separated supports under the flat skin,
a more fully suspended inner cup, or a graded core with a soft initial region
and a later stop. They are not added to this print: sparse supports risk long
unsupported skin spans; suspension requires resolving edge/clamping bypasses;
and a graded stop needs actual impact travel to place it usefully. A gyroid is
also possible but has no demonstrated advantage in this shallow core. Do not
multiply speculative topologies before testing whether I/H improve the actual sound.

## Printing and manufacturing review

Intended printer: Qidi Q2C, **0.4 mm nozzle, 0.2 mm layers**. PETG: two walls and
7% adaptive cubic as the existing starting setup. TPU: **two requested walls and
100% rectilinear fill**. The channels are CAD voids, not slicer infill. Keep TPU
spool, drying, orientation and settings the same across the selected batch.

For the selected batch use:

- [tpu-selected-process.json](profiles/tpu-selected-process.json)
- [tpu95a.json](profiles/tpu95a.json)
- [Q2C printer profile](../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json)

The selected process uses **Arachne** to preserve the new 0.6 mm webs; such thin
regions can use a single variable-width extrusion rather than two ordinary paths.
This is a deliberate sample feature, not a strength qualification. Nominal
wall/solid/fill speeds are 25 mm/s; first-layer/bridge speeds 15 mm/s. Generic TPU
95A resolves to 230°C nozzle, selected cool plate 30°C (hot-plate setting 35°C),
flow ratio 1 and a 4 mm³/s filament limit. These are diagnostic settings, not spool
calibration; actual temperatures and bed preparation must suit the TPU and plate.

**Supports OFF.** Hidden-core supports would be trapped and would alter compliance.
External/internal bridge direction is **180°**, relative angle off, aligned to the
model. In this delivered orientation roof paths cross the Y-running webs along X.
Do not auto-orient individual parts. Import the compound keeping the eight part
positions/orientations; GUI STEP import is untested. A changed layout or profile
needs a new hidden-roof direction review. The old automatic direction bridged
along channels on two historical pads, despite short cross-channel CAD spans.
[Orca bridge-angle documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/strength_settings_advanced#bridge-infill-direction)
explains the 180° override for absolute zero direction.

Wide flat backs provide bed contact. Side skins/webs grow from the floor; folded
webs have no newly floating islands. Flat skins close short channels (roughly
3 mm spans; some cup perimeter spans are 3.2 mm). H/I contact skins are three
nominal layers. Short TPU bridge sag, bonding, warping and intact channels remain
physical checks; CAD flatness is not printed-surface qualification.

The PETG body/lid retain R4.5 plan corners and 1.2 mm bed-edge chamfers. Nut-slot
roofs span the 5.8 mm slot width. Prior automatic supports were external near
these ports; the primary slice had none. Inspect/clean the accessible slots
before assembly and keep loose fragments out of the chamber.

## Verification and physical status

[Selected slice receipt](notes/selected_final.json): matching STEP/STL exports,
OrcaSlicer **2.4.2**, Q2C 0.4 mm, supplied TPU triplet, centered compound placement,
0.2 mm layers, two walls, 100% rectilinear fill, no brim, primary supports off.
The slice completes without keyword notices. The automatic probe proposes support
inside shallow cores; its native status remains `review_required`.

[Headless path inspection](renders/selected_path_review.png) checks all six
structured floor/pad first-roof layers: paths cross the webs, not along channels.
Eighteen local material-path witnesses on H/I cup floors, roof-pad cores and
side cores have no uncovered width at the selected positions. This shows the slicer retained thin webs at those
witnesses; it does not establish their printed thickness, modulus or damping.
[review_selected_paths.py](review_selected_paths.py) and its
[native-path-derived receipt](notes/selected_path_review.json) record the local scope.

The shared product verification CLI exposes A–I and I30/I24/I20 explicitly.
The thin variants have independent CAD checks and no inherited physical approval.
Receipts for [A](notes/selected_verification_A.json), [E](notes/selected_verification_E.json),
[H](notes/selected_verification_H.json) and [I](notes/selected_verification_I.json)
report CAD PASS for fit, closure, six flat skins, channels, labels and declared
selection. The source-associated analytical screen is separately labeled. A fresh
[focused analytical receipt](notes/selected_compliance_I.json) includes the final
source-boundary chord refinement check; its omitted CAD checks remain UNKNOWN
there and are covered by the full receipts above.
These historical receipts predate the feedback below. Detailed physical handling
and print quality remain UNKNOWN; subjective quietness has user evidence;
`unresolved_evidence` is expected. Original A–F receipts remain historical R1 evidence.

Negative CAD controls reject missing floor/ceiling skins, filled channels, a shifted
cup, a lid on the wrong screw diagonal and an unknown variant. The screw witness
traverses the complete body/lid joint. The common CLI conformance suite passes
87 tests. The beam assembly reproduces the exact axial straight-bar solution;
its mesh/discretization refinement is numerical evidence only.

Reproduce from the repository root, without a runtime deadline:

```sh
./evaluate_model.py model/tpu_damping_box/liners_selected.py --views none --slice --slice-keep-run --slice-printer .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json --slice-process model/tpu_damping_box/profiles/tpu-selected-process.json --slice-filament model/tpu_damping_box/profiles/tpu95a.json --report model/tpu_damping_box/notes/selected_final.json
./execute.py model/tpu_damping_box/review_selected_paths.py
./execute.py model/tpu_damping_box/compliance_screen.py
./execute.py model/tpu_damping_box/verification.py --variant I
./execute.py model/tpu_damping_box/check_witnesses.py
```

The [selected half-section scene](selected_inspection.py) is inspection-only;
do not print it. The exported STEP/STL pair shares units, selected geometry,
orientation and component positions. STL slicing does not verify Orca GUI STEP import.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | Yes — A/E/H/I and shell reported 2026-10-16 | `tpu_damping_box.step/.stl`; `liners_selected.step/.stl`, named designs at `41e1e04`; exact printed files unknown | PLA shell. I approved, much quieter than E/H; E/H damp somewhat; A noisy. Detailed settings, fit and damage unknown. |
| New thin test piece(s) | Unknown | `liners_thin.step/.stl` | I30/I24/I20 are new experiments; quietness and printed integrity unreported. |
| Final printable object(s) | N/A | None — research samples only | I approved in this trial; no final application qualified. |

## Shake experiment and feedback

Use the same loose nut, shell, fasteners and grip for every trial. First shake
empty to distinguish fixture/liner rattles from nut impact. Compare A/E/H/I in a
shuffled order and then reverse it. Shake X, Y and Z separately for roughly ten
similar strokes, then tumble freely. Keep stroke/cadence similar; X/Y addresses
side faces, Z the floor/pad, and tumbling includes corners. Recheck the perceived
winner against A and E without looking at its letter if practical. Fixed microphone
position/gain helps recording; automatic phone gain does not give calibrated dB.

Report the letter/axis, quieter/same/louder than A, sound character (sharp tick,
dull thud, squeak, empty-box rattle), liner-swap effort and any skin damage or
bulging. Repeat gentle and firmer shaking: soft structures may bottom out or
change behavior with amplitude. A loose screw or torn skin is a failure to record,
not a quietness result.

### User print feedback — 2026-10-16

| ID | User observation | Decision |
| --- | --- | --- |
| A | Still makes a lot of sound | Retain historical solid control. |
| E | Some damping effect | Retain reference. |
| H | Some damping effect | Retain reference. |
| I | Much more damping than the others; explicitly approved | Preserve 4 mm design; make three much thinner derivatives. |

Associated repository design: `41e1e04`, focused A/E/H/I set. The user identified
letters, not artifact hashes. The box was printed in PLA instead of PETG. Liner
material is understood as TPU; hardness, brand, actual printer/profile,
orientation, test nut, shake protocol, decibels, skin integrity and wear are
unknown. Supplied TPU 95A profiles are planning assumptions, not actual settings.
This is a subjective physical comparison, not material calibration.

The new instruction approves I and authorizes three substantially thinner
derivatives. No reprint of A/E/H/I is needed. Reduced stroke and changed cavity
size can alter sound; thinner variants have no physical approval yet.
Results do not automatically transfer to heavier contents, another TPU hardness,
impact speed or larger box.

## Historical batch

The initial [A–F STEP](liners_batch.step), [STL](liners_batch.stl),
[source](liners_batch.py), [core diagram](renders/core_sections.png) and
[slice report](notes/tpu_final.json) are retained as historical exports; the exact
plate the user printed is unknown. They are not the
recommended current batch. A/E geometry is reused unchanged; G is a screened
thin-inclined source concept with no agreed standalone printable export. Initial
research also included [Chapa et al.](https://doi.org/10.1155/amse/1234886), whose
impact-force and absorbed-energy rankings differ across TPU honeycomb topologies.
The present selection prioritizes light-impact compliance, not those large-impact rankings.

## User intent

Source: the user's 2026-10-15 request and clarifications. Build a small closable
PETG box for a loose stock nut, with separately printed, interchangeable,
permanently labeled TPU liners; explicit CAD damping structures on all six faces;
batch printing. The user then specified **flat object-contact faces with structures
inside the liner**, and research on effective damping structures.

Latest directive: **maximize quietness while keeping the liner thin**, retain
solid control A, and supply a focused STEP print set favoring stronger candidates
rather than printing every concept. That request authorized additional
promising suggestions and implementation, with no measured acoustic target.
The 2026-10-16 report subsequently approves I and requests two or
three (preferably three) much thinner I derivatives. The original solid control
remains available and need not be reprinted. Dimensions, shortlisted IDs,
webs/skins and manufacturing settings remain agent decisions. This separate
research does not resume the
stopped swatch-box TPU project.

## Attribution

Initial and focused revisions: primary model GPT-6.1, reasoning effort medium,
**as supplied by the user**; exact runtime model identifier and configured effort
are not independently exposed. Harness: Codex shared-workspace CLI/API agent,
GPT-6 family; provider OpenAI. No subagents. Independently authored CadQuery
geometry, linear frame screen and core diagrams; cited research informs hypotheses,
not physical qualification. Orca/Qidi JSON profiles have separate
[AGPL-3.0 attribution](profiles/ATTRIBUTION.md). No published specimen meshes or
figures were copied. Research/model dates: 2026-10-15 (baseline), 2026-10-16
(thin derivatives and user feedback).
Thin revision: same user-supplied model/effort attribution; runtime identifier not exposed.
