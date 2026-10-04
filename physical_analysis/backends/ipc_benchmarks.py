"""Narrow qualification fixtures. No object geometry is changed for IPC."""
import cadquery as cq
from .. import AnalysisCase, Material, Region


def compression(motion_mm=.02, *, increment=.1, mesh=.8):
    # Same 2x2x4 mm Poisson-zero specimen / .01 mm gap as the existing
    # contact_case. Clamp lateral top DOFs instead of every interior node:
    # Poisson-zero uniaxial solution is unchanged; interior nodal BCs unsupported.
    material=Material('uniaxial',1200,0,'Numerical uniaxial benchmark, not filament calibration')
    c=AnalysisCase('ipc_compression',max_increment=increment)
    c.add_part('block',cq.Workplane('XY').box(2,2,4,centered=False).translate((0,0,.01)),material=material,mesh_size_mm=mesh)
    c.add_part('floor',cq.Workplane('XY').box(4,4,1,centered=False).translate((-1,-1,-1)),material=material,mesh_size_mm=1)
    c.prescribe_motion('block',Region.plane('z',4.01),displacement_mm=(0,0,-motion_mm),name='push')
    c.fix('floor',name='floor')
    c.contact('block',Region.plane('z',.01),'floor',Region.plane('z',0),penalty_N_mm3=120000)
    c.observe('block',Region.plane('z',.01),name='bottom')
    return c


def flexible_beam(*, mesh=.8, increment=.05):
    material=Material('benchmark',1200,.3,'Numerical homogeneous elastic benchmark')
    c=AnalysisCase('ipc_contact_beam',max_increment=increment)
    c.add_part('beam',cq.Workplane('XY').box(40,8,2,centered=False),material=material,mesh_size_mm=mesh)
    c.fix('beam',Region.plane('x',0),name='root')
    c.add_part('pusher',cq.Workplane('XY').box(2,8,2,centered=False).translate((38,0,2.1)),material=material,mesh_size_mm=1)
    c.prescribe_motion('pusher',displacement_mm=(0,0,-1.1),name='push',progress=((0,0),(.5,1),(1,0)))
    c.contact('beam',Region(lower=(38,0,2),upper=(40,8,2)),'pusher',Region.plane('z',2.1),
              penalty_N_mm3=60000,discretization='surface_to_surface')
    c.observe('beam',Region.plane('x',40),name='tip')
    return c
