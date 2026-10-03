"""Inspection only: upward ledge and fingertip below the seated G hood."""
import cap_j3_base_5 as j3
import upward_grips as grips

g=grips.g
window=g.block(29,63,-.04,.04,0,14)
result=g.compound(j3.base().intersect(window),g.cap().intersect(window),
                  grips.finger(1).intersect(window))
