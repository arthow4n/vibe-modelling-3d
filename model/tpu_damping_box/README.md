# Flat-faced TPU damping box experiment

**I is approved by the user (2026-10-16).** In the tested **PLA** enclosure,
E, H and I all damped sound, but I was clearly best; solid A remained noisy.
The approved 4 mm I source and exports are preserved. This does not establish
equal acoustic performance with a PETG shell.

The next experiment is three much thinner I-derived cup/pad pairs for the same
shell. Keep the printed I as the reference. Thin variants are untested.

![Focused core sections](renders/selected_core_sections.png)

## Thinner I experiment

**Current batch: I30 / I22 / I10**, one cup and matching pad per ID.
[Primary STEP](liners_thin.step) · [matching STL](liners_thin.stl) ·
[entry point](liners_thin.py) · [builders](thin_design.py).
Reuse the PLA shell, screws and printed original I. All six contact faces remain
flat. **I10 replaces unprinted I26** to give a much larger experimental jump.
I30 and I22 retain their geometry; I24/I20 and I26 are absent from this plate.

| ID | Total lining | Reduction vs approved I | Backing / gap or core / contact skin | Support width | Clear cavity |
| --- | --- | --- | --- | --- | --- |
| Original I, approved | 4.0 mm | Reference | 0.8 / 2.6 / 0.6 mm | 0.6 mm chevrons | 26 mm cube |
| I30, retained | 3.0 mm | 25% | 0.6 / 1.8 / 0.6 mm | 0.5 mm chevrons | 28 mm cube |
| I22, retained | 2.2 mm | 45% | 0.6 / 1.0 / 0.6 mm | 0.9 mm chevrons | 29.6 mm cube |
| I10, extreme limit | **1.0 mm** | **75%** | **0 / 0.4 / 0.6 mm** | **1.2 mm straight stand-offs** | 32 mm cube |

I10 is about **55% thinner than I22**. This is an aggressive nominal design
limit for this chosen nozzle/layer setup, not the thinnest physically possible
liner or a claim of useful damping. A 0.6 mm skin over only 0.4 mm air space may
bottom out early, bridge sag can consume that space, and its straight supports
have much shorter load paths than approved I. It is a different architecture,
not a scaled chevron. The experiment asks whether useful quieting survives.
No numerical acoustic/compliance ranking is assigned.

### I10 architecture and assembly

The shell itself backs the ribs, removing the liner's continuous outer skin.
Its object-contact membrane remains flat and continuous on floor, ceiling and
four walls; 3.6 mm-pitch ribs face outward toward the shell. **1.2 mm rib widths
and bed frames** allow margin for the profile's 0.15 mm per-edge first-layer
compensation; the 0.4 mm dimension is air-space/rib height, not a free-standing
0.4 mm-wide wall. Corners, frames and supporting ribs remain direct TPU load paths.

A 0.6 mm upper locating rim retains the common pad pocket. All cups retain the
34 × 34 × 34 mm envelope and 0.2 mm per-side shell allowance. All pads are
32.4 mm square with 0.2 mm per-side cup-pocket allowance. I30/I22 keep their
0.2 mm axial preload. **I10 uses zero deliberate preload** so it does not spend
half its shallow gap on nominal compression; its pad prints **1.0 mm thick**.
I30/I22 pads print 3.2/2.4 mm thick. Actual clamping, rattle and fit remain untested.

Both I10 parts retain a **12 mm bold recessed I10 label** on a solid **24 × 12 mm
panel** near an exterior edge (label centre Y +9 mm in print pose), rather than
hiding letters behind open ribs. The recess is 0.2 mm deep. The local panel fills
the gap there, giving a stiffer patch; it does not protrude into the object space.
This deliberately trades some local compliance for durable, readable labeling.
I30/I22 labels retain their previous placement and typography.

Use the same nut, shell, TPU and grip; shake empty first to detect liner rattle.
Compare gentle and firmer X/Y/Z shaking and tumbling, interleaving original I.
The cavity grows as lining shrinks: increased travel is a confound, not an
isolated material comparison. Note sharp ticks, bottoming, skin damage, axis,
label-side versus other impacts, and whether I10 offers any useful quieting.

