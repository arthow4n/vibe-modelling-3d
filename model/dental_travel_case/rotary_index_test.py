"""Historical indexed layout currently printing. Retain shells/wheel; replace its hollow axle with rotary_printed_fasteners.py."""
from rotary_refinement_design import SAMPLE,build,configuration
result=configuration(build('wheel',dimensions=SAMPLE,fastener='legacy-m6'),'print-study')
