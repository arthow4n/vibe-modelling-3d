"""Display-only pose: map print Z to viewer Y. Never export this pose."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from storage_tray import build_tray
result = build_tray().rotate((0, 0, 0), (1, 0, 0), -90)
