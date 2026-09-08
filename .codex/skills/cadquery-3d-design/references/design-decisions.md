# Requirements and functional decisions

Read when interpreting a new object, mechanism or ambiguous physical feedback.

## Requirements clarification

Reuse the user's known dimensions, printer, material and assembly preferences.
Honor an explicit request to proceed autonomously: choose a reasonable mechanism
and document assumptions instead of asking for routine preference decisions.
Otherwise ask only when an unresolved requirement would materially change fit,
function, usability or manufacturing. Continue independent work while awaiting
an essential answer; do not mistake elapsed time for an answer.

Useful questions establish the intended use, critical interfaces, loads and
whether required hardware or assembly is acceptable. Explain what to measure
and why; do not expect the user to specify every printing detail. Do not assume
access to purchased parts merely because the user has a printer.

When a mechanism choice needs user input, recommend one feasible approach and
briefly explain the meaningful tradeoff. When the user has delegated the choice,
select it directly within known constraints. State the interpreted use, print
approach and consequential assumptions before building. Revisit clarification
only if new evidence reveals a material conflict; a named fit parameter is not
proof that the assumed dimension is correct.

## Functional design

Design functional objects around behavior and interaction, not only shape. Before creating geometry, reason about what must be held, supported, guided, blocked, connected, protected, or constrained; how an item enters or is installed; what retains it after insertion; what prevents accidental movement or release; how it is intentionally removed or adjusted; and what normal forces or disturbances it should tolerate.

Check whether the user can still grab, access, operate, plug in, unplug, or otherwise manipulate the relevant object. Account for required clearance, friction or retention, and flexibility where relevant. Identify obvious everyday failure modes.

For holders, docks, clips, mounts, adapters, organizers, and similar objects, reason through this sequence:

```text
How does the item enter?
How is it retained?
What prevents accidental release?
How is it intentionally removed?
Can the user still access or operate it?
```

A visible slot, opening, hook, or retaining feature is not enough if the held object can fall through, the opening blocks installation, retention is ineffective, or the user cannot reach the object. Avoid designs that require threading a long or attached item through a closed hole when it should be installable in place.

## Critical and vibe dimensions

Separate dimensions that control function from dimensions chosen mainly by visual judgment:

* **Critical dimensions** materially affect fit or function, such as cable diameter, device thickness, shaft diameter, mounting spacing, shelf or desk thickness, insertion clearance, retaining throat/opening, and mating diameter. Ask for these explicitly, infer them conservatively when reasonable, or expose them as named model parameters.
* **Vibe dimensions** do not materially affect function or printability, such as decorative curvature, non-critical taper, visual balance, and cosmetic transitions. External proportions and corner radii belong here only when they do not affect fit, strength, bed contact, or support requirements. Choose and refine these visually as needed.

Critical functional geometry takes priority over cosmetic refinement.

## Translate subjective feedback into a physical question

“Tight” can mean hinge wobble, movement when closed, resistance to accidental
opening, friction during movement, or deliberate release effort. Explain only
the relevant distinctions; ask what happens during use rather than requiring
engineering terminology. Reuse preferences already established.

Trace the load-bearing contact during insertion, seating, attempted opening and
intentional release. Check whether contact blocks motion or cams the parts apart.
Compute engagement from both mating surfaces in a common coordinate frame:
moving both surfaces can leave overlap unchanged. A visible hook, larger tooth,
or collision-free closed pose does not establish positive retention. Where
useful, check that locked movement intersects the catch and released movement
clears it; distinguish rigid motion checks from elastic deformation.

Resolve a known manufacturing defect on a fit-critical surface before offering
another trial that depends on that surface. Disclosing a likely defect does not
make it an informative experiment. Consider orientation, geometry or part
separation within the user's assembly constraints; explain any new tradeoff.
