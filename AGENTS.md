# AGENTS.md

This repository is for autonomous / vibe-driven 3D modelling with CadQuery.

The goal is to take a modelling request and work toward a satisfactory parametric 3D model with minimal user intervention.

## Design for 3D printing

This repository is mainly for creating 3D-printable objects. Unless the request specifies otherwise, design for single-colour printing with a typical 0.4 mm nozzle.

Prefer geometry that is practical to print: use printable wall and feature sizes, avoid details that are too fine to resolve reliably, provide sensible clearances for moving or mating parts, and consider overhangs, bridging, support requirements, orientation, and bed adhesion. Keep designs suitable for a single material and colour; do not rely on multi-material features or colour changes unless explicitly requested.

Use these assumptions when interpreting ambiguous requirements and when judging whether a model is satisfactory. If a request calls for a different printer, nozzle, material, or manufacturing process, follow that request instead and record important assumptions where useful.

## Functional design

Design functional objects around their behavior and interaction, not only their shape. Before creating geometry, reason about what must be held, supported, guided, blocked, connected, protected, or constrained; how an item enters or is installed; what retains it after insertion; what prevents accidental movement or release; how it is intentionally removed or adjusted; and what normal forces or disturbances the object should tolerate.

Consider whether the user can still grab, access, operate, plug in, unplug, or otherwise manipulate the relevant object. Account for required clearance, friction or retention, and flexibility where relevant. Identify obvious ways the design could fail during normal use.

For holders, docks, clips, mounts, adapters, organizers, and similar objects, reason through the interaction sequence:

```text
How does the item enter?
How is it retained?
What prevents accidental release?
How is it intentionally removed?
Can the user still access or operate it?
```

A visible slot, opening, hook, or retaining feature is not enough if the held object can fall through, the opening blocks installation, retention is ineffective, or the user cannot reach the object. Avoid designs that require threading a long or attached item through a closed hole when the item should be installable in place.

Distinguish between critical dimensions and vibe dimensions:

* **Critical dimensions** materially affect fit or function, such as cable diameter, device thickness, shaft diameter, mounting spacing, shelf or desk thickness, insertion clearance, retaining throat/opening, and mating diameter. Ask for these explicitly, infer them conservatively when reasonable, or expose them as named model parameters.
* **Vibe dimensions** do not materially affect function, such as external proportions, decorative curvature, non-critical taper, corner radii, visual balance, and cosmetic transitions. Choose and refine these visually as needed.

Critical functional geometry takes priority over cosmetic refinement.

## Core workflow