### Manufacturing and verification

Use the same TPU as approved I; reference setup assumes TPU 95A, Q2C 0.4 mm nozzle,
0.2 mm layers and [tpu-selected-process.json](profiles/tpu-selected-process.json):
Arachne, two requested walls, solid fill in CAD material, supports off, explicit
**180° external/internal bridge direction**, and no component rotation.
Print backing/rib feet down, cups open up and pads contact-skin up. Layout remains
118 × 74.2 mm, 34 mm tall, with stable perimeter-frame/rib bed contact on I10.
I10's contact skin is three layers and its air gap is two layers. Floor/pad roof
spans between straight ribs are 2.4 mm (outermost gaps up to 2.6 mm), with a bed
frame supporting outer edges;
the label panel supplies its own support. The I10 upper rim adds a 0.4 mm outward
ledge over the wall skin between ribs. Review its actual paths and support probe;
physical finish and membrane integrity remain unqualified.

[Native final receipt](notes/thin_final.json) associates the published geometry,
paired STEP/STL, settings and Orca 2.4.2 smoke slice. The STL review does not
qualify GUI STEP import. Supports proposed inside shallow gaps cannot be removed;
primary supports remain off and the native review status remains visible.
The current slice completes with no keyword notices. Its support probe proposes
**no support on either I10 part**; proposals remain in I30/I22 shallow cores.
Estimated batch: **28.88 g / 5 h 5 min 45 s**, not measured.

Current CAD receipts: [I30](notes/limit_verification_I30.json),
[I22](notes/limit_verification_I22.json), [I10](notes/limit_verification_I10.json):
fit/insertion, six flat skins, core air/material, labels and selection dimensions.
[Path review](notes/thin_path_review.json), [bridge/support preview](renders/thin_path_review.png)
and [label paths](renders/thin_label_paths.png) cover the actual new batch.
I10 floor/pad stand-offs require multiple substantial paths; its side check spans
the complete skin-plus-rib section, since the shallow stub joins the continuous
skin. These are different sections from I22's separate folded webs. Neither
path coverage nor multiple paths establishes deposited strength or quietness.
The final review covers **six first-skin layers**, **52 local web material
witnesses**, and **26 multi-path sections** (18 I22, eight I10). I10 retains two
paths about 0.50 mm wide at the first rib layer, three paths about 0.42–0.45 mm
at the second, and two about 0.52–0.56 mm across each sampled side rib-plus-skin.
The final CAD and common CLI checks pass; the CLI conformance suite has 87 passes.

Earlier I26 receipts remain historical: it is replaced for experiment spacing,
not a failed print. The original I's approval stays scoped to its reported PLA
trial in [the feedback receipt](notes/reported_I.json). All three thin pairs are
unprinted and have no physical approval.

Reproduce from the repository root:

```sh
./evaluate_model.py model/tpu_damping_box/liners_thin.py --views none --slice --slice-keep-run --slice-printer .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json --slice-process model/tpu_damping_box/profiles/tpu-selected-process.json --slice-filament model/tpu_damping_box/profiles/tpu95a.json --report model/tpu_damping_box/notes/thin_final.json
./execute.py model/tpu_damping_box/review_thin_paths.py
./execute.py model/tpu_damping_box/verification.py --variant I10
```

### I26 replacement request — 2026-10-16

The user has not printed I26 and sees little value in its intermediate thickness.
They request a much larger downward step beyond I22 while retaining I30 and I22.
This is a change in experimental priorities, not a physical rejection. The user
specifies no numerical minimum or guaranteed damping target; 1.0 mm and the open
rib architecture are engineering choices. CAD plus actual sliced sections are the
appropriate evidence for manufacturing; a material-calibrated impact/acoustic
model is unavailable, so quietness remains a physical experiment.

### Thin-feature rejection and prevention

