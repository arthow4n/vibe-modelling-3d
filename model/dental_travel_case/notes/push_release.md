# Push-to-release alternatives

The user has selected **B for a physical mechanism trial**. Print the [new three-piece B1 sample](slider_b.md) to understand and test the operation; the full case has not been redesigned. The printed PLA C2 sample was too tight both to open and to close, so unchanged C2 prints remain on hold. The [SVG comparison](../renders/concepts/push_release_options.svg) ([PNG](../renders/concepts/push_release_options.png)) below records the earlier proposal phase; no CAD was changed during that drawing-only phase.

## What the print changes

User report, 2026-10-22: the short `smooth_joint_test` was printed in PLA; the full box was not printed. The user still wants secure retention but now asks for an intentional push to disengage, with alternatives explored before returning to cantilevers. They do not reject cantilevers. They suspect PETG would also be too tight, but PETG operation has not been observed. Exact print settings, force, damage and cycle results are unknown. The file association is the delivered C2 sample at `43a3e1f`; the actual printed file hash was not supplied.

The sample's missing roof/floor limits force transfer, but its rejected operation is enough to stop recommending more of this architecture unchanged. The previous approximate 11 N PETG full-cap estimate never established acceptable user effort. It cannot overrule this observation or be treated as a measured PLA force. Tight guide fit, friction, catch deflection and shell restraint have not been separated experimentally; no microscopic cause is claimed.

The new architectural objective is **a retaining ledge that carries separation load, plus a modest control movement that clears it before withdrawal**. A gentle lead-in or holding the control during closure can reduce insertion effort independently. Guide clearance still matters: releasing a latch will not cure a binding sleeve.

## Concepts and comparison

Colors in the SVG identify body (blue), cap (amber), moving flexure (purple) and sliding yoke (green); they can all be printed in the same material. White is empty space. Dashed outlines show the prior pose; red arrows show user/moving-part motion, not measured forces. Sections and travel are schematic, not dimensioned CAD. All retain an independent seating stop and a visible seam for lifting, with protected controls and no return to the discarded hinged-case family.

| Option | User action and retention | Potential advantage over a cantilever | Cost or uncertainty |
| --- | --- | --- | --- |
| **A: torsion paddle** | Squeeze two body-mounted buttons through protected cap windows, retract both hooks, then lift. Return bars twist; the paddle should remain comparatively rigid. | Can package a short lever without a long bending tongue; torsion-bar stiffness and hook overlap are separate design variables. | Still a flexure. PLA fatigue/creep and printable bar/slot construction are unqualified; not automatically easier or more durable. |
| **B: sliding locking yoke** | Push a captive U-shaped yoke sideways until two exit windows align with body lugs, then lift the cap. Hold unlocked to seat, then slide back to lock. | The main retaining ledges move rigidly, avoiding repeated bending of a structural latch. Best separation of holding load from elastic release effort. | Three pieces rather than two; sliding tolerance, contamination, accidental sliding and remembering to relock. A light position detent may itself use a small flexure, but does not carry the cap's separation load. |
| **C: squeeze-to-expand rim** | Compress the rim's narrow ends so its broad sides move outward and clear body lugs. Lift while squeezed; also squeeze when closing. | Potentially two pieces and a smooth exterior, with bending distributed around a curved band instead of an isolated tongue root. | Lowest confidence: the roof, guides and attachments can prevent the desired expansion. Bag squeezing may reproduce the release action. It requires a deliberately compliant rim, not just softer current walls. |

**My preference:** B is the clearest alternative if avoiding PLA spring strain matters more than an extra part and a manual lock step. A is the more promising two-piece push-button direction if a compact integral spring can be printed reliably. C is worth showing, but should be dropped if useful catch clearance needs excessive shell distortion or exposes an easy compression-release route. No option has yet earned a force or durability claim.

A correctly designed push-release cantilever can also separate retaining strength from release effort. Its principal disadvantages here are the required bending length, root strain, guarding and prior weak whole-shell escape routes—not an inherent inability to retain strongly. None of the alternatives is proven superior to that baseline. The existing M1's weak retention is product-specific evidence, not a general verdict on cantilever latches.

## Whole-object checks before choosing CAD

