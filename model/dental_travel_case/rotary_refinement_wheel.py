"""Rough complete closed-wheel form study; inspection only, not a print release."""
from rotary_refinement_design import D, build, configuration
result=configuration(build('wheel',dimensions=D,fastener='printed-coarse'),'locked')
