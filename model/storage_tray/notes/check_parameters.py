"""Representative parameter check; display geometry only, no exports."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import storage_tray as tray
tray.INTERIOR_WIDTH = 200.0
result = tray.build_tray()
assert abs(result.val().BoundingBox().xlen - 218.0) < 1e-4
