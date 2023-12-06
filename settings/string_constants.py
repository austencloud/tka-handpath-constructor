ARROW_DIR = "resources/images/arrows/"
HAND_DIR = "resources/images/hands/"
ICON_DIR = "resources/images/icons/"

SVG_NS = "http://www.w3.org/2000/svg"

GRID_FILE_PATH = "resources/images/grid/grid.svg"
HAND_SVG_FILE_PATH = "resources/images/hand.svg"

BLUE = "blue"
RED = "red"
RED_HEX = "#ED1C24"
BLUE_HEX = "#2E3192"

LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"

SHIFT = "shift"
DASH = "dash"
STATIC = "static"

COLOR = "color"
MOTION_TYPE = "motion_type"

LOCATION = "location"
ARROW_LOCATION = "arrow_location"
HAND_LOCATION = "hand_location"
START_LOCATION = "start_location"
END_LOCATION = "end_location"

CLOCKWISE = "cw"
COUNTER_CLOCKWISE = "ccw"

START_POS = "start_position"
END_POS = "end_position"

NORTH = "n"
SOUTH = "s"
EAST = "e"
WEST = "w"

NORTHWEST = "nw"
NORTHEAST = "ne"
SOUTHWEST = "sw"
SOUTHEAST = "se"

ARROW = "arrow"
HAND = "hand"

COLOR_MAP = {RED: RED_HEX, BLUE: BLUE_HEX}

### ICONS ###

SWAP_ICON = "swap.png"
MIRROR_ICON = "mirror.png"

SWAP_COLORS_ICON = "swap_colors.png"

ICON_PATHS = {
    "swap_icon": ICON_DIR + SWAP_ICON,
    "swap_start_end": ICON_DIR + MIRROR_ICON,
    "swap_colors": ICON_DIR + SWAP_COLORS_ICON,
}

ARROW_ATTRIBUTES = [
    COLOR,
    MOTION_TYPE,
    ARROW_LOCATION,
    START_LOCATION,
    END_LOCATION,
]

HAND_ATTRIBUTES = [COLOR, HAND_LOCATION]
