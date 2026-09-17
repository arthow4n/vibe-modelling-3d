"""Full-scale exterior sample for H Soft."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from faceted_storage_tray import build_exterior_coupon
result = build_exterior_coupon(wall_panels=12, facet_relief=1.2, ridge_fraction=0)
