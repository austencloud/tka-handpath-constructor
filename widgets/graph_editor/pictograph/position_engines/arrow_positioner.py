from PyQt6.QtCore import QPointF
from settings.numerical_constants import DISTANCE
from settings.string_constants import (
    NORTHEAST,
    SOUTHEAST,
    SOUTHWEST,
    NORTHWEST,
)
from objects.arrow import StaticArrow, Arrow

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from widgets.graph_editor.pictograph.pictograph import Pictograph


class ArrowPositioner:
    def __init__(self, pictograph: "Pictograph") -> None:
        self.letters = pictograph.letters
        self.pictograph = pictograph

    def update_arrow_positions(self) -> None:
        for arrow in self.pictograph.arrows:
            arrow.setTransformOriginPoint(0, 0)
        for arrow in self.pictograph.arrows:
            if not isinstance(arrow, StaticArrow):
                self.set_arrow_to_default_loc(arrow)

    def set_arrow_to_default_loc(self, arrow: "Arrow") -> None:
        arrow.set_arrow_transform_origin_to_center()
        layer2_point = self.pictograph.grid.layer2_points.get(arrow.location)
        adjustment = QPointF(0, 0)

        if arrow.location == NORTHEAST:
            adjustment = QPointF(DISTANCE, -DISTANCE)
        elif arrow.location == SOUTHEAST:
            adjustment = QPointF(DISTANCE, DISTANCE)
        elif arrow.location == SOUTHWEST:
            adjustment = QPointF(-DISTANCE, DISTANCE)
        elif arrow.location == NORTHWEST:
            adjustment = QPointF(-DISTANCE, -DISTANCE)

        new_pos = QPointF(
            layer2_point.x() + adjustment.x(),
            layer2_point.y() + adjustment.y(),
        )

        final_pos = QPointF(new_pos.x(), new_pos.y())
        arrow.setPos(final_pos - arrow.boundingRect().center())
