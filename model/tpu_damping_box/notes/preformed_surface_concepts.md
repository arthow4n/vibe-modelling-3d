# More surface ideas — preformed liners beyond B/S

[Object status](../README.md) · [Overview SVG](../renders/concepts/preformed_overview.svg) ·
[N1: slicer infill](../renders/concepts/preformed_infill.svg) ·
[N2: curved web](../renders/concepts/preformed_curved_web.svg) ·
[N3: preformed trough halves](../renders/concepts/preformed_troughs.svg) ·
[Actual N1 paths/configurations](infill_study/README.md)

**Latest route:** the user favors ties and asks for direct B-skin/curve path
research. The [completed adaptive wall study](tie_surface_study/README.md)
recommends T12/T16 straight-tie skins ahead of the tested smooth roots, based on
actual routes. Its N2 R0.25 blend is examined, not promoted. Gyroid remains a
separate candidate; none of this establishes physical finish or damping.
The comparison below preserves the earlier N1–N3 phase and its reasoning.

The user requests further ideas after setting aside separate thin cups and
rejecting folding. These three proposals change core generation, attachment
geometry or print orientation. They are **discussion concepts**, not new models,
full-box print instructions or claims of smoother prints. The subsequent user
authorization adds a [slice-only infill proxy and three actual path comparisons](infill_study/README.md). B08/B16 and S16 remain the
physical references. The [printed comparison and retained path review](b_surface_concepts.md)
own the evidence: B has better reported contact finish than S16, but visible
patterns, occasional bumps, stringing and seam artifacts remain unexplained.

| Concept | What changes | Printing and complete liner count | Main tradeoff |
| --- | --- | --- | --- |
| N1: slicer-generated sparse core | A volumetric wall gets ordinary gyroid infill instead of CAD dots, with substantial perimeter skins. | One cup upright + one flat lid pad = two total. | Needs a prepared sparse-infill/corner project; core can still mark the face. |
| N2: continuous curved web | A longer bending web meets each skin tangentially, replacing abrupt post/rib junctions. | One cup upright + one flat lid pad = two total. | Deeper core and thicker skins may reduce damping; continuous geometry is not one nozzle path. |
| N3: preformed trough halves | Split the cup longitudinally, putting its largest opposed walls horizontal on the bed. | Two preformed cup halves on their backs + one flat pad = three total. | Join lines on two narrow faces and the floor; remaining short walls still print upright. |

All meet the user's count of up to two cup pieces **plus** the usual pad. None
uses folding, loose core inserts, eight separate tiles or an independently
printed thin inner cup. N1/N2 still have upright walls: substantial multi-path
skins and attached core distinguish them from P1, but do not establish tall-print
reliability. Thickness is unconstrained; preserving usable contents space still
matters. No automatic transfer to the tall dental liner is implied.

## N1 — let ordinary infill make the core

The requested [actual slices](infill_study/README.md) compare **G20 (Gyroid 20%),
G30 (Gyroid 30%) and X20 (Cross Hatch 20%)** on one 6 mm-thick straight-wall proxy.
[Consecutive-layer SVG](../renders/concepts/infill_study_paths.svg) ·
[Full-wall SVG](../renders/concepts/infill_study_full.svg) ·
[Roof SVG](../renders/concepts/infill_study_roofs.svg). G20 is the leading infill
candidate; the study confirms sparse core and three wall contours, not finish.

Model a sufficiently deep **solid CAD wall volume**, then use Classic perimeters
and sparse gyroid to create its internal air space. The printed result is not
solid C. The core's dimensions must leave room between the inner and outer
perimeter skins; the existing 1.6 mm sandwich is not a suitable assumed envelope.
An illustrative starting range is 1.2–1.5 mm skins and 3–5 mm of core, with actual
path counts and cell spacing selected in a later slice. These are not qualified
sizes or calibrated stiffnesses.

