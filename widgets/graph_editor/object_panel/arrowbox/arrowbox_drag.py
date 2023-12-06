from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QTransform
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt
from settings.string_constants import (
    ANTI,
    BLUE,
    CLOCKWISE,
    COLOR,
    COUNTER_CLOCKWISE,
    IN,
    LAYER,
    NORTHEAST,
    NORTHWEST,
    PRO,
    HAND_LOCATION,
    RED,
    SOUTHEAST,
    SOUTHWEST,
)
from objects.arrow import Arrow
from typing import TYPE_CHECKING, Dict, Tuple

from widgets.graph_editor.object_panel.objectbox_drag import ObjectBoxDrag
from utilities.TypeChecking.TypeChecking import (
    ArrowAttributesDicts,
    Colors,
    MotionTypes,
    Locations,
    RotationDirections,
    Locations,
    RotationAngles,
)
from data.start_end_location_map import get_start_end_locations

if TYPE_CHECKING:
    from main import MainWindow
    from widgets.graph_editor.pictograph.pictograph import Pictograph
    from widgets.graph_editor.object_panel.arrowbox.arrowbox import ArrowBox


class ArrowBoxDrag(ObjectBoxDrag):
    def __init__(
        self, main_window: "MainWindow", pictograph: "Pictograph", arrowbox: "ArrowBox"
    ) -> None:
        super().__init__(main_window, pictograph, arrowbox)
        self.attributes: ArrowAttributesDicts = {}
        self.arrowbox = arrowbox
        self.objectbox = arrowbox
        self.ghost_arrow = None
        self.start_orientation = IN
        self.setup_dependencies(main_window, pictograph, arrowbox)

    def match_target_arrow(self, target_arrow: "Arrow") -> None:
        self.target_arrow = target_arrow
        self.target_arrow_rotation_angle = self._get_arrow_drag_rotation_angle(
            self.target_arrow
        )
        self.is_svg_mirrored = target_arrow.is_svg_mirrored
        super().match_target_object(target_arrow, self.target_arrow_rotation_angle)
        self.set_attributes(target_arrow)
        self.apply_transformations_to_preview()

    def set_attributes(self, target_arrow: "Arrow") -> None:
        self.color: Colors = target_arrow.color
        self.motion_type: MotionTypes = target_arrow.motion_type
        self.arrow_location: Locations = target_arrow.arrow_location
        self.rotation_direction: RotationDirections = target_arrow.rotation_direction

        self.ghost_arrow = self.pictograph.ghost_arrows[self.color]
        self.ghost_arrow.target_arrow = target_arrow

    def place_arrow_on_pictograph(self) -> None:
        self.placed_arrow = Arrow(self.pictograph, self.ghost_arrow.get_attributes())

        self.placed_arrow.hand = self.ghost_arrow.hand
        self.ghost_arrow.hand.arrow = self.placed_arrow
        self.pictograph.add_motion(
            self.placed_arrow, self.ghost_arrow.hand, self.motion_type, IN, 1
        )
        self.pictograph.addItem(self.placed_arrow)
        self.pictograph.arrows.append(self.placed_arrow)

        self.pictograph.removeItem(self.ghost_arrow)
        self.pictograph.arrows.remove(self.ghost_arrow)
        self.pictograph.clearSelection()

        self.placed_arrow.ghost_arrow = self.ghost_arrow
        self.placed_arrow.update_appearance()
        self.placed_arrow.show()

        self.placed_arrow.setSelected(True)

    ### UPDATERS ###

    def _update_arrow_preview_for_new_location(self, new_location: Locations) -> None:
        self.previous_drag_location = new_location
        self.arrow_location = new_location
        (
            self.start_location,
            self.end_location,
        ) = get_start_end_locations(
            self.motion_type, self.rotation_direction, self.arrow_location
        )

        self._update_ghost_arrow_for_new_location(new_location)
        self.update_rotation()
        self.update_hand_during_drag()

        self.pictograph.add_motion(
            self.ghost_arrow,
            self.ghost_arrow.hand,
            self.motion_type,
            IN,
            1,
        )
        self.ghost_arrow.update_ghost_arrow(self.attributes)
        self.pictograph.update_pictograph()

    def _update_ghost_arrow_for_new_location(self, new_location) -> None:
        self.ghost_arrow.color = self.color
        self.ghost_arrow.arrow_location = new_location
        self.ghost_arrow.motion_type = self.motion_type
        self.ghost_arrow.rotation_direction = self.rotation_direction

        self.ghost_arrow.is_svg_mirrored = self.is_svg_mirrored

        ghost_svg = self.ghost_arrow.get_svg_file(self.motion_type)
        self.ghost_arrow.update_mirror()
        self.ghost_arrow.update_svg(ghost_svg)
        if self.ghost_arrow not in self.pictograph.arrows:
            self.pictograph.arrows.append(self.ghost_arrow)
        if self.ghost_arrow not in self.pictograph.items():
            self.pictograph.addItem(self.ghost_arrow)

    ### EVENT HANDLERS ###

    def handle_mouse_move(self, event_pos: QPoint) -> None:
        if self.preview:
            self.move_to_cursor(event_pos)
            if self.is_over_pictograph(event_pos):
                if not self.has_entered_pictograph_once:
                    self.remove_same_color_objects()
                    self.has_entered_pictograph_once = True

                pos_in_main_window = self.arrowbox.view.mapToGlobal(event_pos)
                view_pos_in_pictograph = self.pictograph.view.mapFromGlobal(
                    pos_in_main_window
                )
                scene_pos = self.pictograph.view.mapToScene(view_pos_in_pictograph)
                new_location = self.pictograph.get_closest_box_point(scene_pos)

                if self.previous_drag_location != new_location:
                    self._update_arrow_preview_for_new_location(new_location)

    def handle_mouse_release(self) -> None:
        if self.has_entered_pictograph_once:
            self.place_arrow_on_pictograph()
        self.deleteLater()
        self.pictograph.update_pictograph()
        self.arrowbox.drag = None
        self.ghost_arrow.hand = None
        self.reset_drag_state()
        self.previous_drag_location = None

    ### FLAGS ###

    def is_over_pictograph(self, event_pos: QPoint) -> bool:
        pos_in_main_window = self.arrowbox.view.mapToGlobal(event_pos)
        local_pos_in_pictograph = self.pictograph.view.mapFromGlobal(pos_in_main_window)
        return self.pictograph.view.rect().contains(local_pos_in_pictograph)

    ### UPDATERS ###

    def update_hand_during_drag(self) -> None:
        for hand in self.pictograph.hand_set.values():
            if hand.color == self.color:
                if hand not in self.pictograph.hands:
                    self.pictograph.hands.append(hand)

                hand.set_attributes_from_dict(
                    {
                        COLOR: self.color,
                        HAND_LOCATION: self.end_location,
                        LAYER: 1,
                    }
                )
                hand.arrow = self.ghost_arrow
                self.ghost_arrow.hand = hand

                if hand not in self.pictograph.items():
                    self.pictograph.addItem(hand)
                hand.show()
                hand.update_appearance()
                self.pictograph.update_hands()

    def apply_transformations_to_preview(self) -> None:
        self.update_mirror()
        self.update_rotation()

    def update_mirror(self) -> None:
        if self.is_svg_mirrored:
            transform = QTransform().scale(-1, 1)
            mirrored_pixmap = self.preview.pixmap().transformed(
                transform, Qt.TransformationMode.SmoothTransformation
            )
            self.preview.setPixmap(mirrored_pixmap)
            self.is_svg_mirrored = True

    def update_rotation(self) -> None:
        renderer = QSvgRenderer(self.target_arrow.svg_file)
        scaled_size = renderer.defaultSize() * self.pictograph.view.view_scale
        pixmap = QPixmap(scaled_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        with painter as painter:
            renderer.render(painter)

        angle = self._get_arrow_drag_rotation_angle(self)

        unrotate_transform = QTransform().rotate(-self.target_arrow_rotation_angle)
        unrotated_pixmap = self.preview.pixmap().transformed(unrotate_transform)

        rotate_transform = QTransform().rotate(angle)
        rotated_pixmap = unrotated_pixmap.transformed(rotate_transform)

        self.target_arrow_rotation_angle = angle
        self.preview.setPixmap(rotated_pixmap)

        (
            self.start_location,
            self.end_location,
        ) = get_start_end_locations(
            self.motion_type,
            self.rotation_direction,
            self.arrow_location,
        )

    def _get_arrow_drag_rotation_angle(
        self, arrow: Arrow | ObjectBoxDrag
    ) -> RotationAngles:
        """
        Calculate the rotation angle for the given arrow based on its motion type, rotation direction, color, and location.
        Takes either the target arrow when setting the pixmap, or the drag widget itself when updating rotation.

        Parameters:
        arrow (Arrow): The arrow object for which to calculate the rotation angle.

        Returns:
        RotationAngles: The calculated rotation angle for the arrow.
        """
        motion_type, rotation_direction, color, location = (
            arrow.motion.motion_type,
            arrow.rotation_direction,
            arrow.color,
            arrow.arrow_location,
        )

        rotation_angle_map: Dict[
            Tuple[MotionTypes, Colors],
            Dict[RotationDirections, Dict[Locations, RotationAngles]],
        ] = {
            (PRO, RED): {
                CLOCKWISE: {
                    NORTHEAST: 0,
                    SOUTHEAST: 90,
                    SOUTHWEST: 180,
                    NORTHWEST: 270,
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: 90,
                    SOUTHEAST: 180,
                    SOUTHWEST: 270,
                    NORTHWEST: 0,
                },
            },
            (PRO, BLUE): {
                CLOCKWISE: {
                    NORTHEAST: 0,
                    SOUTHEAST: 90,
                    SOUTHWEST: 180,
                    NORTHWEST: 270,
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: 90,
                    SOUTHEAST: 180,
                    SOUTHWEST: 270,
                    NORTHWEST: 0,
                },
            },
            (ANTI, RED): {
                CLOCKWISE: {
                    NORTHEAST: 90,
                    SOUTHEAST: 180,
                    SOUTHWEST: 270,
                    NORTHWEST: 0,
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: 0,
                    SOUTHEAST: 90,
                    SOUTHWEST: 180,
                    NORTHWEST: 270,
                },
            },
            (ANTI, BLUE): {
                CLOCKWISE: {
                    NORTHEAST: 90,
                    SOUTHEAST: 180,
                    SOUTHWEST: 270,
                    NORTHWEST: 0,
                },
                COUNTER_CLOCKWISE: {
                    NORTHEAST: 0,
                    SOUTHEAST: 90,
                    SOUTHWEST: 180,
                    NORTHWEST: 270,
                },
            },
        }

        direction_map: Dict[
            RotationDirections, Dict[Locations, RotationAngles]
        ] = rotation_angle_map.get((motion_type, color), {})
        location_map: Dict[Locations, RotationAngles] = direction_map.get(
            rotation_direction, {}
        )
        rotation_angle: RotationAngles = location_map.get(location, 0)

        return rotation_angle
