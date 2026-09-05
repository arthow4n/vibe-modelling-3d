# Sunglasses case — print-in-place revision

The user chose a print-in-place hinge, with no bought rods, nuts or hinge
assembly. Confirmed printer volume: 260 × 260 × 260 mm. Material: PETG.
The design skill was updated and committed separately before this revision.

## Fit and mechanism

- Confirmed folded glasses: 160 × 80 × 60 mm.
- Nominal interior: 168 × 88 × 68 mm, with 4 mm inside corner radii.
- Shell: 174 × 94 × 74 mm; with hinge and latch: about 174 × 113 × 74 mm.
- Walls, floor and roof: 3 mm. Existing thumb latch and glasses clearance retained.
- Two enlarged sections of an integral printed spindle turn inside matching
  sockets on the lid. Narrow socket ends capture the enlarged sections, so
  there is no loose pin to insert and no hardware or adhesive needed to operate
  the case. Two connected-by-capture but unfused solids are intentional.
- Shaft diameter 4.8 mm; enlarged diameter 8.8 mm; socket radial allowance
  0.5 mm per side, plus 0.3 mm axial allowance on each conical transition.
  Minimum socket wall is 1.3 mm. Conical transitions are 45 degrees in print
  orientation. Angled ear undersides grow from their shell wall toward the
  spindle. Exposed upper ear edges have 0.3 mm chamfers.
- The meeting shell rims carry closing loads. The latch catches beneath its
  keeper; pull the lower tab outward about 1.5–2 mm, then lift the lid.
  The hinge opens to 180 degrees; do not force it beyond the evaluated range.

## Which files to print

1. **Start with `hinge_test.stl`.** This uses the same spindle/socket profile,
   clearances, mounting-ear construction and vertical print axis as the case.
   It occupies about 17 × 27 × 63 mm and contains about 7.5 cm³ of material.
   It is designed without supports; add a brim around its two feet. Print both
   captive parts together, then gently work the joint through its motion.
   Check that it rotates and stays captured when gently pulled in either axial
   direction. This tests hinge clearance, not case strength or latch force.
2. **Print `sunglasses_case.stl` as supplied.** The lid is already open 180
   degrees and the whole assembly is standing on the short ends, with the hinge
   axis vertical. Its envelope is about 47 × 210 × 174 mm, leaving room on the
   confirmed bed for brim and accessible supports. Center the complete object
   and place it on the bed; do not auto-orient or separately arrange its solids.
   Splitting into separately positioned objects defeats print-in-place capture.

The former `body.stl` and `lid.stl` are removed because they were for the
hardware hinge and could lead to printing incompatible parts. The single case
STL now preserves all moving-part relationships. `sunglasses_case.step` shows
both halves closed for CAD inspection; it is not the intended print pose.
`sunglasses_case.py` is the authoritative source. `LAYOUT` selects closed,
open (110 degrees), print (180 degrees, standing), coupon, or hinge_section.
Changing the view does not change the poses used for exports.

## PETG slicing and cleanup

Use a 0.4 mm nozzle and start with 0.2 mm layers, 5 perimeters, 6 top/bottom
layers and 25% infill. Inspect the actual paths in the thin socket walls; the
1.3 mm minimum hoop wall should contain multiple extrusion paths. Use the
printer's calibrated PETG profile, moderate speed around the slender spindle,
and a brim around both case feet for the tall print.

The hinge axis is vertical to avoid a supported pin trapped inside a horizontal
bore. **Do not put supports inside the bearing clearances or fuse the two parts
with a mesh-repair/union operation.** The inclined hinge-ear undersides and
socket cones are intended to print without internal supports.

The standing shell still has accessible overhangs: the upper short-end cavity
walls, lower rounded corners, and the external latch/keeper. Add removable
supports there as needed, particularly under the upper inside end walls;
do not assume that those walls will bridge unsupported. Both cavities remain
open for support removal. Inspect the full layer preview before printing.
This is an assembly-free design, not a claim that the whole print is support-free.

After cooling, remove the brim and accessible supports, clean any strings at
the hinge openings, and gently work the lid to free the joint. If the coupon
fuses, adjust the print profile or the clearance parameter and repeat the coupon
before the full case. Do not force a fused spindle. Test latch action without
sunglasses first. Small print adjustments may be needed for comfortable latch
force and reliable retention.

Lining is optional and separate from the mechanism. The allowance permits
roughly 1 mm soft lining on each surface, leaving a nominal 166 × 86 × 66 mm
space; keep any lining clear of the meeting rims, latch and hinge. An existing
soft glasses pouch can also protect lenses if its folded size fits. Check the
actual glasses gently before closing.

## Verification and limits

CadQuery MCP evaluations validate two connected solids, no closed-state
intersection, and clearance around the complete rectangular glasses envelope.
Lid/body intersection is checked every 5 degrees from 20 to 180 degrees; the
initial opening requires manually flexing the latch, which rigid CAD does not
simulate. The coupon is checked every 15 degrees through 180 degrees, and
attempted 1.5 mm axial movement of the socket interferes with each enlarged
shoulder as expected for captive retention.

Closed, open, connected print, coupon and cutaway hinge views were inspected.
The cutaway illustrates the captured enlarged spindle and its clearance; do
not print that visualization. An alternate 168 × 84 × 64 mm glasses envelope
with 0.55 mm radial hinge clearance also passed evaluation. The confirmed
160 × 80 × 60 mm dimensions and 0.5 mm gap were then restored and evaluated.
STL scale, two connected mesh components, watertight edges and Z=0 placement
are verified separately from the CAD solid checks.

No slicer is installed in this workspace and no physical print has been made.
Support strategy and printability have been reviewed geometrically. Actual
joint freedom, latch force/fatigue, support removal and backpack compression
resistance remain unverified; the case has no tested load rating.

Edit the named dimensions and clearances near the source top. The bearing
positions follow case width; arbitrary parameter combinations are not proven.
The fallback export path is for this repository's MCP, which omits __file__;
update that fallback if moving the repository. Normal file execution exports
beside the Python source.
