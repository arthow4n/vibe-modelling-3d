"""Short closed-ended stock-only indexed rotary trial; four printed parts + M6 nut."""
from rotary_refinement_design import SAMPLE,build,configuration
result=configuration(build('wheel',dimensions=SAMPLE),'print-study')
