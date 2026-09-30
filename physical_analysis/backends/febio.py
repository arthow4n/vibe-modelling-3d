"""Experimental FEBio contact route, driven by the swatch release failure.

Not a replacement for the default backend. Peak Green strain is recovered from
nodal kinematics and checked against native element-mean principal strains.
"""
import os
from pathlib import Path
from .structural import CalculixBackend, runtime_environment


class FebioBackend(CalculixBackend):
    backend_name = 'FEBio'
    worker_module = 'physical_analysis.backends.febio_worker'

    def __init__(self, *, augmented_lagrange=True, search_radius_mm=1.0, two_pass=False, force_residual_tolerance_N=1e-6):
        from ..case import positive
        positive(search_radius_mm, 'Contact search radius')
        positive(force_residual_tolerance_N, 'Absolute residual force tolerance')
        self.augmented_lagrange = bool(augmented_lagrange)
        self.search_radius_mm = search_radius_mm
        self.two_pass = bool(two_pass)
        self.force_residual_tolerance_N = force_residual_tolerance_N

    def configure_request(self, request):
        if request['loads'] or not request['nonlinear']:
            raise ValueError('Experimental FEBio route supports nonlinear prescribed motions only')
        if any(c['discretization']!='surface_to_surface' for c in request['contacts']):
            raise ValueError('FEBio route requires surface_to_surface contact intent')
        request['febio'] = dict(augmented_lagrange=self.augmented_lagrange,
                               search_radius_mm=self.search_radius_mm,two_pass=self.two_pass,
                               force_residual_tolerance_N=self.force_residual_tolerance_N)

    def environment(self):
        env=runtime_environment()
        prefix=Path(os.environ.get('FEBIO_RUNTIME','~/.local/opt/febio-exploration/FEBio4')).expanduser()
        env['FEBIO_COMMAND']=os.environ.get('FEBIO_COMMAND',str(prefix/'bin/febio4'))
        env['LD_LIBRARY_PATH']=str(prefix/'lib')+os.pathsep+env.get('LD_LIBRARY_PATH','')
        return env


def evidence_files(directory):
    from .structural import evidence_files as mesh_evidence
    files,_=mesh_evidence(directory)
    files.update(native_input=('analysis.feb',True),native_log=('analysis.log',True))
    return files, ('Decompress analysis.feb.gz and run the recorded FEBio executable with '
                   '-i analysis.feb in a new directory. analysis.inp is the shared mesh deck, '
                   'not the native FEBio solve input. Peak Green strain uses recorded tet10 G8 kinematic recovery.')
