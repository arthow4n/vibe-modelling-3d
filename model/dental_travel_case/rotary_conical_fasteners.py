"""Matched conical screw plus unchanged printed nut, both in print placement."""
import cadquery as cq
from rotary_conical_design import printed_axle,screw_print_pose
from rotary_printed_fastener_design import printed_nut
result=cq.Assembly(name='conical_screw_and_printed_nut')
result.add(screw_print_pose(printed_axle()),name='conical_socket_screw')
result.add(printed_nut().translate((22,0,-5.5)),name='unchanged_printed_nut')
