"""Historical M6 full manufacturing study; not a production print release."""
from rotary_refinement_design import D, build, configuration
result=configuration(build('wheel',dimensions=D,fastener='legacy-m6'),'print-study')
