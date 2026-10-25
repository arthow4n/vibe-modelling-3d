# Connector concept decisions

## User intent and phase boundary

The user reports the R5 short cord is okay and defers further cord modelling.
The next independent object connects a cord terminal loop to an existing key
ring or similar closed loop. Either end must detach without spinning the entire
attachment or winding a split ring around it. Both ends should remain securely
closed in use. PLA and PETG should both be suitable without a spring-return gate,
elastic snap, friction wedge or added spring. Printed assembly parts are preferred;
existing hardware is allowed. The requested deliverable is several SVG suggestions.
Generic reasonable sizing was explicitly delegated after the optional size question.

No load or exact ring dimensions were supplied. New wording calls the previous
cord PETG, whereas its recorded development material is TPU; actual printed spool
is unconfirmed. Connector retention therefore must not rely on cord elasticity.
No CAD/export/slice work is authorized by the SVG handoff itself.

## Architecture screen

An open S-hook does not close both ends. A split-ring-like printed spiral needs
attachment winding and/or elastic deflection. A spring carabiner or flexure gate
would contradict the requested mechanism. A twist-on sleeve can be rigid, but
requires sleeve travel and manipulation around a small loop; it offers no clear
advantage over explicit screw-locked gates for these first drawings.

A uses perpendicular removable screw pins across U-shaped mouths. Nut pockets
prevent rotation; screws provide threaded capture. The free horn is slimmer than
the nut receiver so the cord can enter over the free horn. Pin shanks bridge the
mouths and transfer loop pull into the horns. Nut retention during opening needs
detailing; existing M3 nuts and M3×12 screws are listed in stock preferences.

B seats a straight gate nose ~2 mm into an opposite pocket and locates its tail
in an open-front guide. A keeper screw crosses a closed indexing hole in the
gate into the central body boss. Its shaft blocks translation and its head
blocks lifting; clamp pressure alone is not the retention mechanism. To release,
remove keeper, retract gate ~2.2 mm toward the middle, then lift it normal to
the front face. The opposite gate stays closed. The drawing offsets the removed
gate sideways for visibility; this is not an additional required in-plane travel.
The shallow retraction avoids running the upper gate into the lower gate. Exact
clearance and finger access remain to be established in CAD. Body socket and
central guide support the gate under load; screw still needs a structural check.

C uses separate shoulder hinge pins and heel index screws. The nose socket must
support the closed tongue while allowing outward rotation on release. Index
screws cross closed holes to block rotation. Hinge-pin heads go behind the body,
with the removable index heads in front; separated axes avoid head crowding.
Fasteners must seat against designed stops without clamping the hinge immobile.
Keeper/index holes, shoulders, threads and sockets are principles, not completed
manufacturing geometry in these sheets.

All three have mirrored independent ends. Operating either closure leaves the
other closure untouched. None self-closes. Back-out resistance under repeated
twisting/shaking remains an explicit experiment, even with a positive gate lock.
A threaded connection is not evidence of a vibration-proof lock.

## Whole-object and print considerations

The existing terminal bore, rather than only wire thickness, constrains passage
over the free horn. Overall central thickness may exceed free-horn thickness;
actual local horn diagonals must fit the 7.6 mm faceted R5 bore without stretching.
A/B/C proposed envelopes are approximate and illustrated schematically. The gray
ring and cord indicate attachment context, not validated interpenetration geometry.

B is the preferred first all-printed direction because it avoids hinge fits and
lets small gates be printed broad-face down, with larger coarse keeper threads
in the central body. Removing a gate and keeper is slower and creates loose parts.
C is worthwhile if avoiding a loose gate matters more. A is worthwhile if compact
size and using existing hardware matter more than an all-printed assembly.

Next useful evidence after concept selection would be actual CAD loading paths,
full closure/release motion, screw seating, contact support and a complete small
prototype. Physical qualification must include both ends under pull and twist,
thread loosening, gate wear and deliberate operation. No load rating or universal
printed-thread tolerance follows from the SVG review.
