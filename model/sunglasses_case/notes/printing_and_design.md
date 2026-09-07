# Sunglasses case — support-free flat print

**Current work:** the printed case's shape and hinge operation were acceptable,
but hinge play and latch retention failed the user's expectations. For the
replacement small experiments, use [closure_trials.md](closure_trials.md).
The full-size geometry below remains the historical production version.

Confirmed requirements: folded glasses 160 × 80 × 60 mm, PETG, 260 × 260 ×
250 mm safe build volume (X × Y × Z), 0.4 mm nozzle, no supports, no purchased hardware and no hinge assembly.

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
was subsequently printed; the user reported excessive play and weak retention.

The ramp-rooted PETG latch has sloped detents and an accessible thumb tab.
Pull the tab outward before lifting the lid. Shell rims meet to carry closing
loads. The hinge is checked through 180 degrees; do not force it beyond that.

## Files and printing

- `sunglasses_case.stl`: complete print-in-place case, already flat and open.
- `A_twin_hinge_loop_1p8.stl`: twin bearings and positive loop latch.
- `B_twin_hinge_loop_2p6.stl`: twin bearings and more latch engagement travel.
- `C_located_loop_2p6.stl`: B plus locating tabs to limit closed sideways play.
- Each A/B/C sample also has a matching print-ready STEP file.
- `sunglasses_case.step`: complete case in the same flat, open print pose as the STL.
- `sunglasses_case.py`: authoritative parametric source. `LAYOUT` selects
  closed, open, print, coupon or hinge_section; exports retain their intended
  poses.
- `renders/`: closed, open, print, coupon and hinge cutaway views.

### Mechanism test pieces

The obsolete five tolerance samples and standalone hinge STL were removed;
recover them from Git at `1c6b8c3` if needed. Their claims of deeper engagement
were not borne out: extending the keeper and shifting the tooth by equal amounts
left the same nominal peak overlap. The new experiments use a loop beneath a
flat retaining shoulder. See [the current comparison and test instructions](closure_trials.md),
including the short loop bridge and the catch's one-sided overhang risk.

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

The final STEP was reimported through CadQuery MCP: it contains two valid solids, both touching the bed, and its bounds match the STL within 0.05 mm. Its open print pose was visually inspected.

The historical case and hinge coupon had watertight meshes and passed slicing
without supports or warnings. That did not establish satisfactory physical
retention, as the user's later prints demonstrated. See the historical
[slicer evidence](support_free_review/report.md) for settings and measurements.

New A/B/C trial verification is documented separately in `closure_trials.md`.
There is no tested load rating. Slicer success does not measure surface finish,
PETG stringing, joint freedom, latch fatigue or backpack compression resistance.

Edit named dimensions near the source top; arbitrary combinations are not
proven. The export fallback path accommodates the local MCP omitting `__file__`;
update it if moving the repository.
