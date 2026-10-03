"""K local XZ/side section: real pocket, outer shoulder crown and its carrier."""
import dome_latch_study as k

# Section through the left nominal shoulder tangency. Keep its real curvature;
# the stem is shown behind the card. This is reference geometry, not a specimen.
nose_x=k.DOME_X-k.NOSE_CONTACT_RADIUS
strip=k.j.g.block(nose_x-.15,nose_x+.15,-2,4.6,k.j.slots.FLOOR,25)
card=k.dome_card().intersect(strip)
panel=k.card_panel().intersect(strip)
result=k.j.g.compound(card,panel)
