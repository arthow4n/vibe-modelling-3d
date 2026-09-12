# Sunglasses case — reduced interior and accepted E closure

Print `sunglasses_case.stl`. The matching `sunglasses_case.step` uses the same
open, bed-ready arrangement: body, captive hinged lid, and one separate keeper.
Both large exterior panels lie on the bed. All dimensions below are millimetres.

## Confirmed dimensions and physical feedback

The user printed D and E and found both satisfactory, with a slight preference
for E. The accepted E artifact is retained at revision `bca684e`, STL SHA256
`e9062bcc54901fe00ca580ce24eed744d63309ab8796496524affcfe0961c00c`.

After trying the earlier full case, the user explicitly confirmed a new interior
of **158 × 78 × 63 mm**, reduced from 168 × 88 × 68 mm. These directly specified
dimensions supersede the original approximate glasses measurements. The cavity
has 7 mm corner radii; the dimensions describe its nominal straight-wall extents,
not an unrounded rectangular block that fits into the corners.

The shell is 164 × 84 × 69 mm, excluding hinge/latch projections. Closed overall
bounds including mechanisms are approximately 164 × 105.82 × 69 mm. Walls and
exterior panels remain 3 mm thick. Exterior corner radius 10 mm, broad 2 mm
bottom chamfer and 0.6 mm rounded rims retain the previous comfortable edge treatment.

## E mechanism integration

The loop, receiver and keeper are translated copies of the accepted E geometry:
2.8 mm loop leaves, rounded roots, 0.2 mm seated gap and 3.2 mm outward release
travel. Flexure length and tooth shape were not scaled with the enclosure.
The two hinges use E's 0.20 mm radial cone and 0.20 mm axial ear clearances.
Their centres are 60 mm apart on the full case; E's test fixture used 36 mm.

The separately printed keeper remains identical to E's and can be reused.
Its tapered key retains the tested 0.16 mm leading-end coordinate clearance
and 0.04 mm trailing-end nominal interference. The receiver captures vertical
and outward loads; sideways retention relies on the same tapered fit.

The full shell is stiffer and the hinge/latch distance is greater than on the
coupon. E's physical success supports this choice but does not physically
validate the resized full case's closure force, fatigue or backpack durability.

## Physical print status

Status reviewed 2026-09-12.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | Yes | `D_firm_side_printed_keeper.stl`; `E_extra_firm_side_printed_keeper.stl` | User printed D and E and found both satisfactory; E is the accepted mechanism baseline. |
| Final printable object(s) | No | `sunglasses_case.stl` | The current reduced full case remains unprinted; its closure force, fatigue and backpack durability still need a full-case trial. |

## Printing and assembly

- PETG, 0.4 mm nozzle, 260 × 260 × 250 mm safe printer volume.
- Use your calibrated printer profile. The diagnostic check used 0.2 mm layers,
  5 perimeters, 8 top/bottom layers, 25% gyroid and a 5 mm brim, with supports off.
- Keep both hinged halves in their supplied relative positions. Keep the small
  keeper on its supplied side: rotating it upright recreates the tooth overhang.
- The full print layout is approximately 184.24 × 196.44 × 43.50 mm. Generated
  paths including the brim fit comfortably inside the safe bed. Diagnostic
  consumption is 225.90 g and estimated time 18 h 24 min; printer settings affect both.
- After cooling, remove the brim and gently free the hinges. Slide the keeper's
  narrow end (printed last, opposite the bed-facing end) into the open side of
  the front receiver until approximately flush. Its ramp faces up and flat
  retaining shoulder faces down. No rods, screws, glue or hinge assembly.
- Pull the loop outward to release before lifting the lid. Check seating and
  release on the empty case before putting the glasses inside.

The loop retains a 12 mm bridge supported by its two leaves. The keeper's
locking surface prints as a vertical perimeter rather than a hanging underside.
The source was evaluated and the complete layout sliced without supports or
warnings. These checks do not certify physical print quality.

## Source and verification

`sunglasses_case.py` is the main entry point and defaults to the print pose.
Change `INNER_LENGTH`, `INNER_WIDTH` and `INNER_HEIGHT` to adjust the cavity;
do not scale the exported mesh to change case size. `e_closure.py` contains
the E interfaces in reference coordinates, with no export side effects.
`inspect_case_closed.py` displays the assembled pose without changing exports.

`verify_production_case.py` checks the E interfaces and hinges against the
retained coupon definitions, exercises an alternate 168 × 88 × 68 mm cavity,
and verifies the actual STEP/STL components. The symmetric geometry differences
for the transferred interfaces are zero. All three exported solids are valid,
all three mesh components are watertight and nondegenerate, and their individual
bounds and bed positions agree.

See [production review](production_e_review/report.md),
[checklist](production_e_checklist.md), and [provenance](provenance.md).
Current renders are in `renders/print/`, `renders/closed/` and `renders/verified/`.
Old production renders were removed; historical trial sources and artifacts remain.
