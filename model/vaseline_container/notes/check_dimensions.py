"""One representative parameter change; evaluate with CadQuery MCP."""
from pathlib import Path
import json
D = Path('/home/hevar/git/vibe-modelling-3d/model/vaseline_container')
s = (D/'vaseline_container.py').read_text().replace('OUTER_DIAMETER = 50.0','OUTER_DIAMETER = 52.0').replace('CLOSED_HEIGHT = 25.0','CLOSED_HEIGHT = 27.0')
n = {}; exec(compile(s,'vaseline_container_variant','exec'),n)
result = n['result']
assert result.isValid() and len(result.Solids()) == 2
(D/'notes/parameter_check.json').write_text(json.dumps({'diameter_mm':52,'closed_height_mm':27,'valid_solids':2,'scope':'Build check only; does not validate arbitrary parameter combinations.'},indent=2)+'\n')
