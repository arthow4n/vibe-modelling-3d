# AGENTS.md

This repository is for autonomous / vibe-driven 3D modelling with CadQuery.

The goal is to take a modelling request and work toward a satisfactory parametric 3D model with minimal user intervention.

## Core workflow

For modelling tasks, work autonomously toward the requested result.

Use this loop:

1. Understand the requested object and constraints.
2. Create or edit the CadQuery `.py` model.
3. Use the CadQuery MCP `evaluate_file` tool.
4. Inspect the returned:

   * rendered views
   * bounding box
   * volume / surface information
   * topology
   * model parameters
   * build errors, if any
5. Compare the result with the user's request and any reference images or drawings.
6. Modify the model to address the largest discrepancies.
7. Evaluate again.
8. Repeat until further iteration is unlikely to materially improve the result.
9. Export the final model.
10. Save the latest useful rendered views.
11. Commit the completed work.
12. Push the commit to the current remote branch.

Do not stop after producing the first valid model if visible or structural improvements are still obvious.

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

## CadQuery evaluation

The CadQuery MCP is intentionally exposed with a small tool surface.

Use `evaluate_file` as the normal feedback mechanism.

Evaluate the object's source file directly, for example:

```text
model/camera_bracket/camera_bracket.py
```

Do not recreate `evaluate_file` functionality with ad-hoc scripts unless it is unable to perform the required evaluation.

Treat evaluation as part of the modelling process, not merely as a final check.

A successful build alone does not mean the model is finished.

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

When reference images are available, compare the generated views against them carefully.

## Iteration strategy

Prioritize corrections by impact.

A useful order is:

1. overall proportions and bounding dimensions
2. major topology and missing geometry
3. placement and size of major features
4. secondary features
5. fillets, chamfers, transitions, and details
6. cosmetic refinements

Do not endlessly tune insignificant details.

If the request is ambiguous, make reasonable engineering or visual assumptions and continue rather than blocking progress unnecessarily.

Record important assumptions in comments in the model or, when useful, in:

```text
model/<object_name>/notes/
```

## Modelling preferences

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

Use lower-level CadQuery/OCP operations when they materially improve the result, but do not introduce complexity without a reason.

Keep the model readable enough that another agent or human can modify it later.

Avoid destructive conversion to meshes as the primary modelling representation.

## Completion criteria

Before declaring a modelling task complete:

* the CadQuery source builds successfully
* the intended result is a valid solid or valid set of solids
* the latest rendered views have been inspected
* major requested features are present
* proportions and dimensions are reasonable relative to the prompt/references
* obvious geometry defects have been corrected
* the final source file is saved
* appropriate final exports are generated
* the latest useful rendered views are saved
* all files belonging to the object are contained within `model/<object_name>/`

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
* obvious improvements remain

Ask the user only when a genuinely important design decision cannot be inferred and different choices would produce materially different objects.

Otherwise choose a reasonable interpretation, document the assumption if useful, and continue.

## Failure handling

If CadQuery code fails:

1. inspect the actual error
2. fix the smallest underlying issue
3. evaluate again

Do not replace a promising model wholesale after a minor failure.

If an approach repeatedly fails, simplify the construction or choose a different CAD operation.

If a requested detail cannot be modelled reliably, preserve the successful parts of the model and clearly identify the remaining limitation.

## Final response

When finished, summarize:

* what was modelled
* important assumptions
* the object directory, for example `model/camera_bracket/`
* final files created
* any material limitations
* the commit that was created and pushed

Keep the final response concise. The repository artifacts are the primary deliverable.
