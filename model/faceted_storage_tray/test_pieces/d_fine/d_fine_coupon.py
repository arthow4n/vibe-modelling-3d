"""Full-scale exterior sample for D Fine."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from faceted_storage_tray import build_exterior_coupon
result = build_exterior_coupon(wall_panels=16, facet_relief=2.4, ridge_fraction=0)
