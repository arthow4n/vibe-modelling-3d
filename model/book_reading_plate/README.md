# Book reading plate — recessed, captive keys

A 400 mm wide PETG L-shaped platform for an open book. Inside dimensions are
250 mm along the back and 40 mm along the lip, with 10 mm walls extending outward.
Two halves join through four internal tenons and four printed tightening keys.

**No connector projects from either broad face.** The rear contains rounded
assembly/release recesses; it is not an uninterrupted sheet, but has no raised
key heads, catches or hardware against your lap. All connectors stay inside the
10 mm wall. The L itself measures 400 × 260 × 50 mm overall.

## How the keys stay in

![Rear view of a locked, recessed joint](renders/assembled/joint_locked_isometric.png)

Two flexible catches are printed **as part of the right half** at each joint.
Push the key into its rear recess until both catches snap behind its enlarged
head. Their flat shoulders block backward travel. The key's shaft and the
surrounding socket constrain sideways movement; its head stops forward travel.
Tilting or inverting the plate does not provide an unlocked escape direction.
The taper tightens the seam; **retention does not depend on taper friction**.

The key head sits 3.8 mm below the rear face. At the nominal locked position its
tip is 0.2 mm below the front face. A head-to-pocket depth stop limits further
insertion so the tip cannot project beyond the front plane. Catch surfaces are
at or below the rear plane. The pocket rims have 0.6 mm bevels and rounded corners.
The main exposed plate edges retain 4 mm radii and the outside L elbow a 9 mm
radius. Bed-contact end edges use a printable 2 mm chamfer.

To remove a key deliberately, unload the plate, spread **both** recessed catch
tips outward, and push the key backward using its front access hole. Fingernails
or blunt tools may be needed for the recessed release access. Do not pry the
head out against engaged catches. The key is loose only after intentional release.

This revision replaces the friction-only keys in commit `e7fd4d2`. Both plate
halves, keys and test piece have changed: use the current matching set. No print
or functional-test result has been reported for either revision.

## Files and recommended first print

**Print [joint_test.stl](joint_test.stl) first.** It contains two cropped blocks
and one full-size key. The complete plate is supplied alongside it.

| File | Purpose / quantity | Print orientation bounds, mm |
| --- | --- | --- |
| [joint_test.stl](joint_test.stl) / [STEP](joint_test.step) | One complete test joint; three pieces | 89.32 × 84.96 × 82 |
| [plate_left.stl](plate_left.stl) / [STEP](plate_left.step) | One male half | 133.90 × 247.24 × 236 |
| [plate_right.stl](plate_right.stl) / [STEP](plate_right.step) | One receiving half with integral catches | 170.37 × 225.41 × 200 |
| [locking_keys.stl](locking_keys.stl) / [STEP](locking_keys.step) | Four recessed keys, already laid out | 100 × 16 × 6 |
| [book_reading_plate_assembled.step](book_reading_plate_assembled.step) | Assembly inspection only; do not slice | 400 × 260 × 50 |

Matching STEP/STL pairs use millimetres and identical placement. Keep the supplied
orientations and relative positions, and center each layout on the bed. Each
plate half is its own print job. The print-layout files do not contain assembled
or display-only geometry.

The authoritative parameters/builders are in [components.py](components.py).
[book_reading_plate.py](book_reading_plate.py) shows the assembly;
[export_plate.py](export_plate.py) builds exports and interface checks;
[verify_exports.py](verify_exports.py) independently checks the saved files.
Use the CadQuery MCP evaluator for these entry points.
[joint_locked.py](joint_locked.py) and [joint_detail.py](joint_detail.py) provide
rear inspection views. [print_preview.py](print_preview.py) reads the exported
coupon STEP for its print-layout illustration.

## Printing and the physical trial

Confirmed material: **PETG**, 0.4 mm nozzle, **260 × 260 × 250 mm** usable envelope.
Reference settings: 0.20 mm layers, six perimeters, six top/bottom layers,
40% gyroid infill, 4 mm outer brim, supports off. Use the same material and
settings for the sample and the production joints. Use your calibrated PETG
and machine settings; the saved profile's 240 °C nozzle / 80 °C bed and timing
are diagnostic assumptions, not an identified printer's validated job.

Both halves stand on their outside ends with the joints upward, rotated 30°
on the bed. The L-shaped feet and brim support the tall prints. Keys print with
the broad head down. Socket openings face upward, key holes have 45° roofs,
and catch roots/hooks grow through sloped transitions. The male rear relief
opens through the tenon tip, avoiding an unsupported closing ledge. The 1.8 mm
catch arms have rounded roots/edges and clearance for outward release movement.
Do not change orientation without reassessing fit surfaces and overhangs.

The arms bend across printed layers in this panel orientation. The coupon is
therefore important for layer bonding, actual flexure and release effort. The
smallest designed catch floor gap is 0.4 mm; check it is clear after printing.
The production catches' full lengths, recesses, keys, clearances and print axes are
reproduced in the full-size single-joint coupon (one pair of catches).

1. Remove brim/strings and check the sockets and catch recesses for debris.
   Slide the test blocks together until the seam closes. Tenon fit clearance
   is 0.20 mm per side, with 0.60 mm tip clearance.
2. Insert the key from the rear, narrow tip first. Its tapered flank faces away
   from the seam. Press until **both hooks visibly return over the head**; this
   is the locked state. Do not leave the key merely friction-seated partway.
3. Invert, shake gently over a tray, pull at the key with a fingernail, and twist
   the blocks. The key should stay captured and the seam should have no noticeable
   rocking. Check for whitening, cracks, incomplete hook return or a fused arm.
