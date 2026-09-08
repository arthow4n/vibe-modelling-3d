# Scalloped Vaseline container

Two-piece, nearly round screw-top jar, within a **50 mm diameter envelope × 25 mm closed height**. Twelve broad scallops on both pieces give oily fingers purchase without sharp knurling. A 38 mm mouth, rounded lip and 2 mm inside floor radius make scooping easier. Cavity capacity is approximately 23 mL to the rim; leave headspace and keep the threads clean.

## Use and files

Turn clockwise to close gently against the shoulder; turn counterclockwise to unscrew and lift off. The coarse, single-start 3 mm pitch thread engages over approximately 1.5 turns. No extra hardware, gasket or snap assembly.

- `vaseline_container.py`: authoritative parameterized CadQuery source; millimetres.
- `vaseline_container.step` / `.stl`: both parts in matching print placement.
- `base.step` / `.stl`, `lid.step` / `.stl`: individual parts, same print orientation.
- `vaseline_container_assembled.step`: closed inspection pose only.
- `renders/`: final print and assembled views.
- `verify_and_export.py`: MCP evaluation entry point for exports and mechanical/file checks.
- `inspect_assembled.py`: MCP evaluation entry point for the closed pose.

Print the base floor down and the lid outside-top down, as exported. Assumed PETG, 0.4 mm nozzle, 0.2 mm layers, four perimeters, five top/bottom layers, 20% infill, no supports. Use your own printer profile; the stored profile is diagnostic. Layout is about 107.3 × 49.3 × 22.75 mm, comfortably inside the confirmed 260 × 260 × 250 mm limits.

## Decisions and evidence

- The requested 25 mm height is the assembled height. Scallops cut inward from the 50 mm circle; axis-aligned width is approximately 49.29 mm.
- Neck wall 2 mm; base floor and lid roof 2 mm. Grip valleys stay outside the thread groove. Mouth has a 0.45 mm fillet, top grip edges a 0.65 mm fillet, and bed edges a 0.35 mm chamfer.
- Nominal radial fit allowance 0.30 mm; groove flank allowance includes 0.25 mm axial expansion. Female thread extends through the mouth for entry and release.
- CAD motion sampled every 30° through three opening turns: no solid interference. A straight 0.8 mm lift collides with the retaining thread flanks. These checks establish geometric retention, not friction or opening torque.
- `notes/verification.json`: final combined exports passed solid validity, watertight mesh, component/bounds/volume and bed-contact checks, with file hashes.
- `notes/slice_review/summary.json`: PrusaSlicer 2.9.6 diagnostic slice, no notices or support paths; deposited footprint inside safe limits. Estimate **25.58 g / 2 h 22 min**.
- `notes/thread_layers.png`: inspected current/preceding paths at lid groove and base thread heights. Thread contours grow from adjoining walls; no isolated starts or unsupported cavity roof. Internal solid-fill bridges are over infill, not across the open jar.
- A 52 × 27 mm alternate parameter configuration was checked for a valid two-solid build. Fit and print checks apply to the delivered 50 × 25 mm configuration.

Physical fit, oily-hand grip, wear and resistance to loosening have not been tested. This is a screw closure without a gasket; no leak-tight seal is claimed. First print the full pair: at this size a separate thread coupon saves little while omitting the actual grip and seating behavior. If it binds, remove stray extrusion first, then increase `RADIAL_CLEARANCE` by 0.1 mm and regenerate. Tighten gently.

## Checklist

- [x] Scope, existing edits and required MCP tool checked.
- [x] Use, critical dimensions, material assumption and failure modes established.
- [x] Physical uncertainty identified; full pair selected as first practical trial.
- [x] Orientation, walls and support strategy chosen.
- [x] Parametric geometry built, evaluated and rendered through CadQuery MCP.
- [x] Screw motion, retention, release, grip and scoop access reviewed.
- [x] Final slice and relevant layer paths inspected.
- [x] Exposed edges treated.
- [x] Matching final STEP/STL verified; useful views saved.
- [x] Assumptions, evidence and print instructions recorded.
- [x] Work reviewed and staged for the repository commit/push workflow.

## Attribution

Primary language model: **GPT-6 Astra**. Reasoning effort: **low** (user-provided attribution, interpreting “recently effort load” as “reasoning effort low”). Harness: **Codex**. Provider: **OpenAI**.
