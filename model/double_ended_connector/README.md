# Two-ended connector — all-printed hand locks

Three revised **SVG concepts** connect the cord loop to an existing key ring.
Every connector part is printed in PLA or PETG. Each end opens independently by
hand, with no metal, bought springs, elastic snap gate or tools. Operating parts
stay attached; neither loop needs to be twisted or wound onto a split ring.

**View the [new SVG comparison](renders/hand_locks/hand_lock_options.svg)**
([PNG](renders/hand_locks/hand_lock_options.png)). **D, the threaded barrel, is the
recommended simple starting point.** F is worth comparing if a separate
unlock-then-turn sequence matters more than the extra parts.
These are proposals for discussion, not printable files. The old A/B/C drawings
are superseded; metal pins, tool operation and loose keepers miss the revised brief.

![Three all-printed hand locks](renders/hand_locks/hand_lock_options.png)

| Detailed SVG | Approximate envelope | Daily operation | Proposed complete part count |
| --- | --- | --- | --- |
| [D — threaded barrel gate](renders/hand_locks/d_barrel_gate.svg) | 44 × 22 × 10 mm | Turn the barrel down to expose a mouth; turn back until it cups the opposite horn. No hinge. | 5: body, two barrels, two printed stop tips |
| [E — captive screw-driven bolt](renders/hand_locks/e_retracting_bolt.svg) | 48 × 24 × 11 mm | Turn a recessed thumbwheel; a guided bolt retracts into the central body. Reverse to seat it in the opposite horn. | 8: body, cover, two bolts, two lead screws, two printed cover screws |
| [F — rotary gate with index lock](renders/hand_locks/f_rotary_index.svg) | 46 × 24 × 11 mm | Back out a captive thumb lock, then rotate the gate clear. Close and advance the lock tip into its hole. | 8: body, cover, two rotors, two thumb locks, two printed cover screws |

All include both ends. Assembly screws and stop tips are printed too; they are
not removed during normal opening. Two-hand operation is assumed. None self-closes.

## Holding and deliberate release

D needs repeated rotation before the opening appears; its sleeve bridges the
mouth while engaged. E converts repeated thumbwheel rotation into bolt travel;
the bolt cannot retract directly without turning the lead screw. F uses a lock
tip crossing a rotor hole to block gate rotation, rather than squeezing the rotor
with friction. Withdrawing the tip alone leaves the gate covering the opening.
Each detail sheet shows the two-ended object, one open end, an enlarged lock
section, the release sequence and proposed assembly.

These are different ways to resist an accidental single pull or bump. **None has
proved resistance to shaking.** Thread back-out, rubbing against other keys,
wear and deliberate opening effort remain physical questions. No springless lock
here is claimed to be automatically vibration-proof. D has the fewest parts;
E conceals gate travel but needs more housing; F adds a distinct second motion.

## Sizing and manufacture assumptions

The user delegated generic sizing. Retain ~3.2 mm cord section, key-ring wire up
to 3 mm, ~6 mm loading mouths and slim free horns targeting ~3.2 × 4 mm local
sections. The cord's nominal bore is 7.6 mm across flats. Actual horn passage,
attachment routing, gate travel and finger clearance must be checked in CAD if a
concept proceeds; the enlarged lock sections are not dimensioned part drawings.

Separate parts are intended to print without freeing a print-in-place joint.
Body, covers and flat gates print broad face down; coarse screws upright and
barrels upright with an open bore. Assume a 0.4 mm nozzle and 0.2 mm layers.
Coarse thread lead, assembly retention, fit, clearances and load-bearing sections
are still design work. The mechanisms require rigid relative motion, not useful
PLA/PETG spring behavior. This is not yet a printability or strength result.

## Evidence and print status

Four new SVGs were generated, XML-parsed, rendered to PNG and visually reviewed.
The comparison uses consistent object scale; lock sections are enlarged separately.
Navy is body, teal gate, orange hand control or stop; all are the same printed
material. Gray indicates existing attachments, not supplied parts.

| Item | Print status | Artifact(s) | Remaining work |
| --- | --- | --- | --- |
| Test piece(s) | N/A | SVG concepts only | Choose a direction before detailed CAD and a printable prototype. |
| Final printable object(s) | N/A | None | Fit, motion, capture, shaking, wear and load qualification remain. |

[Current decisions and correction](notes/hand_lock_decisions.md) ·
[Historical A/B/C rationale](notes/concept_decisions.md) ·
[Historical A/B/C handoff](notes/r1_handoff.md).
Regenerate only the new sheets with
`./execute.py model/double_ended_connector/draw_hand_locks.py`.
The [generator](draw_hand_locks.py) is drawing source, not a CadQuery model.

## Attribution

Primary language model: GPT 6.1, reasoning F4 Medium, as explicitly supplied by
the user; runtime identity and effort are not independently exposed. Harness:
Codex CLI. Provider: OpenAI. No external artwork or third-party mechanism drawing
was used. Material contributors: user requirements, clarification and cord print
feedback. Historical A/B/C attribution remains in the linked handoff.
