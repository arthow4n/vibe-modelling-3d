"""Current coupon print layout, read from verified exported STEP."""
from pathlib import Path
import cadquery as cq
result = cq.importers.importStep(str(Path(__file__).resolve().parent/'joint_test.step'))
