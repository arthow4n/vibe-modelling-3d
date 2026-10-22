"""Rough open pose of covered wheel and separate cap keeper."""
from rotary_refinement_design import D, build, configuration
result=configuration(build('wheel',dimensions=D,fastener='printed-coarse'),'open')
