from utilities.TypeChecking.TypeChecking import (
    MotionAttributesDicts,
    Colors,
    MotionTypes,
    Locations,
    Locations,
    RotationDirections,
)
from settings.string_constants import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from widgets.graph_editor.pictograph.pictograph import Pictograph
    from objects.arrow import Arrow
    from objects.hand import Hand


class Motion:
    def __init__(
        self,
        pictograph: "Pictograph",
        arrow: "Arrow",
        hand: "Hand",
        motion_attributes: MotionAttributesDicts,
    ) -> None:
        self.pictograph = pictograph
        self.arrow = arrow
        self.hand = hand
        self.attributes = motion_attributes
        self.setup_attributes(motion_attributes)

    def setup_attributes(self, motion_attributes) -> None:
        self.color: Colors = motion_attributes[COLOR]
        self.motion_type: MotionTypes = motion_attributes[MOTION_TYPE]
        self.arrow_location: Locations = motion_attributes[ARROW_LOCATION]
        
        self.start_location: Locations = motion_attributes[START_LOCATION]
        self.end_location: Locations = motion_attributes[END_LOCATION]

        self.handpath_rotation_direction = self.get_handpath_rotation_direction()

    def update_attr_from_arrow(self) -> None:
        self.color = self.arrow.color
        self.motion_type = self.arrow.motion.motion_type
        self.arrow_location = self.arrow.location

        self.start_location = self.arrow.motion.start_location
        self.end_location = self.arrow.motion.end_location

    def get_handpath_rotation_direction(self) -> RotationDirections:
        if self.motion_type == SHIFT:
            pattern = [self.start_location, self.end_location]
            clockwise_patterns = [
                ["N", "E", "S", "W"],
                ["W", "N", "E", "S"],
            ]
            counterclockwise_patterns = [
                ["N", "W", "S", "E"],
                ["E", "S", "W", "N"],
            ]
            if pattern in clockwise_patterns:
                return CLOCKWISE
            elif pattern in counterclockwise_patterns:
                return COUNTER_CLOCKWISE

        elif self.motion_type in [DASH, STATIC]:
            return None