- **A, nominally two printed pieces:** the cap guides on the sleeve, its axial stop meets the sleeve tip, and the body hook's retaining surface sits above the cap lip. Pressing moves that hook inward; both must clear before lifting. Place the retaining load line so upward pull favors engagement rather than rotating the paddle inward. Limit inward overtravel and shield the button windows with the underlying sleeve without blocking button travel. The return bars must be relaxed when seated. Close with the buttons held if the ramp alone still needs excessive force. Future manufacture would retain upright body/inverted cap orientation; short bar spans and their roots/slot roofs need a real printable layout and slice, not an assumed PLA living hinge.
- **B, three printed pieces:** the yoke is attached to the cap, its ledges lie below body lug shoulders, and cap rails transfer that axial load. Slider motion aligns bottom-open exit slots, letting the lugs move downward relative to the lifted cap. One U-shaped piece connects the two sides around one narrow end, leaving the contents passage open. Rails, end stops and a guarded LOCK/UNLOCK control keep it captive; a detent resists unintended lateral movement but is not a structural catch. Exact rail assembly/capture must be resolved before detailed CAD. Print the yoke separately on a broad face so its load-bearing ledges are supported; body/cap orientation and any rail overhangs require review. No automatic return spring is hidden in this proposal: manually return the slider to LOCK after seating, with a visible position cue.
- **C, potentially two printed pieces:** the release ring belongs to the cap and its broad-face receiver lips sit below body lugs. Squeezing the narrow ends expands the receiver spacing. Relocate catches to those broad faces and reserve clearance between body guides and inward-moving rim ends; simply adding squeeze marks to C2 cannot work. Keep the axial seating stop on a stiff shoulder so it does not preload or immobilize the ring. Roof connections should attach at suitable ring nodes while leaving a compliant band and travel gaps. This competes with smoothness, protection and reliable guidance. An extra loose ring would raise the part count to three and weaken its simplicity advantage. Integral bands/connecting bridges need a supportable print path; there is no qualified layout yet.

For all: open upright with the lower body supported, release first and lift second. Buttons or the slider must be reachable without squeezing the stored tube or projecting into its loading passage. Controls need enough guarding to distinguish deliberate operation from bag contact, without recreating large exterior bumps. The old 30 mm overlap is historical geometry, not a fixed requirement for the replacement; choose enough guide length to prevent peel/binding, rather than assuming more overlap is always better. Do not carry the old force checks to a new latch architecture.

A twist/bayonet cap was considered but not selected: this rectangular sleeve cannot freely rotate through a useful locking angle without extra envelope or a separate rotating collar. Magnetic attraction alone would not provide the requested deliberate release action. These are not additional recommended variants.

## Research boundary

[Covestro's Snap-Fit Joints design guide](https://www.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1556891135.pdf?hash=7876F8D5E2C7244C33BEAA0DDC6C20F6&rev=2375d9db07bd48b19949b705c884423b), pp. 4–6 and 18–19, distinguishes flexural cantilevers from torsion-bar rockers and discusses deliberate press release. It supports A's mechanism family and the fact that a cantilever can also have a useful release action. The guide concerns plastic design, principally molded examples; it does not qualify these printed PLA bars, this shell geometry or cycle life. B and C are object-specific schematic proposals, not source-validated products. No numerical dimensions or printed-material allowables were imported from that guide.

## Verification, limits and attribution

This phase checks drawing readability, mechanism direction and the local document links. No model source or STEP/STL was edited. No new physical validation, CAD interference, strength, manufacturing or slicer result is claimed. Existing C2 digital evidence remains historical and scoped to its old geometry, while its printed operation is rejected for effort.

| Item | Print status | Artifacts | Result / remaining observation |
| --- | --- | --- | --- |
| C2 trial | Yes | `smooth_joint_test.step` / `.stl` | PLA, too tight opening and closing; no measured force. |
| Release concepts | N/A | SVG / PNG only | B now selected for the separate B1 physical sample; A/C remain proposals. |
| Full C2 case | No | `short_lap_case_smooth.step` / `.stl` | User has not printed the full case; on hold after sample feedback. |

Primary model: GPT-6 family; exact identifier and reasoning effort not exposed. Harness: Codex coding-agent environment; provider: OpenAI. User supplied the physical feedback; diagrams and comparisons are agent-authored. Historical attribution is preserved in the existing object records.
