"""h_soft: 12 panels/side, 1.2 mm relief, ridge fraction 0."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from faceted_storage_tray import build_tray
result = build_tray(wall_panels=12, facet_relief=1.2, ridge_fraction=0)
