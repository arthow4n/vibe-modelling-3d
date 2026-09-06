# Sunglasses case — support-free flat print

Confirmed requirements: folded glasses 160 × 80 × 60 mm, PETG, 260 × 260 ×
260 mm build volume, no supports, no purchased hardware and no hinge assembly.

## Final design

The case prints open 180 degrees, with both broad exterior faces on the bed.
Its print envelope is 174 × 212.04 × 47 mm, leaving space for a 5 mm brim.
Closed shell dimensions are 174 × 94 × 74 mm, excluding hinge and latch.
The interior is 168 × 88 × 68 mm with 7 mm corner radii; CAD checks confirm
clearance around the complete rectangular glasses envelope. Walls and panels
are 3 mm thick. Exterior corners now have 10 mm radii, the outer panel edges
have 2 mm chamfers, and the meeting rims have 0.6 mm rounds for hand comfort.

Two captive joints use short opposing conical pivots instead of a long rod.
The hinge has a round crown and tangent 45-degree undersides supported by
sloping webs. Socket roofs also grow at 45 degrees. Tiny 0.12 mm flat cone tips
avoid degenerate export triangles while retaining the conical mating surfaces.
Two separate, mechanically captured solids are intentional.

The user successfully printed the earlier hinge coupon and requested less
play. Cone clearance is reduced from 0.7 to 0.6 mm measured radially at fixed
axial position (normal surface gap approximately 0.424 mm). The gap between
adjacent ears is reduced from 0.6 to 0.5 mm. The new round, tighter version
has been evaluated and sliced but has not yet been physically retested.

The ramp-rooted PETG latch has sloped detents and an accessible thumb tab.
Pull the tab outward before lifting the lid. Shell rims meet to carry closing
loads. The hinge is checked through 180 degrees; do not force it beyond that.

## Files and printing

- `sunglasses_case.stl`: complete print-in-place case, already flat and open.
- `hinge_test.stl`: updated production joint on short wall sections and feet,
  approximately 32 × 41.44 × 42.60 mm. Useful for checking the tighter fit.
- `sunglasses_case.step`: closed case for CAD inspection.
- `sunglasses_case.py`: authoritative parametric source. `LAYOUT` selects
  closed, open, print, coupon or hinge_section; exports retain their intended poses.
- `renders/`: closed, open, print, coupon and hinge cutaway views.

Print the STL as supplied. Center the complete object and place it on the bed;
keep its solids together in their original positions. Use **supports disabled**.
The inspected profile uses a 0.4 mm nozzle, 0.2 mm layers, 5 perimeters,
8 top and bottom layers, 25% gyroid infill and a 5 mm brim. Eight solid layers
on each side keep the 3 mm panels solid, avoiding an internal bridging band.
Use your calibrated PETG temperatures and printer profile. The saved diagnostic
profile is for investigation, not machine-ready G-code.

After cooling, remove the brim and strings and gently work the hinge free.
Test the latch and fit before putting glasses inside. If the tighter coupon
fuses, restore or adjust the named clearances and recheck it before a full print.
No rods, nuts, adhesive or hinge assembly are required. Optional soft lining
can protect lenses; keep it away from the hinge, latch and meeting rims.

## Verification and limits

CadQuery MCP evaluations passed for the final case, coupon and alternate
168 × 84 × 64 mm glasses dimensions; the confirmed dimensions were restored
and evaluated again. Checks cover valid solids, closed-state clearance, glasses
fit, lid motion every 5 degrees from 20 to 180 degrees, coupon motion every
15 degrees, and captive retention under attempted axial displacement. Initial
opening requires latch flex, which rigid CAD checks do not simulate.

The final STL files each have two watertight components with paired triangle
edges, no degenerate faces, and both components touching the bed. Final rendered
views were inspected. PrusaSlicer 2.9.6 sliced both models with supports disabled,
without stability warnings, bridge infill, overhang perimeter or support roles.
Selected hinge layers were inspected against preceding toolpaths. See
[slicer evidence](support_free_review/report.md) for settings and measurements.

The earlier hinge has a successful user print; the revised hinge fit, full case,
latch force/fatigue and backpack compression resistance still need physical
validation. There is no tested load rating. Slicer success does not measure
surface finish, PETG stringing or joint freedom.

Edit named dimensions near the source top; arbitrary combinations are not
proven. The export fallback path accommodates the local MCP omitting `__file__`;
update it if moving the repository.