The potential benefit is replacing many short dot-boundary events with normal
infill runs, while giving the visible face multiple perimeter paths. Gyroid is
not a single continuous toolpath: clipping, anchoring and part geometry still
create separate runs. Prusa's [infill documentation](https://help.prusa3d.com/article/infill-patterns_177130)
describes its non-crossing paths within a layer. That property motivates the
choice; it proves neither less TPU stringing nor better finish than B.

The cup prints bottom first, mouth up. Wall infill grows from the base. The
floor's top skin and the flat pad's top skin bridge between infill supports;
density must be chosen from actual clear spans, not just a low percentage.
There is no roof across the cup mouth. All TPU flexes together: contents →
perimeter skin → bending infill → outer skin → rigid box.

**Setup consequence:** the retained process has 100% infill and two wall loops.
It cannot be reused unchanged. N1 would require a supplied ordinary sparse-infill
preset and model-specific **100% corner regions** in a prepared project, with
no extra printed parts. Solid CAD corner mass alone still gets sparse infill;
rounded corners alone do not satisfy the user's solid-corner intent. This
project dependency is a real cost relative to N2's modelled voids, not hidden
manual setup or a claim that an STL automatically encodes infill.

The primary risk is the same physical coupling: infill still meets and can push
or thermally mark the skin. Dense cells or thick skins may also lose B's useful
damping. This is the simplest core CAD, not necessarily the simplest print setup
or a guaranteed surface isolation mechanism.

## N2 — curved web with gentle, tangent attachments

Keep both continuous skins and replace isolated ties/straight ribs with a
sinuous web. In a horizontal wall cut, its crests merge into the two skins along
a tangent, with finite overlap and rounded transitions rather than point contact
or a sharp T. Longer curved segments are intended to bend into the air space.
The drawing pairs before/load sections; their motion is qualitative, not a
simulation. Rough discussion sizes are 1.2–1.5 mm skins, a roughly 1 mm web and
a deeper core. Do not make microscopic tangent contacts that vanish in Classic.

Print the cup upright. Its wall section repeats through height, so the web is
supported by its own previous layer and there are no B-style tie rows turning
on/off. Keep wall channels open at the rim and let the separate pad cover them
in use. The integral floor and separate pad use a short-span closed core starting
from printed B practice; **do not turn the wide wavy wall channel sideways and
print an unsupported roof across it**. Floor/core transitions still need CAD
and slice review. Solid corner lands taper into the curved section.

This is a different web load path and junction shape, not fewer dots. However,
S already had continuous ribs and its finish was worse than B's. Constant Z
geometry alone is therefore not a persuasive new answer. Rounded tangential
joins plus robust skins are the actual hypotheses. Internal channel contours,
gap fill and seams still exist; the model cannot dictate one uninterrupted
nozzle run. Thick skins and broad joins may make this too stiff or leave their
own repeated marks. N2 is the most speculative of the three surface proposals.

## N3 — two preformed half-troughs printed on their backs

Split the liner down its long axis into two **side-by-side** halves. Each part
contains one large wall, half of each adjacent narrow wall and half the closed
floor. It is already a trough when printed. Lay the large wall's outer backing
on the bed; its object-facing skin becomes a horizontal **top surface**, not a
bed-contact surface. Two short side returns and the integral floor-half grow
from that backed panel. The cup-mouth end stays open. The SVG shows the assembled
cross section, one part's print cross section and the long axis along the bed.

Build order is backing skin → small-cell supported core → contact skin, with
return walls growing at the perimeter. Only the small core roofs bridge; no
bridge spans the open trough. Use substantial skins and a modelled short-span
core derived from the B floor/pad principle, not a thin unsupported shell.
A representative slice must check the new orientation, core roof, return-wall
roots and end-wall transitions; old B approval does not qualify them.

Drop the two halves into the existing rigid box and seat the usual pad. Plain
butt joins on the narrow faces and through the floor avoid additional snap lips,
clips, hinges or glue. Solid seam lands and corner lands provide substantial
edges; fit to the rigid box and pad capture must keep the joins flush. The drawing
shows the intended restraint, not a verified interference or retention fit.
Reject this architecture if the halves drift or the joins catch contents.

