# Sunglasses case

Fits the confirmed folded glasses envelope of 160 × 80 × 60 mm. Units are mm.
Interior nominal envelope: 168 × 88 × 68; internal corner radius 4.
Shell: 174 × 94 × 74; including latch and hinge: approximately 174 × 109 × 74.
Walls, floor and roof are 3 mm thick. Rounded plan corners, 0.6 mm exterior
edge chamfers and 0.3 mm rim chamfers soften handling edges. The meeting
wall rims carry closing/compression loads, rather than loading the latch.
This is a protective case design, without a verified compression load rating.

## Files and printing

- `sunglasses_case.py`: authoritative parametric source; evaluate with CadQuery MCP.
- `sunglasses_case.step`: both halves in closed assembly coordinates, no hardware.
- `body.stl` and `lid.stl`: individual parts, already oriented exterior flat face down.
- `sunglasses_case.stl`: both parts separated in print orientation; spans 360 mm,
  so split/rearrange in the slicer or use the individual files on a smaller bed.
- `renders/`: closed views; `open/` shows 110-degree opening; `print/` shows both parts.

Assumed process: PETG, single material, 0.4 mm nozzle, approximately 0.2 mm layers.
Start with 5 perimeters, 6 top/bottom layers and 25% infill; confirm the 3 mm
panels and walls in the slicer. Each part fits a 180 × 120 mm usable bed area,
excluding brim. A 200 × 150 mm or larger bed leaves more room for adhesion aids.
Body height is about 41.5 mm; lid print height is 47 mm including the latch.
Use accessible supports under the exterior hinge barrels/webs and the latch
root overhang. Inspect the latch gap and remove all support without prying hard
on the leaf. Avoid supports in the small hinge bores; clean/ream them to 3.6 mm
if needed. Roof and floor print on the bed, so neither needs a large bridge.
Do not substitute brittle PLA for the flexible PETG latch without redesign/testing.

## Assembly and use

1. Remove supports and smooth the rims, latch and bore mouths.
2. Interleave the hinge knuckles and insert an M3 × 150 mm threaded rod.
   Fit an M3 washer and locknut at each end. File any cut rod ends smooth.
   Leave slight axial play: the nuts retain the rod, not clamp the hinge tight.
   Hardware is not included in the STL/STEP files.
3. Glue approximately 1 mm soft felt or foam lining inside both halves; keep
   glue, seams and lining clear of the hinge, latch and meeting rims. The 4 mm
   allowance on every side includes lining; nominal free envelope with 1 mm
   lining is 166 × 86 × 66 mm. Check actual glasses gently before closing.
4. Press the lid closed until the hook engages. To open, pull the lower front
   tab outward by about 1.5–2 mm, then lift the lid. Do not force the latch.
   The lid is shown at 110 degrees; no mechanical opening stop is provided.

The long leaf, recessed hook and cammed keeper provide intentional release:
pushing the tab inward does not unlock it. Retention overlap is 1.4 mm in Y,
with 0.6 mm vertical clearance under the keeper. The latch and mating hinge
have explicit clearance but require a trial print to establish force and life.
Start opening/closing tests without the glasses; check the latch does not take
a permanent set. Then check lined fit and gently test normal backpack loading.

## Verification and adjustments

CadQuery evaluation confirms two valid solids, no closed-state volume overlap,
and no contact with the full rectangular glasses envelope. Opening clearance
is checked at 5-degree intervals from 20 to 110 degrees; the initial motion
requires manually flexing the latch, which rigid-body CAD does not simulate.
Closed, open and print views were inspected. Exported STL edges are paired
twice, with correct millimetre dimensions and both parts on Z=0 within numeric
precision. Nominal material volume is 208.95 cm³; sliced mass depends on settings.

A 170 × 84 × 64 mm glasses configuration also evaluated successfully, then the
confirmed dimensions were restored and evaluated again. Edit the glasses
dimensions and CLEARANCE near the source top; hinge positions follow width.
If width changes, choose rod length to suit (hinge span + about 14 mm).
The supplied 150 mm rod applies to the original size. The parameters are not
validated across arbitrary dimensions. EXPORT writes adjacent artifacts when
run as a file; its fallback path supports this repository's MCP execution,
which does not supply __file__. Update that fallback if moving the repository.

No slicer or physical print was used. Latch fatigue, lens abrasion, support
removal, hardware fit and compression resistance remain physically unverified.
