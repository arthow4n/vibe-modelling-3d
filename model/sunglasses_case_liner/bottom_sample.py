"""20 mm square crop of the actual S16 bottom panel; upper contact skin faces up.

Print this same file twice to compare ironing off/on. Exposed cut edges retain
actual internal channels; no labels or added edge frame change the test surface.
"""
import design as d

SAMPLE_SIZE = 20.0
result = d.cup().intersect(d.block(SAMPLE_SIZE,SAMPLE_SIZE,d.THICKNESS)).clean()
