# D/E: lighter fixtures with side-printed keeper teeth

These are the next two samples to print. Each STL includes a complete captive
hinge/loop fixture and its separate small keeper insert. Matching STEP files
have exactly the same print placement. The large sunglasses case is unchanged.

## What changed after A/B/C were printed

User feedback on A/B/C (revision `578bc5d`, hashes in
`closure_review/summary.json`): the three felt too similar; C's tabs gave no
noticeable improvement. Hinge movement is acceptable. The keeper underside
drooped and the loop contacted that droop, interfering with seating. Retention
still needs to feel firmer. This confirms the previously identified keeper
overhang risk; absence of slicer warnings did not validate that surface.

D/E address three different causes:

- **Tooth print quality:** a separate keeper prints on its side. Its complete
  tooth outline starts on the bed and continues through the part. The locking
  surface is a vertical perimeter during printing, not a suspended underside.
- **Closed movement:** the designed rail-to-shoulder gap is 0.20 mm, previously
  0.40 mm. The rail must travel 3.20 mm outward to clear the tooth, previously
  1.80 mm (A) or 2.60 mm (B/C). Both new samples use the same keeper geometry.
- **Spring response:** D has 2.20 mm thick leaves; E has 2.80 mm leaves. This
  is a deliberate stiffness comparison, not another small overlap adjustment.
  Both have rounded roots. Actual force and fatigue life remain unmeasured.

The retaining shoulder stays flat. An inward-sloping undercut would also resist
intentional release; stronger spring return and smaller seated clearance are
the selected means of making the loop engage firmly. This is not a preloaded
seal or a claim of zero movement.

The open frame removes the floors and most walls. Hinge shapes, 36 mm spacing,
0.20 mm radial cone clearance and 0.20 mm axial ear clearance are unchanged
from the accepted A/B/C configuration. Latch/hinge separation is also retained.
The skeletal frame is not a proxy for the full case's stiffness or impact strength.

## What to print and assemble

| File stem / embossed letter | Loop leaves | Role |
| --- | ---: | --- |
| `D_firm_side_printed_keeper` / D | 2.20 mm | Start here |
| `E_extra_firm_side_printed_keeper` / E | 2.80 mm | Firmer comparison |

Use PETG, a 0.4 mm nozzle and 0.2 mm layers with your calibrated printer profile.
Keep the supplied print orientation. Do not rotate the separate tooth upright
or automatically rearrange the two hinge-connected halves. Supports are off.
The loop still contains a 12 mm bridge between its leaves; the hinge is unchanged.

**One printed-part assembly step is required.** No rods, screws, nuts or glue:

1. Remove the brim, especially around the small keeper's bed-facing edge.
   Gently free the hinges after cooling.
2. Find the side opening in the front receiver. Slide the keeper into it,
   narrow end first (the end printed last, opposite its bed face). The tooth
   points outward, its entry ramp upward and its flat locking shoulder downward.
   Slide toward the receiver's closed end until the insert is approximately flush.
3. The tapered key is intended to become snug near the end of insertion. It has
   0.16 mm coordinate clearance at the leading end and 0.04 mm nominal interference
   at the trailing end. This is a new fit to validate: stop if it needs excessive
   force, and report a binding or loose insert separately from latch behavior.

The keyway captures upward/outward keeper loads geometrically. Its slight wedge
fit holds it against sideways withdrawal; that friction fit has not been printed
yet. A positive sideways retainer may be needed before production integration
if the insert walks out. D and E use interchangeable keeper inserts.

## Compare the two samples

First pull the loop outward, close the frame, and let the loop return fully
under the tooth. Check that it seats beneath the clean shoulder rather than
on the tooth tip. Try opening without pulling the loop: the shoulder should
block opening. Then operate the finger ledge to pull the loop outward and open.
Also compare normal snap closing, release effort and closed movement.

Report D/E, whether the insert stayed snug, whether the loop seated completely,
and whether opening/release feels too light, comfortable, or too stiff. Note
bridge sag, whitening or cracks separately. Do not force a binding sample.
No glasses or destructive shock test are needed for these mechanism trials.

## Validation and limits

`keeper_latch_trials.py` builds and exports both configurations. CAD checks cover
valid solids, closed fit, shell/hinge rotation, positive latch obstruction during
opening, released clearance, and vertical/outward key capture. Small interference
at the tapered key is intentional; these checks do not simulate elastic flex,
friction, load ratings or fatigue. `verify_keeper_exports.py` checks the actual
three STEP solids and three watertight STL components, individual placements,
nondegenerate facets and bed contact.

Both diagnostic slices use roughly 33 g including brim, versus about 63 g for
A/B/C: approximately **48% less filament**. They take about 3 h 50 min with the
generic diagnostic speeds. See `keeper_review/report.md` for exact measurements,
layer evidence and reproduction commands. Physical success of D/E is unverified.

The earlier [Formlabs snap-fit guide](https://formlabs.com/uk/blog/designing-3d-printed-snap-fit-enclosures/)
supports treating retention geometry and flexible-arm dimensions together.
Its material/process guidance is not a PETG force or fatigue specification.
All D/E dimensions are this project's experimental choices.
