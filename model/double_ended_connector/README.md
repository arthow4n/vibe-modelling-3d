# Two-ended cord / key-ring connector — SVG concepts

Start with the [three-option SVG comparison](renders/concepts/connector_options.svg)
([PNG preview](renders/concepts/connector_options.png)). These are editable concept
sketches for rigid PLA or PETG connectors. Each end opens independently without
rotating the attached loop. No printable model is included in this phase.

**Recommended starting direction: B, sliding lift-out gates.** A rigid gate seats
in an opposite horn pocket; a printed screw through a closed hole in its tail
blocks removal. Retention does not depend on elastic bending or clamp pressure.

| Option and detailed SVG | Proposed envelope | Parts and interaction |
| --- | --- | --- |
| [A — screw-pin shackles](renders/concepts/a_screw_pin.svg) | ~35 × 16 × 7 mm | One printed body, two stock M3×12 screws, two M3 nuts. Unscrew and withdraw one pin, pass the loop over the slim horn, replace pin. Tool needed; removed pin is loose. |
| [B — sliding lift-out gates](renders/concepts/b_sliding_gates.svg) | ~42 × 20 × 9 mm | Five printed parts: body, two gates, two keeper screws. Remove keeper, retract gate ~2.2 mm to clear its socket, lift it out toward the viewer. Gate and keeper become loose. |
| [C — hinged gates](renders/concepts/c_hinged_gates.svg) | ~44 × 20 × 10 mm | Seven printed parts: body, two gates, two hinge pins, two index screws. Remove one index screw and swing that gate outward. Gate remains attached; index screw is loose. |

Each detail sheet shows both ends closed, one end open, the locking principle,
and proposed printing and assembly. Navy is the body, teal the gate, orange a
fastener, gray the existing cord loop and key ring. Gray attachments and enlarged
lock details are schematic. Dimensions are design targets, not manufacturing
profiles; do not extrude these drawings directly as finished parts.

## Sizing, assembly and remaining questions

The user delegated generic sizing. Targets are a 3.2 mm cord section, key-ring
wire up to 3 mm thick, and roughly 6 mm loading openings (5.5 mm in A). The
accepted [R5 cord](../tpu_coil_cord/README.md) has a nominal 7.6 mm bore across
flats. Its faceted 3.2 mm cord has greater diagonal width. Free horns must pass
through that bore without requiring the cord to stretch. Maximum connector
thickness belongs at the central fastener bosses, with slimmer free horns.
Actual rings, local horn sections and complete entry paths still need CAD checks.

Bodies and gates are intended to print separately, broad face down; printed
fasteners head down with shaft upright. PLA or PETG with a 0.4 mm nozzle and
0.2 mm layers is the process assumption. B/C use coarse custom threads rather
than small printed M3 threads. C hinge pins install from the back and index
screws from the front. A uses stock hardware already listed in repository
preferences. No purchased springs, elastic gates or press-fit catches are proposed.

All closures require deliberate screw engagement. No independent anti-back-out
feature is claimed. Thread fit, loosening under shaking, socket fit, load
capacity, wear and operation effort are unqualified. B is preferred for its
simpler rigid gate and two-point support; C trades more parts and clearance for
keeping the gate attached. A offers fewer printed interfaces with metal hardware.

## Evidence and print status

All four SVGs were generated successfully, parsed as XML, rendered with CairoSVG,
and visually reviewed for legibility, part accounting and the opening sequence.
This is visual concept evidence; no CAD, slice, physical fit or strength result.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | SVG proposals only | No printable sample designed in this phase. |
| Final printable object(s) | N/A | None | Concept selection, detailed geometry and physical qualification remain. |

[Design decisions and requirement context](notes/concept_decisions.md) preserve
the reasoning. Regenerate the drawings from the repository root with
`./execute.py model/double_ended_connector/draw_concepts.py`.
The [generator](draw_concepts.py) owns the drawings; it is not a CadQuery model.

## Attribution

Primary language model: GPT 6.1, reasoning F4 Medium, as explicitly supplied by
the user; runtime identity and effort are not independently exposed. Harness:
Codex CLI. Provider: OpenAI. No external artwork or third-party mechanism drawing
was used. Material contributors: user requirements and R5 print feedback.
