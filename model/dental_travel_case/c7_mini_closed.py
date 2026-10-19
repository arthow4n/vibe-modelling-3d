"""Inspection only: closed miniature with hidden hinge, no hardware proxies."""
from internal_hinge_design import build, MINI, assembly
result=assembly(build('internal_screw',size=MINI),0)