Its manufacturing difference is substantial for a long narrow liner: most
contact area prints horizontally, and build height is roughly half the cup's
cross-sectional width rather than its full length. The returns still print
upright and are not promised smooth. Core-supported horizontal top skins can
still show bridging, fill and cooling defects; prior flat-surface ironing did
not fully fix S. N3 provides a different controllable surface orientation,
not an assurance that top fill will beat B.

Unlike the rejected folding net, it requires no corner flaps or bend allowances.
Unlike P1's nested cups, both halves are core-backed. It still needs a usable
split for each target shape, sufficient bed length, and a check for ledges or
undercuts. Complex pockets may rule it out; do not force it onto every model.
There are two narrow-face joins plus a floor join, so the smooth-face benefit
is purchased with visible/tactile seams elsewhere.

## Print-path refinements that can accompany a selected design

These are supporting ideas, not substitutes for the architectures. Orca's
[wall-order documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_wall_and_surfaces/644ec80f411f679697a02a98b6efae836beb2ad8)
explains that infill-first can push walls outward and that Inner/Outer/Inner
requires at least three wall paths. A “three walls” setting cannot create that
sequence in an existing one-bead skin; design enough material and verify the
actual paths. This is a reason to investigate multi-path surfaces, not proof
that wall order caused the user's marks.

The existing process already has 15% infill/wall overlap. Orca's
[overlap guidance](https://github.com/OrcaSlicer/OrcaSlicer/wiki/strength_settings_infill/a3d775e1b6d760a4f35188c8e4fbe51faabd80d2)
connects overlap to bonding and possible excess-material roughness. Do not
recommend reducing it indiscriminately or claim that the default has not
already addressed it. In B's CAD webs much of the junction work is perimeters,
not sparse infill, so that setting is not a general cure for B's geometry.

Put seam starts in an accessible solid corner zone where possible, preserving
its smooth corner turn and avoiding fresh ledges or thin notches. A painted seam
can move a seam artifact; it does not remove core patterns. Wipe was already on
in the retained B setup. Moisture, pressure response and exact user seam/travel
behavior remain unmeasured, so no new universal TPU process calibration is made.

## Earlier N1–N3 recommendation and evidence status

N3 is the clearest change to manufacturing if the two narrow-face joins are
acceptable; N1 is the useful one-piece-cup alternative, with its prepared-project
cost explicit. N2 is worth discussing as a curved bending core but is a weaker
finish hypothesis. This is an agent ranking, not user selection. All retain both
skins, solid corner intent, black TPU, ordinary Classic, nominal 0.4 mm nozzle
and 0.2 mm layers. No Arachne or custom G-code is assumed.

SVG/XML, raster readability, local links and construction reasoning were
checked for N1–N3. The user then authorizes infill configurations and requires
actual sliced paths: the linked N1 wall proxy has valid CAD/paired exports and
three completed diagnostic slices with no notices or proposed supports. New
study profiles are separate from unchanged B/S settings. No physical print or
damping measurement exists. If a direction advances, verify its identified wall/roof
paths and representative finish/damping before extending it to the tall liner.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| N1 diagnostic proxy | No | [Source/STEP/STL and three diagnostic slices](infill_study/README.md) | Slice explanation only; no reported print, finish/strength/damping unknown. |
| N2/N3 test pieces | N/A | Discussion SVGs only | No CAD or physical specimens. |
| Final printable objects, N1–N3 | N/A | None | No print-ready objects in this concept phase. |

Attribution, 2026-10-21: primary model GPT-6 family; exact runtime identifier and
reasoning effort not exposed. Codex shared-workspace CLI/API agent, OpenAI;
no subagents. User supplies requirements and print feedback; agent authors the
new architecture interpretations and SVGs. Primary slicer documentation informs
path hypotheses, not TPU performance qualification.
