# Sunglasses case — support-free flat print

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
has been evaluated and sliced but has not yet been physically retested.

The ramp-rooted PETG latch has sloped detents and an accessible thumb tab.
Pull the tab outward before lifting the lid. Shell rims meet to carry closing
loads. The hinge is checked through 180 degrees; do not force it beyond that.

## Files and printing

- `sunglasses_case.stl`: complete print-in-place case, already flat and open.
- `hinge_test.stl`: updated production joint on short wall sections and feet,
  approximately 32 × 41.44 × 42.60 mm. Useful for checking the tighter fit.
- `mechanism_test_current.stl`: present hinge and latch settings.
- `mechanism_test_tight_hinge.stl` and `mechanism_test_tight_latch.stl`:
  previous tighter comparison samples.
- `mechanism_test_very_tight_hinge.stl` and
  `mechanism_test_very_tight_latch.stl`: new 0.20/0.20 mm hinge-clearance
  comparison samples.
- `sunglasses_case.step`: complete case in the same flat, open print pose as the STL.
- `sunglasses_case.py`: authoritative parametric source. `LAYOUT` selects
  closed, open, print, coupon or hinge_section; exports retain their intended
  poses.
- `renders/`: closed, open, print, coupon and hinge cutaway views.

### Mechanism test pieces

The full case is unchanged by this test revision. The samples isolate the
uncertain physical interfaces before another large print:

| Sample | Cone radial clearance | Ear gap | Latch tooth shift | Keeper depth |
| --- | ---: | ---: | ---: | ---: |
| current | 0.60 mm | 0.50 mm | 0.00 mm | 1.40 mm |
| tight hinge | 0.35 mm | 0.30 mm | 0.00 mm | 1.40 mm |
| tight latch | 0.35 mm | 0.30 mm | 0.80 mm | 2.20 mm |
| very tight hinge | 0.20 mm | 0.20 mm | 0.00 mm | 1.40 mm |
| very tight latch | 0.20 mm | 0.20 mm | 0.80 mm | 2.20 mm |

The first value is measured at fixed axial position; the normal gap on the
45-degree conical surface is smaller. The tooth shift moves the cantilever's
detent farther outward in the open print pose, and keeper depth extends the
fixed triangular catch. These are test variants, not yet selected production
settings. The `current` sample reproduces the present case interface, the
hinge samples isolate hinge play, and the latch samples test deeper catch
engagement together with their corresponding hinge clearance.

The very-tight 0.20 mm radial value corresponds to approximately 0.14 mm on
the angled mating surface. It may fuse in PETG even on a precise printer; free
it gently if possible and do not force the captive cones.

Print the individual STLs with supports disabled. Each is a shortened
cross-section, so it tests local hinge and latch behavior without reproducing
the full case's bending stiffness. After cooling, flex each latch by hand and cycle its hinge gently.
Check whether the lid stays closed under a light shake and whether
the latch releases without excessive force. A sample tests fit, engagement and
local freeing; it does not establish full-case stiffness, backpack impact
resistance, latch fatigue or lens protection.

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

The case, hinge coupon and mechanism samples have watertight components with
paired triangle edges, no degenerate faces, and bed contact. Final rendered
views were inspected. The mechanism plate was evaluated as six solids and its
three paired samples remain separated. PrusaSlicer 2.9.6 slicing of the case,
hinge coupon and mechanism plate passed with supports disabled, without
stability warnings, bridge infill, overhang perimeter or support roles. The
mechanism plate still needs physical trial printing.
Selected hinge layers were inspected against preceding toolpaths. See
[slicer evidence](support_free_review/report.md) for settings and measurements.

The earlier hinge has a successful user print; the revised hinge fit, full case,
latch force/fatigue and backpack compression resistance still need physical
validation. There is no tested load rating. Slicer success does not measure
surface finish, PETG stringing or joint freedom.

Edit named dimensions near the source top; arbitrary combinations are not
proven. The export fallback path accommodates the local MCP omitting `__file__`;
update it if moving the repository.
