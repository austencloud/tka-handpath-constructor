from settings.string_constants import (
    NORTHEAST,
    NORTHWEST,
    SOUTHEAST,
    SOUTHWEST,
    CLOCKWISE,
    COUNTER_CLOCKWISE,
    NORTH,
    EAST,
    SOUTH,
    WEST,
)
from utilities.TypeChecking.TypeChecking import (
    Locations,
    MotionTypes,
    StartEndLocationsTuple,
)


start_end_location_map = {
    NORTHEAST: {
        COUNTER_CLOCKWISE: {(EAST, NORTH)},
        CLOCKWISE: {(NORTH, EAST)},
    },
    NORTHWEST: {
        COUNTER_CLOCKWISE: {(NORTH, WEST)},
        CLOCKWISE: {(WEST, NORTH)},
    },
    SOUTHEAST: {
        COUNTER_CLOCKWISE: {(SOUTH, EAST)},
        CLOCKWISE: {(EAST, SOUTH)},
    },
    SOUTHWEST: {
        COUNTER_CLOCKWISE: {(WEST, SOUTH)},
        CLOCKWISE: {(SOUTH, WEST)},
    },
}


def get_start_end_locations(
    motion_type: MotionTypes,
    arrow_location: Locations,
) -> StartEndLocationsTuple:
    return start_end_location_map[arrow_location][motion_type]