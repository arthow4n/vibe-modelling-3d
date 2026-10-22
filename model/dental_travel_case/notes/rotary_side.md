# Compact one-side rotary locks

Review the [three-option SVG](../renders/concepts/rotary_side_options.svg) ([PNG](../renders/concepts/rotary_side_options.png)), [swivel-tab section](../renders/concepts/rotary_side_tab.svg) and [quarter-turn cam explanation](../renders/concepts/rotary_side_cam.svg). **R1 has now been selected for a physical trial:** [R1a sample and instructions](rotary_r1.md), [STEP](../rotary_r1_test.step), [STL](../rotary_r1_test.stl). The proposal comparison below records the preceding SVG phase; R2/R3 remain unbuilt. The bulky B1 yoke and the too-tight C2 pull-apart snap are on hold.

## What the user means and what changed

The user rejects B1's large exterior yoke and proposes a small control that rotates on one side to lock cap and base after they are pushed together. They expect the final sleeve to have enough overlap that one lock may suffice, while acknowledging uncertainty about its form. They request several SVG variants before modelling, prioritizing a minimal but useful exterior. Whether B1 was physically printed or operated was not reported; bulk rejection is a product/form decision, not a measured latch failure. The earlier C2 sample was printed in PLA and was too tight opening and closing; those observations remain authoritative.

The drawings interpret “spin from the side” as a **local rotor whose axis is normal to one exterior wall**, not rotation of the entire rectangular cap. The two main alternatives differ in which shell carries that rotor. Both let the guide slide freely when unlocked; neither requires springing a strong snap over its catch.

The complete-case sketches share the old 264 × 75.8 mm visual basis, with one localized control on one broad face near the seam. Enlarged details are schematic, not CAD sections. Blue means body or its integral keeper, amber cap or its integral keeper, green moving rotor, grey axle/fastener, white empty space; colors identify physical roles and do not require multicolor printing. Proposed footprints are approximate starting proportions, not dimensional commitments. Pivot-head thickness, retainers and local boss depth are unresolved; the sketches do not promise a flush control for free.

## Three variants

| Variant | What turns and what holds | Does it pull the halves snug? | Main tradeoff |
| --- | --- | --- | --- |
| **R1: body-mounted swivel tab** | A short tab turns from a parked horizontal pose to upright. Its inward-facing nose sits above an integral cap shelf; cap lift puts the shelf against the nose underside. | **No deliberate draw-down.** The seating stop establishes closure; a small clearance must be taken up before bearing. | Small visual footprint, simple action. Needs a real nose/shelf relationship and a retained axle; a flat strip spanning the seam is insufficient. |
| **R2: cap-mounted slotted cam** | A local disc turns around a body stud. In OPEN the stud exits through a radial mouth; in LOCK the curved slot ends with solid cam material below the stud. | **Potentially yes.** A small final ramp on the bearing edge takes up axial play before reaching a flat dwell and hard stop. | Closest to the requested “turn it snug.” More sensitivity to clearance, cam profile, stud root and pivot stiffness. |
| **R3: side locking screw / pin** | A side thumb screw advances a tip into a blind socket in the sleeve. The tip resists cap withdrawal in bearing; retract it before lifting. | **No.** Sideways screw force is not automatically axial cap clamping. | Familiar and local, but more turns, thread wear, a local thread boss and possible screw loss. Shown as a fallback, not my first choice. |

**My preference:** R1 is the simplest starting point if a positive rotational lock with modest axial play is acceptable. R2 is the better match if the turn should also settle the cap firmly against its existing seat. R3 makes the alternatives concrete but adds fiddling without clearly improving this object's use.

These mechanisms replace the wraparound yoke; they do not merely shrink it. Most exterior surfaces can remain uninterrupted. The controls still need finger purchase and a protected parked/locked position. A broad paddle or large guard would undermine the reason for changing architecture.

## How the keeper relationships work

**R1:** body → axle → tab → inward nose → cap shelf. In the normal section the stem is outside the shelf with clearance; only the nose reaches inward above it. This is what blocks axial lift. The keeper is integral to the cap, not another loose part. The swing needs a clear lateral entry into that relationship, an angular stop and a light position detent. Retaining loads should meet bearing surfaces without creating a torque that swings the tab open. The supplied front view alone is not proof of that; the [nose section](../renders/concepts/rotary_side_tab.svg) names the needed contact. Do not use a large friction preload at the pivot as the only lock-position retention.

**R2:** cap → axle → cam jaw → body stud → sleeve/body. The [detail sheet](../renders/concepts/rotary_side_cam.svg) shows the same fixed stud during a 0 / 45 / 90-degree turn, with the rotor's curved clearance slot moving around it. In OPEN the lower mouth supplies an axial exit path. In LOCK that mouth has rotated sideways and a solid edge blocks withdrawal. The stud is integral to the body. Its final root, radial stand-off and local cap window need design; the section deliberately exaggerates radial depth so the force path is visible. The cam connects around the stud outside that cut plane.

