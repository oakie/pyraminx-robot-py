W = 'w'
X = 'x'
Y = 'y'
Z = 'z'

POS = '+'
NEG = '-'

UNDEFINED = '.'
GREEN = 'G'
YELLOW = 'Y'
BLUE = 'B'
ORANGE = 'O'

color_ranges = {
    YELLOW: [(25, 40, 60), (40, 255, 255)],
    BLUE: [(90, 40, 60), (120, 255, 255)],
    GREEN: [(50, 40, 60), (90, 255, 255)],
    ORANGE: [(0, 40, 60), (25, 255, 255)]
}

colors = {
    YELLOW: (0, 255, 255),
    BLUE: (255, 0, 0),
    GREEN: (0, 255, 0),
    ORANGE: (0, 100, 255),
    UNDEFINED: (127, 127, 127)
}

axial_map = {
    W: [None, (1, 0, 0, 0), (2, 0, 0, 0)],
    X: [None, (0, 1, 0, 0), (0, 2, 0, 0)],
    Y: [None, (0, 0, 1, 0), (0, 0, 2, 0)],
    Z: [None, (0, 0, 0, 1), (0, 0, 0, 2)]
}

axial_offset = {
    W: (X, Z, Y),
    X: (W, Y, Z),
    Y: (W, Z, X),
    Z: (W, X, Y)
}

counter_rotation = {
    POS: NEG,
    NEG: POS,
    None: None
}

face_color_map = {
    W: YELLOW, YELLOW: W,
    X: BLUE, BLUE: X,
    Y: ORANGE, ORANGE: Y,
    Z: GREEN, GREEN: Z
}

# Contains two-element lists of transforms and their inverses
transform_map = {
    (W, X): [''],
    (W, Y): [W + NEG, W + POS],
    (W, Z): [W + POS, W + NEG],

    (X, W): [Z + NEG + W + POS, W + NEG + Z + POS],
    (X, Y): [Z + POS, Z + NEG],
    (X, Z): [W + POS + Z + POS, Z + NEG + W + NEG],

    (Y, W): [Z + NEG, Z + POS],
    (Y, X): [X + POS, X + NEG],
    (Y, Z): [W + POS + Z + NEG, Z + POS + W + NEG],

    (Z, W): [Y + POS, Y + NEG],
    (Z, X): [X + NEG, X + POS],
    (Z, Y): [X + POS + W + NEG, W + POS + X + NEG]
}

COAST = 'coast'
BRAKE = 'brake'
HOLD = 'hold'

CART_POS_UNKNOWN = -1
CART_POS_A = 0
CART_POS_B = 1
CART_POS_C = 2
CART_POS_D = 3
CART_POS_E = 4

TOOL_GRP_UNKNOWN = -1
TOOL_GRP_OPEN = 0
TOOL_GRP_SHUT = 1

TOOL_KEY_UNKNOWN = -1
TOOL_KEY_OPEN = 0
TOOL_KEY_SHUT = 1
