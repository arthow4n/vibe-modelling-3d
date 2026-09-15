"""Representative resize proving that the named profile parameters remain usable."""

import sys
from pathlib import Path


object_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(object_dir))
import rounded_square_tray as tray

tray.TOP_OUTER_SIZE = 230.0
tray.TOP_OUTER_RADIUS = 34.0
tray.BOTTOM_OUTER_SIZE = 216.0
tray.BOTTOM_OUTER_RADIUS = 28.0
tray.INNER_SIZE = 210.0
tray.INNER_RADIUS = 27.0

result = tray.build_tray()
