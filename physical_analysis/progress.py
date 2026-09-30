"""Read contact-study progress and actual driver travel without a solver rerun.

This is a diagnostic of saved converged increments, not a convergence forecast
or a completed-path quality result. It avoids repeatedly searching large logs.
"""
import argparse
import json
import math
from pathlib import Path
import re


def prescribed_position(constraint,time):
    points=constraint.get('progress') or ((0,0),(1,1))
    for (a,x),(b,y) in zip(points,points[1:]):
        if time<=b+1e-9:
            value=x+(y-x)*(time-a)/(b-a)
            return [(v or 0)*value for v in constraint['displacement_mm']]
    raise ValueError('Converged fraction outside motion curve')


def run_progress(directory):
    directory=Path(directory);case=json.loads((directory/'case.json').read_text())
    times=[]
    if 'febio' in case:
        # The contact table is small even when nodal output is hundreds of MB.
        source=directory/'contact_0.txt'
        if source.is_file():
            for line in source.read_text().splitlines():
                if re.match(r'^\*?Time\s*=',line):times.append(float(line.split('=',1)[1]))
        backend='FEBio'
    else:
        source=directory/'analysis.sta'
        if source.is_file():
            for line in source.read_text().splitlines():
                values=line.split()
                if len(values)==7 and values[0].isdigit():times.append(float(values[4]))
        backend='CalculiX'
    if any(not math.isfinite(t) or not 0<=t<=1+1e-6 for t in times) or any(b<=a for a,b in zip(times,times[1:])):
        raise ValueError('Invalid converged progress sequence')
    old=json.loads((directory/'result.json').read_text()) if (directory/'result.json').is_file() else None
    recent=times[-12:];travel={}
    for constraint in case['constraints']:
        if any(v for v in constraint['displacement_mm'] if v is not None):
            travel[constraint['name']]=[math.dist(prescribed_position(constraint,a),prescribed_position(constraint,b)) for a,b in zip(recent,recent[1:])]
    return dict(backend=backend,status=old['status'] if old else 'no_final_result',
                completed=old['completed'] if old else False,converged_frames=len(times),
                last_converged_fraction=times[-1] if times else None,
                recent_converged_fractions=recent,recent_driver_travel_mm=travel,
                requested_max_increment=case['max_increment'],
                limits='Saved accepted increments only. No prediction of eventual convergence, operating force, strain or contact passage. Small travel steps locate adaptive cutback; they do not establish its cause.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory');a=p.parse_args()
    print(json.dumps(run_progress(a.directory),indent=2))
