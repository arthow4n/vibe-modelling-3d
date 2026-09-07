# Requirements and functional decisions

Read when interpreting a new object, mechanism or ambiguous physical feedback.

## Requirements clarification

Treat the user's description as a starting point; they may not know which dimensions, interactions, or printing constraints matter. During interpretation and planning, actively look for ambiguity and invite clarification when the answer would improve fit, function, usability, or the printing approach. Do not wait for the user to volunteer technical requirements or silently choose between materially different uses.

* Ask a small set of focused questions in plain language, prioritizing the intended job, what the object must fit, how it is installed and used, and any important loads or environment. For example: “Should this clip onto the desk edge or be screwed underneath?” Explain why the distinction matters and offer a recommended option with its tradeoff when helpful.
* Help the user supply critical measurements: identify exactly what to measure and in which units, or request an available reference or product dimension. A named parameter makes an uncertain dimension editable; it does not establish that the fit is correct.
* Ask about printer, material, build size, or willingness to remove supports only when those answers affect the design. If the user does not know, explain a reasonable default and its implications rather than requiring them to choose CAD operations, tolerances, or slicer settings.
* Before choosing joints, hinges, closures, or other mechanisms, check whether the user accepts assembly and whether all working parts must be printed or purchased items such as rods, screws, nuts, magnets, or adhesives are acceptable. Use preferences already stated in the conversation; otherwise ask before committing to geometry that depends on them. Do not infer that access to a printer means access to hardware or assembly tools.
* When several mechanism approaches are feasible, briefly explain the relevant choices and establish the user's preference. For hinges, these may include print-in-place captive joints, separately printed snap-together joints or pins, flexible hinges, and hardware-based hinges. Discuss only useful alternatives, with their actual tradeoffs: printer clearance accuracy and freeing moving joints, assembly effort, bed footprint, material and fatigue limits, and durability. Recommend an approach suited to the task; do not assume print-in-place or any other mechanism is always best. Once the preference is clear, continue without asking again unless a new constraint requires changing it.
* Briefly state the interpreted use, proposed print approach, and important assumptions before committing to geometry. Separate confirmed requirements from assumptions. Proceed on low-impact visual choices and reversible defaults; wait for clarification before committing to an unresolved interface or use that would produce a materially different object. Continue independent planning while awaiting answers.
* Revisit questions if evaluation reveals an unforeseen conflict between function and printability. Avoid repeated approval requests for routine modelling decisions, and respect a user's request to proceed with reasonable assumptions while clearly identifying unverified fit or performance.

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
