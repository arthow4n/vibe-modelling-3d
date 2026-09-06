"""Editable dimensions, mm. Provisional capacities, not measured user items."""
BRUSH_LENGTH = 238.0
HANDLE_LENGTH = 169.0  # provisional shoulder-to-butt length; test shoulder stop
HANDLE_DIAMETER = 26.0  # circular approximation; button faces up between clips
BRUSH_END_CLEARANCE = 3.5  # each end
BRUSH_LANE = 37.0
PASTE_LENGTH = 200.0
PASTE_WIDTH = 55.0
PASTE_THICKNESS = 40.0
FLOSS_THICKNESS = 30.0  # stands on this narrow edge along case X
FLOSS_WIDTH = 60.0     # along case Y
FLOSS_HEIGHT = 55.0    # vertical
WALL = 2.4
FLOOR = 2.4
DIVIDER_THICKNESS = 2.0
SLOT_CLEARANCE = 0.3   # each side of removable divider
CONTENT_CLEARANCE = 2.0
CORNER = 10.0
EXTERIOR_BEVEL = 1.0
RIM_ROUND = 0.5
HINGE_RADIUS = 5.6
PIVOT_RADIUS = 3.5
PIVOT_TIP_OFFSET = 1.0
CONE_CLEARANCE = 0.6  # radial at fixed X; normal gap = this / sqrt(2)
END_CLEARANCE = 0.5   # axial
EAR_OUTER_OFFSET = 10.0
LATCH_THICKNESS = 1.6
CRADLE_LIFT = 8.0  # raises handle above front rim for finger access
CLIP_WALL = 1.5
CLIP_CLEARANCE = 0.2  # radial clearance to nominal round handle
CLIP_THROAT = 24.0
CLIP_WIDTH = 8.0
FOOT_LENGTH = 18.0
FOOT_WIDTH = 33.0
FOOT_HEIGHT = 3.0
SOCKET_CLEARANCE = 0.2  # each sloping side, coordinate offset in Y
GRIP_BUMP = 0.35      # local friction bumps; trial print must validate retention

IW = max(BRUSH_LENGTH + 2*BRUSH_END_CLEARANCE,
         PASTE_LENGTH + FLOSS_THICKNESS + DIVIDER_THICKNESS + 3*CONTENT_CLEARANCE + 6)
STORAGE_LANE = max(PASTE_WIDTH, FLOSS_WIDTH) + CONTENT_CLEARANCE
ID = BRUSH_LANE + WALL + STORAGE_LANE
IH = max(FLOSS_HEIGHT, PASTE_THICKNESS, HANDLE_DIAMETER+10) + 5.0
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
DIVIDER_X = -IW/2 + 7 + FLOSS_THICKNESS + CONTENT_CLEARANCE
DIVIDER_POSITIONS = (DIVIDER_X, DIVIDER_X+7, DIVIDER_X+14)
SHOULDER_X = BRUSH_LENGTH/2-HANDLE_LENGTH-0.5-WALL/2
CLIP_POSITIONS = (IW/2-88, IW/2-28)
CLIP_RADIUS = HANDLE_DIAMETER/2+CLIP_CLEARANCE
CLIP_Z = FOOT_HEIGHT + CLIP_RADIUS + CLIP_WALL - 0.5
assert CLIP_THROAT < HANDLE_DIAMETER < BRUSH_LANE-8
assert FOOT_WIDTH+2*SOCKET_CLEARANCE+2 < BRUSH_LANE
assert OW + 6 <= 260, 'Length exceeds bed with 3 mm margin each side'
assert 2*OD+2*(HY-OD/2)+6+6 < 260, 'Open case exceeds bed with margins'
assert IH + FLOOR < 250
