"""Inspection only: grip section with assumed distal-pad access volume."""
import cap_j4_base_5 as j
g=j.grips.g
section=g.block(28,63,-.04,.04,0,13)
result=g.compound(j.base().intersect(section),g.cap().intersect(section),
                  j.grips.finger().intersect(section))
