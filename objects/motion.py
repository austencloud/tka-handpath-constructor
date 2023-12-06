from data.start_end_location_map import get_start_end_locations
from utilities.TypeChecking.TypeChecking import (
    MotionAttributesDicts,
    Colors,
    MotionTypes,
    Locations,
    Locations,
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
        attributes: MotionAttributesDicts,
    ) -> None:
        self.pictograph = pictograph
        self.arrow = arrow
        self.hand = hand
        self.attributes = attributes

        self.setup_attributes(attributes)

    def setup_attributes(self, attributes) -> None:
        self.color: Colors = attributes[COLOR]
        self.motion_type: MotionTypes = attributes[MOTION_TYPE]
        self.arrow_location: Locations = attributes[ARROW_LOCATION]
        self.start_location: Locations = attributes[START_LOCATION]
        self.end_location: Locations = attributes[END_LOCATION]

    def update_attr_from_arrow(self) -> None:
        self.color = self.arrow.color
        self.motion_type = self.arrow.motion.motion_type
        self.arrow_location = self.arrow.arrow_location

        self.start_location = self.arrow.motion.start_location
        self.end_location = self.arrow.motion.end_location
