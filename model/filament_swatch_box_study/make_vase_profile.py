"""Object-owned V1 process snapshot: one wall and deliberate vase-only input."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
source=root/'.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json'
profile=json.loads(source.read_text())
profile.update(name='V1 swatch hood PETG spiral .42 wall .20 layer',
    spiral_mode='1',spiral_mode_smooth='0',wall_loops='1',sparse_infill_density='0%',
    top_shell_layers='0',top_shell_thickness='0',bottom_shell_layers='4',bottom_shell_thickness='0',
    line_width='.42',outer_wall_line_width='.42',outer_wall_speed='30',
    enable_support='0',elefant_foot_compensation='0')
path=Path(__file__).parent/'notes/vase_process.json'
path.write_text(json.dumps(profile,indent=2)+'\n')
print(str(path))
