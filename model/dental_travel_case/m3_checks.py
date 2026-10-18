"""Actual M3 CAD engagement/operation checks and load-path explanations."""
import hashlib
import json
from pathlib import Path
import sys

import m1_design as m1
import m2b_design
import m3_design as design
from m1_checks import fit, tube_aperture, end_rounds
from retention_geometry import seated_land
from retention_m2b_checks import layer_connectivity, guide_angle

ROOT=Path(__file__).resolve().parent


def inspect():
    parts=design.build()
    d=parts['dimensions']
    fit(parts)
    tube_aperture(parts)
    end_rounds(parts)
    cap=parts['cap'].val()
    records=[]
    def check(name,a,b,**pose):
        v=a.intersect(b).Volume()
        records.append(dict(name=name,overlap_mm3=v,clear=v<1e-5,**pose))
    check('complete seated',parts['body'].val(),cap)
    offsets=[(0,0),(.25,0),(-.25,0),(0,.25),(0,-.25)]
    for release in (0,1.35,d.release):
        for sign in (-1,1):
            leaf=m1.mirrored(design.tongue(d,release),sign).val()
            for dx,dy in offsets:
                for dz in (-.15,0,.15):
                    check('return / deliberate press',leaf,cap.translate((dx,dy,dz)),
                          sign=sign,release_mm=release,dx=dx,dy=dy,dz=dz)
            lo,hi=d.beam_root+2,d.beam_tip+1.6
            free=leaf.intersect(m1.box(0,0,(lo+hi)/2,d.width+8,d.beam_width+8,hi-lo).val())
            check('leaf and pad clear body guard',free,parts['fixed'].val(),sign=sign,release_mm=release)
    for lift in (0,.25,1,4,12,30,60,106):
        for dx,dy in offsets:
            posed=cap.translate((dx,dy,lift))
            check('guide withdrawal',parts['fixed'].val(),posed,lift_mm=lift,dx=dx,dy=dy)
            for sign in (-1,1):
                check('released hook withdrawal',m1.mirrored(design.tongue(d,d.release),sign).val(),posed,
                      sign=sign,lift_mm=lift,dx=dx,dy=dy)
    lands={str(sign):seated_land(d,cap,sign) for sign in (-1,1)}
    controls={str(delta):{str(sign):seated_land(d,cap,sign,radial_retraction=delta)
                         for sign in (-1,1)} for delta in (1.,1.5)}
    layers=layer_connectivity(d,design.tongue(d).val(),cap)
    guides=[dict(axis=a,sign=s,**guide_angle(parts['fixed'].val(),cap,d,.9,a,s))
            for a in ('x','y') for s in (-1,1)]
    failures=[x for x in records if not x['clear']]
    return dict(status='PASS' if not failures and all(lands.values()) and layers['status']=='PASS' else 'FAIL',
        sources={Path(m.__file__).name:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()
                 for m in (m1,m2b_design,design)},
        producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Finite exact-CAD engagement, return, press and withdrawal; no elastic recovery or force assertion.',
        lands=lands,retraction_controls=controls,first_feature_layers=layers,
        guide_only_angles=guides,poses=records,failures=failures,
        liner='Excluded by user; a later liner will be redesigned.')


if __name__=='__main__':
    answer=inspect()
    path=ROOT/'notes/m3/cad.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(dict(status=answer['status'],pose_count=len(answer['poses']),failures=answer['failures'],lands=answer['lands'])))