4. Release deliberately, repeat several times, and recheck after an overnight
   assembled hold. Confirm the catches remain engaged without continued bending
   and that the rear/front feel flush. If the taper is too tight to reach the
   locked position, adjust `key_seat_clearance` in small 0.02 mm steps and retest;
   increasing it reduces taper interference. If loose, decrease it. This parameter
   changes tightening fit without changing the catch/head engagement dimensions.
   For a binding tenon, inspect debris first, then adjust `socket_clearance`.
5. Assemble the full plate with all four keys fully locked. Gradually test the
   intended book on your lap or a low padded surface, then with both outer sides
   supported. Do not infer full-plate strength from a successful snap test.

The coupon tests local fit, snap engagement, key retention, release and repeatability.
It does not establish full-plate sag, tall-print accuracy, four-joint alignment,
long-term creep, fatigue or strength. Physical retention depends on the catches
printing intact and springing back; no physical result is claimed from CAD alone.

## Verification and remaining limits

The user specified lap use and occasional support at both outer sides, not use
above the face. Book weight was unspecified: **3 kg remains a provisional design
scenario, not a tested load rating**. The approximately 1.1 kg printed plate adds
to that load. No cantilever, impact or person-support load is qualified.

Final CAD checks use CadQuery 2.8.0, OCP 7.9.3.1.1, Python 3.12.14, MCP server 0.2.0:

- Two valid panel solids plus four keys; three separate solids in the coupon.
- Printable layouts fit the envelope and meet the bed; every assembled catch/key
  stays within Z=0–10 mm. The head's depth stop also keeps the tip within that range.
- Panel insertion has no interference at the recorded 36, 18, 2 and 0 mm offsets.
- Seated keys clear the catches. Actual shape intersection places first reverse
  contact at about **0.150 mm**. A 0.5 mm withdrawal intersects both catches, including
  tests shifted ±0.3 mm along either lateral axis.
- Spreading each catch outward 1.65 mm clears the sampled removal path. This is a
  rigid clearance check, not a deformation simulation. The pocket provides at least
  0.35 mm nominal lateral margin at that release displacement.
- The nominal locked taper has 0.062 mm³ interference with its tenon, deliberately
  representing a small physical preload. CAD does not establish seating force.
- Conservative cantilever screening uses 26 mm effective length, 1.8 mm thickness,
  6 mm depth and 1.65 mm lateral displacement: approximately **0.66% root strain**
  and 0.66–1.48 N lateral force per arm for an assumed effective modulus of
  800–1800 MPa. The 1% strain screen is a provisional design choice, not a measured
  PETG limit. Local stress, anisotropy, wear and creep still require the sample.
- The recesses reduce the tenon section. Actual 1 mm CAD slabs at eight positions
  give about **6.5 MPa maximum sampled nominal bending stress** for a 40.5 N central
  load over the 400 mm plate. This excludes stress concentrations, sparse infill,
  receiver deformation and unequal load sharing; it is not a certified safety factor.
- A 380 mm width / 240 mm inner back / 35 mm lip alternate configuration also built
  successfully. All final STEP/STL pairs passed component count, closed-mesh edge,
  winding, bounds, volume and bed-contact checks.

[Geometry checks](notes/geometry_checks.json), [export checks](notes/export_checks.json)
and the [tool/code manifest](notes/evidence_manifest.json) identify parameters,
versions and exact hashes. Reference slicer evidence and estimates are below.
No diagnostic G-code is supplied as a printer-ready job.

## Reference slices and estimates

PrusaSlicer 2.9.6 accepted all four final meshes using the saved
[PETG profile](notes/reference_petg.ini), with fresh nonempty paths, no support
segments, no extracted warnings and deposited footprints inside the corrected
printer envelope, including the 4 mm brim. No repair was reported in the inspected
logs. No printer job was sent. The initial recessed male pocket produced a
collapsing-overhang warning; opening its rear relief through the tenon tip removed
that unsupported ledge and the final left/coupon slices have no such notice.

| Final layout / evidence | PETG including brim | Reference time |
| --- | --- | --- |
| [Joint test](notes/flush_final_joint_test/summary.json) | 66.88 g | 6 h 27 min |
| [Left half](notes/flush_final_plate_left/summary.json) | 583.47 g | 47 h 11 min |
| [Right half](notes/flush_plate_right/summary.json) | 519.78 g | 43 h 1 min |
| [Four keys](notes/flush_locking_keys/summary.json) | 4.44 g | 34 min |
| Complete plate and keys | **1,107.69 g** | **about 90 h 47 min**, sequentially |

These are reference-profile estimates, not predictions for the user's unknown
machine profile. The requested 10 mm walls account for the substantial material
use. Slice reports identify mesh/profile hashes, tool version, command and bounds;
the mesh/export checks independently establish topology and bed contact.

## Print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | Unknown | `joint_test.stl`, `joint_test.step` | Recessed captive-key revision; no user print report. Check both hooks, inversion/shaking, fit, release, layer bonding and overnight relaxation |
| Final printable object(s) | Unknown | `plate_left.stl/.step`, `plate_right.stl/.step`, `locking_keys.stl/.step` | No user print report. Check flushness, full alignment, sag, book support, retention and durability |

Exact printer, actual profile and print date are unknown. Update this record and
the root index together when physical feedback is reported.

## Attribution

Primary language model: GPT-6, identified by session runtime instructions.
Reasoning effort: not exposed. Harness: Codex in the repository workspace.
Provider: OpenAI. No sub-agents or third-party model geometry used. Repository
MIT licence applies. Design/revision evidence recorded 2026-09-22.
