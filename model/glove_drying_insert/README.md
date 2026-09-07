# Fold-flat glove drying insert

One insert per glove. Four entirely printed PETG parts: two open frames, one
snap-retained hinge axle, and one removable cuff spreader. Intended as a first
fit for size-8 skiing gloves; the same palm/cuff design can also fit mittens.
There are no finger branches. Actual glove fit and drying performance are untested.

![Expanded insert](renders/open/inspect_isometric.png)

## Files

- `glove_drying_insert.py`: authoritative, parameterized source; evaluate for print layout.
- `glove_drying_insert.stl` and `.step`: matching four-part print layout, millimetres, all parts on bed.
- `glove_drying_insert_assembled.step`: expanded inspection pose, **not** a print layout.
- `hinge_fit_sample.stl` and `.step`: optional three-part hinge-fit sample.
- `inspect.py` / `inspect_folded.py`: expanded and folded inspection entry points.
- `verify.py`: validity, sampled mechanism checks and larger size configuration.
- `export.py`: batch exports and repository STEP/STL consistency checks.
- `renders/`: print, expanded and folded views. `notes/`: recorded evidence and diagnostic profile.

Evaluate entry points with the repository's CadQuery MCP `evaluate_file` tool.
The inspection/export entry points explicitly reload the source module so edits
are picked up in the MCP process. Re-run verify and export after geometry changes.

## Size and packing

| Item | Approximate dimensions |
| --- | --- |
| Folded mechanism, without spreader | 125 × 61.5 × 10 mm |
| Separate spreader | 67.5 × 25.4 × 4 mm |
| Expanded overall envelope | 131 × 61.5 × 67.5 mm |
| Frames | 3.2 mm thick, 6 mm nominal side rails |
| Print layout | 139 × 161 × 10 mm before brim/skirt |

The larger expanded envelope includes the spreader's outer fingers. The actual
cuff separation is approximately 49–52 mm, depending on where it is measured.
The removable spreader packs alongside the folded frames; there is no integrated
storage latch. The two frames stay joined by the axle during normal packing.

Edit `FRAME_LENGTH`, `CUFF_WIDTH`, `PALM_WIDTH`, and `OPEN_HALF_ANGLE` to change fit.
Length is cuff edge to hinge axis, not glove finger length. A 135 mm length / 68 mm
cuff / 48 mm palm configuration was also evaluated successfully. That is one checked
alternative, not a guaranteed continuous size range. Do not scale the whole STL:
that changes hinge clearance and snap geometry too. Small hinge dimensions are
an engineered interface; changing them needs a new mechanical review.

## Print and assemble

Use your PETG profile with a 0.4 mm nozzle. Starting settings: 0.2 mm layers,
4 perimeters, 5 top/bottom layers, 25% gyroid infill, 3 mm outer brim, no supports.
Keep the supplied orientations: the axle lies horizontally so its split arms
bend in the print plane. Remove all brim remnants from the axle slit and spreader
slots. Smooth any rough edges that could catch glove lining.

1. Optionally print `hinge_fit_sample.stl` first (about **6.7 g / 45 min** in the
   diagnostic slice). It preserves the production knuckles, hole, axle, and
   orientations, with only the frame length cropped.
2. Turn one frame over and interleave its center knuckle with the other frame's
   two outer knuckles. The broad flat faces oppose each other in the folded pose.
3. Align the bores and push in the axle, gently pinching the split tip as needed.
   Its head stops one end; the two shoulders should emerge beyond the other
   outer knuckle. Confirm that the frames rotate and the axle cannot slide out.
   Do not hammer it through a tight bore.
4. Insert the folded nose into the glove's palm, keeping the broad cuff bars
   accessible. Open the frames and push the spreader's two slots over the cuff
   bars, with its open slot mouths pointing toward the palm/hinge. The little
   retaining lips pass the far edges of the cuff bars. Confirm both are seated.
5. To pack, pull the spreader back out toward the cuff, easing its outer fingers
   outward if needed; fold the frames together. Leave the axle installed.

The hinge sample tests pin insertion, retention and movement, **not** spreader
force, full-frame stiffness, glove fit or fatigue. If the axle binds, first check
brim/first-layer flare; then adjust `BORE_RADIUS` (radial clearance is currently
0.4 mm). `PIN_SPLIT` and barb geometry control flex and need a new check if edited.
Spreader face clearance is `SLOT_CLEARANCE`; `SNAP_OVERLAP` sets entry restriction.
Do not force stiff snaps: actual PETG, extrusion and surface finish determine feel.

## Drying and hanging

The insert holds the cuff and palm open without suspension. Rest/support the glove
with its cuff facing the dehumidifier's outgoing airflow. This is an insert, not a
freestanding drying stand: its narrow spreader edge is not a stable pedestal.
Keep the appliance's required air path clear. No duct seal or appliance coupling
is intended.

The 5 mm holes in the cuff bars accept an optional cord loop, removable accessory,
or an existing hanger. Route a hanging loop through **both frames** to carry their
load. Check that the glove cannot slip off; secure its own cuff strap if necessary.
A 4 mm hole in the spreader permits an optional tether to a frame. No bought part
is needed for the folding/drying mechanism; cord is optional and not supplied.
There is deliberately no radiator-specific hook. Do not assume PETG or the glove
is suitable for direct contact with an unknown hot radiator: use nearby airflow
and follow the filament/glove/appliance temperature instructions.

## Evidence and limits

CadQuery MCP built four valid, separate production solids. Rigid intersections
were checked at frame half-angles 0, 3, 6, 11, 15, 25 and 45 degrees: no frame/frame
or axle/bearing collisions. At the working angle, the spreader clears both frames;
closing by one degree meets its slot walls. Pulling the spreader out 2 mm meets
its retaining lips, and withdrawing the axle 2 mm meets its shoulder. The compressed
barb cross-section fits a conservative circular bore with 0.5 mm inward displacement
per arm and a remaining 0.1 mm slit gap. These checks establish geometric room and
retention contacts, **not** elastic stress, insertion force, fatigue or creep life.

Final STEP/STL pairs passed valid-solid, closed/wound mesh, per-component bounds,
volume and bed-contact checks. Reports include file/source hashes.

PrusaSlicer 2.9.6 diagnostic results: **about 26 g / 2 h 28 min** for the complete
insert. Both layouts fit 260 × 260 × 250 mm including generated brim/skirt paths,
with no supports or reported slicer notices. Reviewed layer windows show bed-supported
knuckle feet, a narrow bridge closure above the 45-degree bore roof, a preserved
axle slit and printable spreader fingers. Remove the brim carefully from snap gaps.
The saved generic profile and ignored G-code are diagnostic evidence, not a tuned
machine job. Slice the STL with your printer's actual profile before printing.

Unverified: fit in the user's glove, drying rate inside finger tips, wet-liner
behavior, hanging security, standing stability, snap forces, wear and heat exposure.
First try one insert at room temperature and assess fit without stretching the cuff.

Attribution: **GPT-6 Astra, low reasoning effort**, confirmed by the user; harness
**Codex**; provider **user-provided / not separately recorded**.