The main rotor drawings show constant-radius capture; the separate unwrapped profile explains a possible small draw-in ramp. **No cam rise, torque or preload has been chosen.** The cam must first remove harmless play and then stop at the independent seating surface, rather than recreate the rejected high-effort wedge. A flat dwell plus a positive angular stop reduces the tendency of axial load to drive it back along a ramp; a detent is still needed to resist incidental rotation. Those details are hypotheses to implement and test, not a claim of shock-proof locking or comfort. Close by seating gently and rotating; open by rotating clear before pulling.

**R3:** cap/thread boss → screw tip → sleeve socket. The tip must engage a real shoulder/socket, not simply press harder against a smooth sleeve. A blind pocket preserves separation from contents but needs enough wall behind it; the cap also needs usable thread length. A printed screw could keep hardware count down, while a stock screw with a printed finger knob is another route. Neither thread usability nor captive retention is resolved. Increasing sideways tightening can jam the guide instead of improving axial seating.

## One side and long overlap

A single lock is **plausible, not validated**. A long, close-fitting sleeve gives separated bearing contacts that guide translation and resist rocking. It can let the lock focus on axial separation. It does not remove shell spreading, far-edge peel, torsion from an off-center pull, keeper bending, stud breakage or accidental rotation. This repository's full M1 report already showed that a small sample with satisfactory local retention could miss whole-shell escape. Do not transfer either its weakness or C2's calculated force to a new rotary architecture.

Start with a lock near the center of one broad face, rather than at a corner, to avoid adding a sideways offset on that face. The opposite wall still sits across the case depth and can lift first if the shell spreads. Exact face choice, guide overlap and wall stiffness remain open. Keep the former approximate 30 mm overlap as a starting geometry, not proof that one side is sufficient or a reason to lengthen the sleeve indefinitely. A local axle or keeper boss may be necessary; it should not turn into another continuous exterior band or a bulky interior cage.

After choosing a concept, a small trial would need the retained guide perimeter and overlap as well as the actual one-sided keeper and pivot. A bare rotating tab alone would only demonstrate rotation. A future complete-case check must still address the opposite edge, ordinary opening/closing, loaded packing and accidental contact with the control. That was the boundary of the SVG phase. The subsequently authorized [R1a trial](rotary_r1.md) retains the full perimeter and overlap; it does not qualify the complete case.

## Parts, manufacture and research limits

R1 and R2 need **body + cap + rotor + a pivot/retainer arrangement**. The drawings do not hide the axle as a cost-free attachment. A separate printed pin/retainer adds at least one piece; a stock M3 screw and nut are an alternative using the user's recorded hardware. The subsequent R1a sample uses one M3×12 screw and two jammed M3 nuts to retain a freely turning tab; the earlier proposal left that detail open. Small-head hardware may still project farther than the green rotor alone. R3 needs body + cap + screw/knob, plus whatever captive feature proves worthwhile; screw retention cannot be assumed just because some thread remains engaged in OPEN.

For the usual 0.4 mm nozzle / 0.2 mm layers, a future tab or cam would preferably print broad face down, keeping its load-bearing profile in the bed plane. Axle holes, local body/cap keeper undersides, retaining hardware pockets and any unsupported slot roof must be planned with their own orientations. The shell can retain its established longitudinal layer direction where feasible. No toolpath generation, numerical analysis, material allowable or printability result accompanies these sketches.

[Southco's quarter-turn compression-latch description](https://southco.com/en_us_int/latches/compression-latches/emvise-actionemreg-latchesp/e9-quarter-turn-compression-latches) provides a primary example of combining rotation with drawing a cam tight. It supports the distinction between capture and compression, not the dimensions or performance of our proposed external slotted cam. Its commercial metal construction and published stroke/load information are not transferred to printed PLA/PETG. R1/R3 and the chosen schematic mechanisms here are object-specific engineering proposals.

## Verification, status and attribution

SVG XML, rotation directions, the named bearing contacts, readable previews and local links were reviewed. During the SVG phase, existing CAD source and STEP/STL files remained unchanged. The later R1a sample is separate; its evidence is recorded in [the sample notes](rotary_r1.md). Existing digital checks describe the old geometries and do not override product rejection. There is no force, wear, sealing, accidental-opening or manufacturing qualification for these rotary proposals.

| Item | Print status | Artifacts | Result / remaining question |
| --- | --- | --- | --- |
| R1a sample | Unknown | `rotary_r1_test.step` / `.stl` | Selected for PLA action trial; physical results pending. |
| R2/R3 proposals | N/A | SVGs and PNG previews | Alternatives remain unbuilt. |
| B1 yoke sample | Unknown | Existing `slider_b_test.step` / `.stl`, unchanged | Exterior bulk rejected; print/use not reported; unchanged repeat prints on hold. |
| C2 joint sample | Yes | Existing `smooth_joint_test.step` / `.stl`, unchanged | Printed PLA; opening and closing too tight. |
| Full rotary case | N/A | None | No CAD or printable replacement this phase. |

Primary model: GPT-6 family; exact identifier and reasoning effort not exposed. Harness: Codex coding-agent environment. Provider: OpenAI. User supplied the form rejection and requested direction; SVGs and comparisons are agent-authored. Prior source and physical attribution remains in the existing object records.
