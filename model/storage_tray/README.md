# Rounded storage tray

A one-piece storage tray based on the [supplied photo](references/photo.jpg), with a rounded square cavity, broad tapered exterior, lower shoulder and softened rim. The exterior corners are smooth rather than reproducing the photo's irregular facets. Dimensions and proportions beyond the requested approximately 22 cm interior were chosen autonomously.

## Files and dimensions

- [Printable STL](storage_tray.stl), [STEP](storage_tray.step), and [parametric source](storage_tray.py).
- [Isometric view](renders/print/storage_tray_isometric.png) and [side profile](renders/print/storage_tray_front.png).
- Interior: **220 × 220 mm between opposing straight walls**, 28 mm corner radius; rounded corners reduce corner clearance.
- Overall: **238 × 238 × 38 mm**; interior depth 34 mm, base 4 mm.
- Floor blend radius 4 mm: the flat floor spans 212 mm between blend tangencies at the middle of each side. The rim's 0.8 mm edge rounding slightly widens the very top opening.
- Rim wall 4 mm before edge rounding; exterior grows to a 9 mm horizontal wall section at the lower shoulder. A 0.6 mm underside chamfer breaks the bed edge.

Edit the named parameters at the top of `storage_tray.py`; `build_tray()` is the main builder. STEP and STL share millimetre units, XY centre at the origin and flat underside at Z=0. No assembly is required.

## Printing and use

Print flat underside down, open side up. Assumed indoor general storage in PLA, 0.4 mm nozzle, 0.2 mm layers, four perimeters, five top/bottom layers and 20% gyroid infill. No supports are intended. Use your printer's own material and machine profile; the retained reference profile is for inspection only.

The broad flat base provides stable contact. The lower exterior grows just 2 mm per side over 9 mm of height; the upper wall slopes inward and the cavity remains open, with no roof or trapped supports. Wall thickness accommodates multiple extrusion paths. The floor blend makes small items easier to retrieve and avoids a sharp internal dirt trap. Retention is by the open tray walls, with unrestricted top access; it is not a closed transport container.

The 238 mm footprint fits the 250 × 250 × 250 mm practical envelope. The reference slice uses no skirt or brim. If adhesion needs a brim, allow at most 5 mm per side and recheck the complete slicer footprint. Large flat prints can warp; actual flatness, surface feel and load capacity remain untested. No separate coupon is useful for this simple tray because full-footprint warping is the main physical uncertainty.

## Verification

- CadQuery MCP evaluation: valid single solid, 238 × 238 × 38 mm, volume 415,974.73 mm³. Versions: CadQuery 2.8.0, OCP 7.9.3.1.1, Python 3.12.14, server 0.2.0.
- Source SHA256: `131fd28f3b1c9ddf8a46875b3dc979350516ea57a730854f30201c9c4e8d17d1`.
- Viewed the isometric outline for cavity/rim and side profile for taper and shoulder. Smooth corners approximate the reference; a single photograph does not establish exact original geometry.
- [Export checks](notes/export_checks.json): valid STEP, closed consistently wound STL, one matching component, bounds/volume agreement and bed contact passed. [MCP check entry point](notes/check_exports.py) also verifies four interior wall planes at X/Y = ±110 mm in the actual STEP.
- [Reference smoke slice](notes/slice_review/summary.json), [command](notes/slice_review/command.json), [profile](notes/review.ini): PrusaSlicer 2.9.6 produced fresh nonempty deposition, no supports, no notices; no repair reported in the inspected log. Deposited XY bounds after centering: 6.017–243.983 mm on each axis; height 38 mm.
- Reference estimate: 315.51 g PLA, 25 h 27 min. These are profile-specific estimates, not predictions for the user's printer. CAD/export and slice checks do not establish physical strength or print quality.

### Design checklist

- [x] Scope, photo, user changes and required MCP tool checked; defaults chosen under user authorization.
- [x] Interior dimension, access, retention, edge treatment and ordinary storage use reviewed.
- [x] Single-piece layout, bed contact, wall sizes, overhangs and support strategy reviewed.
- [x] Parametric source evaluated; bounds, topology, final views and actual interior wall positions checked.
- [x] Matching exports independently checked; final reference smoke slice passed.
- [x] Deliverables, reference, print instructions, attribution and physical limitations saved.
- [x] Separate test piece considered: not warranted; full tray is the first physical trial.

## Physical print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None | Full tray is the physical trial; no fit or moving interface needs a coupon. |
| Final printable object(s) | Unknown | `storage_tray.stl`, `storage_tray.step` | No user print report. Check base flatness, rim comfort, finish and stiffness with intended contents. |

## Attribution

Primary language model: GPT-6 Astra; reasoning effort: low (both explicitly supplied by the user). Harness: Codex coding agent/API environment. Provider: OpenAI. No additional model contributors. User supplied the reference photograph; original photograph creator and licence are unknown. The photograph is retained as design reference, with no claim of authorship or relicensing.
