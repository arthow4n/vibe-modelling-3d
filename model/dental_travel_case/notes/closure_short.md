# Short retention trials — less material, full cross-section

**Later continuation, 2026-10-19:** the user reopens wall snaps, accepts that
opening noise may be tolerable, and asks to reduce production overlap while
retaining strong closure and sideways stability. The [new full prototype and
comparison](short_lap.md) supersede this phase's stop. The two printed samples'
high effort/noise remain observations; their exact identities remain unknown.
The files below are historical and do not match the new production cap.

## Printed feedback and direction change — 2026-10-19

The user printed **two short test pieces**. Exact R1-S/R2-S/R3-S/R4-S identities,
export hashes, material and print settings were not specified. They report that
engaging these closures takes much more force and opening generally makes a lot
of noise, particularly with longer engagement. No measured force, sound level,
damage, fatigue or exact microscopic cause was supplied. This is authoritative
negative use feedback, not a calibration of the earlier numerical estimates.

The user does not see sufficient benefit and is unlikely to print the remaining
experimental mechanisms. **Stop the R1–R4 / short-wall closure development**;
preserve the sources, exports and numerical evidence as historical experiments.
The user authorizes a new horizontally opening dental case based on the working
sunglasses-case operation, retaining the accepted slim interior basis and
exploring a substantially smaller hinge or an alternative lid connection.
See the [new clamshell exploration](clamshell_exploration.md).

The recommendations below describe the earlier experiment phase; they are no
longer current print recommendations.

These are the current economical alternatives to the tall R1–R4 research test
pieces. The user trusts the long-overlap investigation but wants to try the
retention mechanisms with much less overlap/base material, preserving the full
XY shape so the complete perimeter can deform. They also request a small gap to
pull the halves apart. The previous long specimens and their force-study inputs
remain unchanged; this phase does not adopt a new full box.

[Actual CAD sections, including the grip gaps](closure_research/short_samples.svg) ·
[CAD evidence and volume comparison](closure_short/cad.json) ·
[Earlier long-shell force estimates and limitations](closure_pull.md)

| Short trial | Source | STEP pair — preferred | Matching STL |
| --- | --- | --- | --- |
| R1-S broad-wall snaps | [Python](../shell_broad_short_test.py) | [R1-S](../shell_broad_short_test.step) | [R1-S](../shell_broad_short_test.stl) |
| R2-S end-wall snaps | [Python](../shell_end_short_test.py) | [R2-S](../shell_end_short_test.step) | [R2-S](../shell_end_short_test.stl) |
| R3-S continuous bead | [Python](../perimeter_bead_short_test.py) | [R3-S](../perimeter_bead_short_test.step) | [R3-S](../perimeter_bead_short_test.stl) |
| R4-S shallow sliding frame | [Python](../slide_wall_short_test.py) | [R4-S](../slide_wall_short_test.step) | [R4-S](../slide_wall_short_test.stl) |

[R1-S print layout](../renders/tests/closure_short/shell_broad_short_test_isometric.png) ·
[R4-S print layout](../renders/tests/closure_short/slide_wall_short_test_isometric.png)

Each file contains its matching base and cap, already separated and placed for
printing. Do not mix long and short parts, or caps from different concepts.

## What changed and what stayed representative

R1-S/R2-S/R3-S retain the **77 × 51.2 mm exterior**, rounded rectangular perimeter,
1.6 mm sleeve wall, 2 mm cap wall, .15 mm nominal side clearance, .65 mm bump,
retaining ramps/pockets and runout. At the catches the complete perimeter stays closed;
these are not isolated strips or scaled clips. Local catch/receiver geometry is
identical to the original after axial translation, checked in an actual 6 mm
high CAD band surrounding the catches. The roof remains the same distance from
the catches.

The overlap is **24 mm rather than 78 mm**. The open-bottom body is **30 mm tall**,
including only **6 mm below the shoulder**, and the cap is **36 mm tall**. Closed,
the pair is **42 mm tall**, formerly 106 mm. Their combined CAD solid volumes are
about **58% lower for R1/R2** and **56% lower for R3**. These are geometric material
comparisons, not measured filament use or print-time predictions.

The 24 mm dimension is an economical experiment choice: it retains the actual
free tip, complete catch/pocket region, a short recovered runout and a grippable
base. It is not a calculated minimum overlap for the full product. Removing the
base floor saves material while preserving the perimeter; it also changes the
fixture stiffness. The little body should be held by its lower band/underside,
not by pressing inward near the catches.

Two **20 mm wide, 3 mm high recessed grip openings** interrupt the cap rim at the
seam, with .8 mm rounded cut corners. R1/R3 have them on the end walls; R2 has them
on the broad walls, away from its end-wall catches. They expose the body shoulder
and the cap's underside so a fingernail/fingertip edge can gain purchase. The
remaining rim, especially the corners, still provides the original seating stop.
A gap cut around the whole rim would let the cap sink farther and change capture;
the CAD check specifically rejects that overshoot without relying on the hooks.
The gap's geometric access is established; actual comfort and useful pulling
force are unmeasured.

