"""Longer covered-wheel screw plus unchanged printed nut, head/flat face down."""
import cadquery as cq
from rotary_covered_design import printed_axle,screw_print_pose
from rotary_printed_fastener_design import printed_nut
result=cq.Assembly(name='covered_wheel_screw_and_nut')
result.add(screw_print_pose(printed_axle()),name='longer_socket_screw')
result.add(printed_nut().translate((22,0,-5.5)),name='unchanged_printed_nut')
