"""Inspection only: connected mini box open to 100 degrees."""
from internal_hinge_design import build, MINI, assembly
result=assembly(build('internal_screw',size=MINI),100)
