"""Dimensions in mm; approximate user measurements, with explicit allowances."""
BRUSH_LENGTH = 255.0
HANDLE_LENGTH = 165.0
HANDLE_DIAMETER = 30.0  # user reports nearly cylindrical; physical clip fit pending
BRUSH_END_CLEARANCE = 2.0  # each end; length is close to the 270 mm print envelope
BRUSH_LANE = 41.0
PASTE_LENGTH = 200.0
PASTE_WIDTH = 60.0  # capacity exceeds measured 160 x 55 x 40 mm tube
PASTE_THICKNESS = 44.0
WALL = 2.4
FLOOR = 2.4
CONTENT_CLEARANCE = 4.0
CORNER = 10.0
EXTERIOR_BEVEL = 1.0
RIM_ROUND = 0.5
PARTITION_CORNER_RADIUS = 14.0  # broad upper corners in the long separator profile
PARTITION_EDGE_RADIUS = 0.8     # soft edge across its 2.4 mm thickness
HINGE_RADIUS = 5.6
PIVOT_RADIUS = 3.5
PIVOT_TIP_OFFSET = 1.0
CONE_CLEARANCE = 0.6  # radial at fixed X; normal gap = this / sqrt(2)
END_CLEARANCE = 0.5   # axial
EAR_OUTER_OFFSET = 10.0
LATCH_THICKNESS = 1.6
CRADLE_LIFT = 8.0  # raises handle above front rim for finger access
CLIP_WALL = 1.2  # curved PETG arms; same geometry in quick fit sample
CLIP_CLEARANCE = 0.15  # radial; retention is throat capture, not bore friction
CLIP_THROAT = 28.4
CLIP_WIDTH = 8.0
FOOT_LENGTH = 18.0
FOOT_WIDTH = 37.0
FOOT_HEIGHT = 3.0
SOCKET_CLEARANCE = 0.2  # each sloping side, coordinate offset in Y
GRIP_BUMP = 0.35      # local friction bumps; trial print must validate retention

IW = max(BRUSH_LENGTH + 2*BRUSH_END_CLEARANCE, PASTE_LENGTH + 2*CONTENT_CLEARANCE)
STORAGE_LANE = PASTE_WIDTH + CONTENT_CLEARANCE
ID = BRUSH_LANE + WALL + STORAGE_LANE
IH = max(PASTE_THICKNESS + 6.0, HANDLE_DIAMETER + 16.0)
OW, OD = IW + 2*WALL, ID + 2*WALL
HEIGHT = IH + 2*FLOOR
SEAM = HEIGHT/2
HY = OD/2 + HINGE_RADIUS*2**0.5 + 0.8
BEARING_CENTERS = (-OW/2 + 52, OW/2 - 52)
PIVOT_ROOT = PIVOT_TIP_OFFSET + PIVOT_RADIUS
RECEIVER_HALF = PIVOT_ROOT - END_CLEARANCE
BRUSH_Y = -ID/2 + BRUSH_LANE/2
PARTITION_Y = -ID/2 + BRUSH_LANE + WALL/2
STORAGE_Y = ID/2-STORAGE_LANE/2
CLIP_POSITIONS = (BRUSH_LENGTH/2-85, BRUSH_LENGTH/2-25)
CLIP_RADIUS = HANDLE_DIAMETER/2+CLIP_CLEARANCE
CLIP_Z = FOOT_HEIGHT + CLIP_RADIUS + CLIP_WALL
assert CLIP_THROAT < HANDLE_DIAMETER < BRUSH_LANE-8
assert FOOT_WIDTH+2*SOCKET_CLEARANCE+2 < BRUSH_LANE
assert OW + 6 <= 270, 'Length exceeds bed with 3 mm margin each side'
assert 2*OD+2*(HY-OD/2)+6+6 < 270, 'Open case exceeds bed with margins'
assert IH + FLOOR < 250
