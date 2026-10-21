"""Print all three B1 coupon components; PLA, 0.4 nozzle / 0.2 layers."""
from slider_b_design import build, configuration
result = configuration(build(), 'print')
