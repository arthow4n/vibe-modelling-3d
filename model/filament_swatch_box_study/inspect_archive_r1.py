"""Inspection only: full stack, sparse leaning remainder and selected cards."""
import archive_r1_base_15 as a
import swatch_reference as ref

b = a.base()
c = ref.card(-a.STACK_DEPTH/2)
full = [c.translate((0,n*ref.THICKNESS,0)) for n in range(a.COUNT)]
shift = 95.0
partial = []
for n in range(5):
    y = (n-2)*ref.THICKNESS
    card = (ref.card(y-ref.THICKNESS/2)
        .rotate((0,y,a.FLOOR),(1,y,a.FLOOR),-10)
        .translate((shift,0,.2)))
    partial.append(card)
selected = [ref.card(-10+n*ref.THICKNESS).translate((shift,0,45)) for n in range(2)]
result = a.g.compound(b,*full,b.translate((shift,0,0)),*partial,*selected)