R4-S retains its **77 × 70 mm XY footprint**, original lid, keys, grooves and side
wall detents. Remove the floor/lower walls below native z37: the open-bottom
frame is **12.2 mm tall**, the printed lid **5.2 mm tall**, and the closed pair
**14.2 mm tall**, instead of 51.2 mm. Combined CAD solid volume drops about **65%**.
A centered **20 mm wide recess, 3 mm deep below the lid**, in the front wall
exposes the lid underside for pulling in the slide direction. The rail/detent
region remains identical outside that deliberate grip opening. The 70 mm slide
length stays unchanged to preserve XY and both ends; this is not a full-length
264 mm sliding-friction test.

## What a print can decide

These samples test whether each minimal mechanism seats, gives a useful snap,
returns after passage, rubs/binds, and permits deliberate separation using the
provided grip. Print R1-S and R2-S as the first matched comparison if only trying
two. Keep material and settings the same. Inspect both catches, pull from outside
using the lower band and cap recess, then compare gentle centered and one-sided
separation. The R4-S cap must slide off; lifting primarily loads its rails.
Record absent retention, excessive effort, whitening, cracking, permanent spread,
post-snap rubbing or awkward grip separately. Stop forcing a binding sample.
A click alone does not demonstrate useful holding.

**Keeping XY does not preserve all flexibility.** Shorter axial walls can be
stiffer, open-bottom supports differ, and shorter guidance changes rocking and
peeling. Consequently the earlier R1/R2 newton/gram estimates do **not** apply to
these samples, and a successful short print does not qualify the 78 mm guide or
a later full case. The new verification variant keeps force coverage UNKNOWN.
No new numerical holding force is claimed. The full perimeter and exact local
interface make this a useful inexpensive fit/short-wall experiment, rather than
a mechanically equivalent replacement for the original long-shell fixture.

## Later full-box decisions explicitly retained

The user suggests that, without the old cantilevers, the adopted full case might
also use substantially shorter overlap. **Re-check that hypothesis** after a
mechanism is selected. The previous overlap also carried bending/rocking loads;
removing cantilevers does not remove that guiding duty. Compare useful bearing
separation, clearance, shell stiffness, off-center loads and practical engagement
before choosing production overlap. Do not automatically promote this 24 mm trial
or keep 78 mm solely because it was used before.

The full case must offer **separate usable grips on body and cap**. Consider
shallow inward scallops/recesses within the flat outer silhouette, located where
pulling does not squeeze the active retention walls or consume essential contents
clearance. Check access with the cap seated, opposing pull direction, edge comfort,
wet/slippery handling and accidental release. The sample's seam notches demonstrate
a purchase point; they do not settle the complete box's ergonomics. These are
recorded future design questions, not newly modeled full-case features.

## Manufacturing and evidence

Use the existing PETG, 0.4 mm nozzle / 0.2 mm layer starting setup. The bases print
on their open cut rings, caps inverted on their rounded roof face; the slider
frame stands on its cut ring and its lid prints outside-face down. All paired
layouts fit the established Q2C envelope. Keep the whole pair's supplied placement
when importing. The sleeve/slot slopes and original tooth ramps are preserved.
The grip cuts open toward the final printed rim on inverted caps, avoiding a
new bridge over the opening. No supports should touch retention faces without
inspection. Thin-rim adhesion and actual fit/return remain print-dependent.

The [checks](../closure_short_checks.py) compare actual interface solids, seated
clearance, detent-removal controls, sampled withdrawal/recovered runouts and the
accessible gap. They also verify that cap seating is not lost. The
[publication association](closure_short/publication.json) binds current shared
builders/wrappers to the paired exports and smoke-slice receipts; source changes
invalidate it. The dedicated shared-CLI variant is `research-short-closures`.
Original user intent remains present with untested force/full-product questions
UNKNOWN. The old `research-minimal-closures` variant still describes the long
specimens and their separately scoped evidence.

All four final pairs passed the OrcaSlicer **2.4.2** smoke slice with the existing
diagnostic Q2C PETG / 0.4 mm nozzle / 0.2 mm layers / two walls / 7% adaptive cubic
profile. Each automatic-support probe completed and generated **no support**;
the reports contain no filtered log notices. These establish selected-profile
toolpath acceptance, not printed fit/strength or Orca GUI STEP import. **122
relevant tests passed**, including the separate short-sample verification plan
and prevention of inherited long-fixture force evidence. The section drawing
and complete R1-S/R4-S print views were visually inspected. The refreshed
[verification report](closure_short/verification.json) records scoped CAD and
four slice PASSes while physical/full-product/force intent remains UNKNOWN.

```sh
./execute.py --threads 1 model/dental_travel_case/closure_short_checks.py
./execute.py --threads 1 model/dental_travel_case/closure_short_drawings.py
./evaluate_model.py model/dental_travel_case/shell_broad_short_test.py --slice --report model/dental_travel_case/notes/closure_short/shell_broad_slice.json --summary
# Repeat for shell_end_short_test.py, perimeter_bead_short_test.py and slide_wall_short_test.py.
./execute.py model/dental_travel_case/closure_short_delivery.py
./execute.py model/dental_travel_case/verification.py --variant research-short-closures
```

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Short test pieces | Partial — two printed, exact variants unknown | Four R1-S–R4-S STEP/STL pairs above; exact printed files not identified | 2026-10-19: excessive engagement effort and noisy opening; development discontinued |
| Final printable object | N/A — samples-only phase | No new full-box export | Production overlap, guidance and ergonomic grips require later integration |

Attribution: primary model GPT-6, reasoning effort not exposed; Codex CLI agent
environment, OpenAI. No sub-agents used, as explicitly requested by the user.