For modelling tasks, work autonomously toward the requested result, applying the [Design for 3D printing](#design-for-3d-printing) and [Functional design](#functional-design) guidance unless the request specifies different manufacturing constraints.

Use this loop:

1. Before creating geometry, understand the requested object and constraints, and identify:
   * the object's intended job
   * important physical interactions
   * critical interfaces
   * how a person or another object interacts with it
   * likely everyday failure modes
2. Create or edit the CadQuery `.py` model.
3. Use the CadQuery MCP `evaluate_file` tool.
4. Inspect the returned:

   * rendered views
   * bounding box
   * volume / surface information
   * topology
   * model parameters
   * build errors, if any
5. Compare the result with the user's request and any reference images or drawings, including its intended function, physical interactions, and ergonomics—not only its visual appearance and dimensions.
6. Modify the model to address the largest discrepancies.
7. Evaluate again.
8. Repeat until further iteration is unlikely to materially improve the result.
9. Export the final model.
10. Save the latest useful rendered views.
11. Commit the completed work.
12. Push the commit to the current remote branch.

Do not stop after producing the first valid model if visible, structural, functional, or ergonomic improvements are still obvious. A model is not finished merely because it builds successfully or visually resembles the requested object.

## Object directory convention

Every object must have its own directory under:

```text
model/<object_name>/
```

All files associated with that object must live somewhere inside that directory, regardless of file type.

Do not organize object files globally by format such as `models/`, `exports/`, `renders/`, or `references/`.

Instead, organize by object first.

Preferred structure:

```text
model/
  object_name/
    object_name.py
    object_name.step
    object_name.stl
    object_name.3mf

    references/
      front.jpg
      side.jpg
      top.jpg
      drawing.pdf

    renders/
      isometric.svg
      front.svg
      top.svg
      right.svg

    notes/
      assumptions.md
```

Not every directory or file above is required.

Create only what is useful for the object.

For example:

```text
model/
  camera_bracket/
    camera_bracket.py
    camera_bracket.step
    camera_bracket.stl
    references/
      reference_01.jpg
      reference_02.jpg
    renders/
      isometric.svg
      front.svg
      top.svg
      right.svg
```

Another object should be completely separate:

```text
model/
  impeller/
    impeller.py
    impeller.step
    references/
      front.png
      side.png
    renders/
      isometric.svg
      front.svg
```

This object directory is the unit of ownership for modelling work, generated artifacts, references, and final deliverables.

Do not place object-specific files outside `model/<object_name>/`.

## Source of truth

The CadQuery Python model inside the object's directory is the authoritative source of the geometry.

For example:

```text
model/camera_bracket/camera_bracket.py
```

Keep important dimensions as clearly named parameters near the top of the model where practical.

Prefer parametric and understandable construction over hard-coded point clouds or unnecessarily complicated geometry.

Generated STEP, STL, 3MF, renders, and other artifacts are derived from the `.py` source unless the task explicitly requires otherwise.

## Python dependencies

If a Python-specific dependency is genuinely needed, use `uv` to set it up. Do not use `virtualenv`, ad-hoc virtual environments, or another Python environment manager. Prefer reproducible project setup files such as `pyproject.toml` and `uv.lock`, and commit the related setup files; do not commit environment directories or caches.

## CadQuery evaluation

The CadQuery MCP is intentionally exposed with a small tool surface.

Prefer and use the customized CadQuery MCP `evaluate_file` tool whenever possible; it is the required way to evaluate and iterate on CadQuery models.

If `evaluate_file` is not available for a CadQuery task, do not proceed with the modelling work or recreate the tool with ad-hoc scripts. Refuse the task for now and ask the user to install the customized CadQuery MCP from [cadquery-contrib](https://github.com/arthow4n/cadquery-contrib/tree/feature/loop-customisations), then retry. Use the tool to do CadQuery work whenever possible.

Evaluate the object's source file directly, for example:

```text
model/camera_bracket/camera_bracket.py
```

Do not recreate `evaluate_file` functionality with ad-hoc scripts unless it is unable to perform the required evaluation.

Treat evaluation as part of the modelling process, not merely as a final check.

When inspecting the evaluation results, apply the [Design for 3D printing](#design-for-3d-printing) and [Functional design](#functional-design) guidance in addition to checking the requested geometry.

A successful build alone does not mean the model is finished. Infer functional and ergonomic behavior from the geometry, dimensions, and rendered views; `evaluate_file` does not physically simulate use.

Use rendered views and geometry information to look for:

* incorrect proportions
* missing features
* wrong feature placement
* incorrect orientation
* unintended intersections
* disconnected solids
* excessive or missing material
* incorrect symmetry
* obviously wrong fillets, chamfers, holes, pockets, lofts, sweeps, or other features
* insufficient access or clearance
* weak or ineffective retaining geometry
* insertion or removal problems
* geometry that allows a held object to slip, fall through, detach, or move unintentionally
* features that visually exist but are ineffective for their intended purpose

When reference images are available, compare the generated views against them carefully.

## Iteration strategy

Prioritize corrections by impact, including printability according to the [Design for 3D printing](#design-for-3d-printing) guidance and function according to [Functional design](#functional-design).

A useful order is:

1. intended function and physical interaction
2. critical interfaces and dimensions
3. overall proportions and bounding dimensions
4. major topology and missing geometry
5. placement and size of major features
6. secondary features
7. fillets, chamfers, transitions, and details
8. cosmetic refinements

After function, critical interfaces, and major geometry are established, explicitly review the object for edge treatment before considering it visually finished. Inspect rendered views for raw CAD edges that make an everyday object look unfinished or ergonomically poor.

Do not endlessly tune insignificant details.

If the request is ambiguous, make reasonable engineering or visual assumptions and continue rather than blocking progress unnecessarily.

Record important assumptions in comments in the model or, when useful, in:

```text
model/<object_name>/notes/
```

## Modelling preferences

Apply the [Design for 3D printing](#design-for-3d-printing) and [Functional design](#functional-design) guidance when choosing dimensions, feature details, orientations, and construction methods.

Prefer standard CadQuery operations when they express the geometry cleanly:

* sketches / profiles
* extrude
* revolve
* sweep
* loft
* union / cut / intersect
* mirror
* linear and polar patterns
* fillet
* chamfer

For everyday objects, do not treat sharp CAD edges as finished by default. Actively decide whether exposed edges should be filleted, chamfered, or intentionally left sharp. Consider this for edges touched by fingers or hands, insertion openings, cable slots, clips and retaining features, handles and grips, corners likely to catch on clothing or nearby objects, sliding parts, mating and alignment features, exposed corners that may chip or feel unpleasant, and 3D-printed transitions that would create unnecessary stress concentrations. Visible and touchable exterior corners should usually receive intentional edge treatment unless a sharp edge is functionally required.

Prefer a fillet when the part is touched frequently, a softer ergonomic transition or molded/product-like appearance is desirable, reducing stress concentration is useful, or a curved transition improves handling or insertion. Prefer a chamfer when helping one part enter another, guiding insertion or alignment, breaking a sharp edge with minimal geometry, creating a lead-in around holes, slots, pegs, sockets, or mating interfaces, or when a flat bevel better matches the intended mechanical form. Do not mechanically fillet every edge; choose treatment based on function and visual intent.

Keep edge treatment proportional to the feature. Avoid huge radii that change intended dimensions, tiny cosmetic fillets that add complexity without value, fillets that interfere with mating surfaces or reduce retention lips, clip engagement, or required clearances, and chamfers that unintentionally enlarge openings or weaken thin walls. Preserve fit, retention, and mating geometry first, then apply edge treatment around it.

Use lower-level CadQuery/OCP operations when they materially improve the result, but do not introduce complexity without a reason.

Keep the model readable enough that another agent or human can modify it later.

Avoid destructive conversion to meshes as the primary modelling representation.

## Completion criteria

Before declaring a modelling task complete, verify the result against the [Design for 3D printing](#design-for-3d-printing) and [Functional design](#functional-design) guidance as well as the requested geometry:

* the CadQuery source builds successfully
* the intended result is a valid solid or valid set of solids
* the latest rendered views have been inspected
* major requested features are present
* the intended function and physical interactions have been considered
* critical interfaces and dimensions have been checked
* insertion and removal have been considered where applicable
* the user can access and operate the relevant object where applicable
* retention and likely everyday failure modes have been considered
* exposed and interactive edges have been intentionally reviewed for fillet/chamfer treatment, including whether any should remain sharp
* proportions and dimensions are reasonable relative to the prompt/references
* obvious geometry defects have been corrected
* the final source file is saved
* appropriate final exports are generated
* the latest useful rendered views are saved
* all files belonging to the object are contained within `model/<object_name>/`

Do not declare the object complete while an obvious functional or ergonomic problem remains, even if the CAD model builds successfully.

For normal mechanical / printable models, produce at least:

```text
model/<object_name>/<object_name>.py
model/<object_name>/<object_name>.step
model/<object_name>/<object_name>.stl
```

Use `.3mf` or other formats when useful for the task.

## Render artifacts

Store renders under:

```text
model/<object_name>/renders/
```

Keep only useful final or intentionally retained render artifacts.

The final model should normally have at least:

* isometric
* front
* top
* right

views.

Additional views are encouraged when they reveal important geometry.

Do not commit large numbers of redundant intermediate renders unless they are useful for documenting the design process.

Intermediate or experimental renders should remain inside the same object's directory if retained.

## Reference artifacts

Store all supplied or generated reference material for an object under:

```text
model/<object_name>/references/
```

This includes, where applicable:

* photographs
* screenshots
* drawings
* diagrams
* PDFs
* dimension references
* comparison images

Do not place references for multiple objects together in a global references directory.

## Multiple objects

When a task creates multiple independent objects, create one directory per object:

```text
model/
  object_a/
    ...
  object_b/
    ...
  object_c/
    ...
```

If several files are genuinely components of one logical object or assembly, they may share one object directory:

```text
model/
  gearbox/
    housing.py
    cover.py
    shaft.py
    gearbox.step
    references/
    renders/
```

Use judgment based on whether the files belong to one coherent deliverable.

## Git workflow

Automatic commit and push are preferred for all repository tasks, not only modelling tasks. When a requested change is complete, inspect the status and diff, stage only the relevant files, create a concise commit, and push it to the current upstream branch. Preserve unrelated user changes and do not modify unrelated files merely to make the working tree clean.

When the modelling task is satisfactorily complete:

1. inspect `git status`
2. review the relevant diff
3. ensure generated junk or temporary files are not being committed
4. verify that object-specific files are contained in the correct `model/<object_name>/` directory
5. stage the object's source, final exports, references when appropriate, and latest useful rendered views
6. create a concise descriptive commit
7. push to the current upstream branch

Example commit messages:

```text
model adjustable camera bracket
refine enclosure vent geometry
reconstruct impeller from references
add printable cable guide
```

Do not modify unrelated files merely to make the working tree clean.

If unrelated user changes already exist, leave them intact and commit only files belonging to the modelling task when practical.

## Autonomy

You are expected to make progress without asking for approval after every modelling decision.

Continue iterating while:

* the model is clearly incomplete
* evaluation reveals substantial discrepancies
* a failed construction can reasonably be repaired
* obvious visual, structural, functional, or ergonomic improvements remain

Ask the user only when a genuinely important design decision cannot be inferred and different choices would produce materially different objects.

Otherwise choose a reasonable interpretation, document the assumption if useful, and continue.

## Failure handling

If CadQuery code fails:

1. inspect the actual error
2. fix the smallest underlying issue
3. evaluate again

Do not replace a promising model wholesale after a minor failure.

If an approach repeatedly fails, simplify the construction or choose a different CAD operation.

If a fillet or chamfer fails because of topology or an excessive radius, do not repeatedly retry arbitrary radii. Identify the problematic edge or radius, reduce the radius or apply the treatment selectively, and preserve the successful main geometry. Do not redesign a sound model solely because a cosmetic fillet fails.

If a requested detail cannot be modelled reliably, preserve the successful parts of the model and clearly identify the remaining limitation.

Geometry that builds successfully but is clearly functionally ineffective should be treated as a modelling failure.

## Final response

When finished, summarize:

* what was modelled
* important assumptions
* the object directory, for example `model/camera_bracket/`
* final files created
* any material limitations
* the commit that was created and pushed

Keep the final response concise. The repository artifacts are the primary deliverable.
