from PyQt6.QtCore import QPointF
from settings.numerical_constants import DISTANCE
from settings.string_constants import (
    ARROW_LOCATION,
    COLOR,
    END_LOCATION,
    MOTION_TYPE,
    NORTHEAST,
    SOUTHEAST,
    SOUTHWEST,
    NORTHWEST,
    START_LOCATION,
    TURNS,
)
from objects.arrow import StaticArrow, Arrow

from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from widgets.graph_editor.pictograph.pictograph import Pictograph



class ArrowPositioner:
    def __init__(self, pictograph: "Pictograph") -> None:
        self.letters = pictograph.letters
        self.pictograph = pictograph

    def update_arrow_positions(self) -> None:
        for arrow in self.pictograph.arrows:
            arrow.setTransformOriginPoint(0, 0)
        optimal_locations = None

        if len(self.pictograph.hands) == 2 and len(self.pictograph.arrows) == 2:
            if self.pictograph.current_letter:
                optimal_locations = self.find_optimal_locations()

        for arrow in self.pictograph.arrows:
            if not isinstance(arrow, StaticArrow):
                if optimal_locations:
                    self.set_arrow_to_optimal_loc(optimal_locations, arrow)
                else:
                    self.set_arrow_to_default_loc(arrow)

    def compare_states(
        self, current_state: List[Dict[str, Any]], candidate_state: List[Dict[str, Any]]
    ) -> bool:
        # Filter out non-arrow entries from candidate_state
        filtered_candidate_state = [
            entry
            for entry in candidate_state
            if set(entry.keys()).issuperset(
                {
                    COLOR,
                    MOTION_TYPE,
                    ARROW_LOCATION,
                    START_LOCATION,
                    END_LOCATION,
                    TURNS,
                }
            )
        ]

        if len(current_state) != len(filtered_candidate_state):
            return False

        for arrow in current_state:
            matching_arrows = [
                candidate_arrow
                for candidate_arrow in filtered_candidate_state
                if all(
                    arrow.get(key) == candidate_arrow.get(key)
                    for key in [
                        COLOR,
                        MOTION_TYPE,
                        ARROW_LOCATION,
                        START_LOCATION,
                        END_LOCATION,
                        TURNS,
                    ]
                )
            ]
            if not matching_arrows:
                return False

        return True



    def set_arrow_to_default_loc(self, arrow: "Arrow") -> None:
        arrow.set_arrow_transform_origin_to_center()
        layer2_point = self.pictograph.grid.layer2_points.get(arrow.arrow_location)
        adjustment = QPointF(0, 0)

        if arrow.arrow_location == NORTHEAST:
            adjustment = QPointF(DISTANCE, -DISTANCE)
        elif arrow.arrow_location == SOUTHEAST:
            adjustment = QPointF(DISTANCE, DISTANCE)
        elif arrow.arrow_location == SOUTHWEST:
            adjustment = QPointF(-DISTANCE, DISTANCE)
        elif arrow.arrow_location == NORTHWEST:
            adjustment = QPointF(-DISTANCE, -DISTANCE)

        new_pos = QPointF(
            layer2_point.x() + adjustment.x(),
            layer2_point.y() + adjustment.y(),
        )

        final_pos = QPointF(new_pos.x(), new_pos.y())
        arrow.setPos(final_pos - arrow.boundingRect().center())
