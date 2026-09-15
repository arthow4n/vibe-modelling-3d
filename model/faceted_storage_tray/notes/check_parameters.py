"""Check an alternate pattern/width, then return the final default geometry."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import faceted_storage_tray as tray
vars(tray).update(INTERIOR_WIDTH=200.0, WALL_PANELS=4, FACET_RELIEF=3.0)
alternate = tray.build_tray()
assert alternate.val().isValid()
vars(tray).update(INTERIOR_WIDTH=220.0, WALL_PANELS=6, FACET_RELIEF=2.4)
result = tray.build_tray()
