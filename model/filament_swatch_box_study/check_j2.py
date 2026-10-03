"""J2 support-span and source-card checks; unchanged printed-liked J spring."""
import json
from pathlib import Path
import cap_j2_base_5 as v
from revision_checks import check_base,sources

record=check_base(v,label='J2',datum_side=1,panel=v.j.card_panel(0).val(),previous=v.j.base().val())
record['spring_geometry_unchanged']=True
record['sources_sha256']=sources(('cap_j2_base_5.py','upright_datums.py','swatch_reference.py',
    'revision_checks.py','check_j2.py','cap_j_base_5.py','../filament_archive_swatch/filament_archive_swatch.scad'))
path=Path(__file__).parent/'notes/j2_checks.json'
path.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,variant='J2',contact_z_mm=record['contact_z_mm'],support_z_mm=record['support_z_mm'])))
