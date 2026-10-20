"""Full short-lap dental case pair, in print placement, no references."""
from short_lap_reinforced import build, SELECTED_OVERLAP
from short_lap_comfort import finish
result = finish(build(SELECTED_OVERLAP))['result']