After inspecting the batch before printing, the user rejected **I24/I20 at
`5efd0e2`** because their lines were too thin for the intended normal 0.4 mm
nozzle workflow. No failed print was reported. I30 seemed printable to the user;
that is a provisional assessment, not physical qualification. The user clarified
that **thin means total liner depth, not necessarily thinner webs** and requested
replacement models committed/pushed before this retrospective.

The corrected models were committed and pushed first as **`0723297`**. I26/I22
retain three-layer skins/backings and 0.9 mm webs while reducing total depth by
35%/45%; I30 is unchanged. Larger labels are retained. Quietness is still unknown.
The slightly thicker envelopes preserve more core space than the retired pair.

The earlier CAD checks established geometry and the earlier path review found
material at selected loci. Neither established adequate manufacturing margin:
**one retained extrusion path can pass a presence witness while remaining a
marginal design choice for this user**. The prior review failed to distinguish
those conclusions. No evidence shows that every 0.4 mm feature is universally
unprintable; this is a rejection of the delivered design/setup choice.

Prevention now lives in the design skill and its print-planning/user-preference
references: choose the overall envelope and local minimum sections separately;
preserve successful local dimensions where practical; inspect widths, distinct
path count, continuity and supporting layers for critical webs; and avoid claiming
printed robustness from slice completion or path presence. The replacement check
uses an explicit local criterion, at least two 0.38–0.65 mm paths, not a global
printer limit. At R5, the I26/I22 witnesses contained two or three paths, widths 0.381–0.589 mm.
R6 changes the selected architecture and witnesses as described above.

[Regression evidence](notes/web_track_regression.json) uses the retained
[original native slice receipt](notes/retired_thin_r4.json) from `5efd0e2`:
[check_web_tracks.py](check_web_tracks.py) must reject the old single-track I24/I20
floor samples. R5 had 36 successful I26/I22 witnesses; the updated R6 consumer
requires the 26 declared I22/I10 sections. It consumes saved
G-code; its raw-file paths must remain available to reproduce it. The receipt
stores source/G-code identity and local scope. This verifies that the new check
can distinguish the relevant path allocation; it does not measure print success,
TPU properties or quietness. No extra CAD/slice is needed for this retrospective.

## Print files

| Print | Primary STEP | Matching STL | Parametric entry point |
| --- | --- | --- | --- |
| New TPU batch: I30/I22/I10 | [liners_thin.step](liners_thin.step) | [liners_thin.stl](liners_thin.stl) | [liners_thin.py](liners_thin.py) |
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

The shared product verification CLI exposes A–I and I30/I22/I10 explicitly.
The thin variants have independent CAD checks and no inherited physical approval.
Receipts for [A](notes/selected_verification_A.json), [E](notes/selected_verification_E.json),
[H](notes/selected_verification_H.json) and [I](notes/selected_verification_I.json)
report CAD PASS for fit, closure, six flat skins, channels, labels and declared
selection. The source-associated analytical screen is separately labeled. A fresh
[focused analytical receipt](notes/selected_compliance_I.json) includes the final
source-boundary chord refinement check; its omitted CAD checks remain UNKNOWN
there and are covered by the full receipts above.
These historical receipts predate the feedback below. Detailed physical handling
and skin quality remain UNKNOWN; old labels are physically rejected as too small;
subjective quietness has user evidence;
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
| Test piece(s) | Yes — A/E/H/I and shell reported 2026-10-16 | `tpu_damping_box.step/.stl`; `liners_selected.step/.stl`, named designs at `41e1e04`; exact printed files unknown | PLA shell. I approved, much quieter than E/H; E/H damp somewhat; A noisy. Previous labels too small to read. Detailed settings, fit and damage unknown. |
| New thin test piece(s) | No — user reports before printing | `liners_thin.step/.stl` | I30/I22/I10 are new experiments; quietness and printed integrity unreported. |
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

**Additional label feedback, 2026-10-16:** the previous batch's 6 mm font-size
labels were too small to read. The user requests much larger and/or bolder labels
before printing the thin batch. This is a physical labeling failure; I's damping
approval remains valid. New label readability remains untested until printed.

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
(thin derivatives, enlarged labels and user feedback).
Thin revision: same user-supplied model/effort attribution; runtime identifier not exposed.
