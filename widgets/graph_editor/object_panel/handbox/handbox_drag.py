from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QPixmap, QPainter, QTransform
from PyQt6.QtSvg import QSvgRenderer
from objects.hand import Hand
from objects.arrow import StaticArrow
from utilities.TypeChecking.TypeChecking import *
from typing import TYPE_CHECKING
from settings.string_constants import (
    IN,
    OUT,
    CLOCKWISE,
    COUNTER_CLOCKWISE,
    NORTH,
    SOUTH,
    WEST,
    EAST,
    COLOR,
    MOTION_TYPE,
    STATIC,
    ARROW_LOCATION,
    START_LOCATION,
    END_LOCATION,
    TURNS,
)
from widgets.graph_editor.object_panel.objectbox_drag import ObjectBoxDrag


if TYPE_CHECKING:
    from main import MainWindow
    from widgets.graph_editor.pictograph.pictograph import Pictograph
    from widgets.graph_editor.object_panel.handbox.handbox import Handbox


class HandBoxDrag(ObjectBoxDrag):
    def __init__(
        self, main_window: "MainWindow", pictograph: "Pictograph", handbox: "Handbox"
    ) -> None:
        super().__init__(main_window, pictograph, handbox)
        self.attributes: HandAttributesDicts = {}
        self.handbox = handbox
        self.objectbox = handbox
        self.static_arrow = None

    def match_target_hand(self, target_hand: "Hand") -> None:
        self.target_hand = target_hand
        self.static_arrow = target_hand.static_arrow
        super().match_target_object(target_hand)
        self.set_attributes(target_hand)

    def set_attributes(self, target_hand: "Hand") -> None:
        self.color: Colors = target_hand.color
        self.hand_location: Locations = target_hand.hand_location

        self.ghost_hand = self.pictograph.ghost_hands[self.color]
        self.ghost_hand.target_hand = target_hand

    def place_hand_on_pictograph(self) -> None:
        self.placed_hand = Hand(self.pictograph, self.ghost_hand.get_attributes())

        self.placed_hand.arrow = self.ghost_hand.arrow
        self.placed_hand.arrow.arrow_location = self.hand_location
        self.placed_hand.arrow.motion.start_location = self.hand_location
        self.placed_hand.arrow.motion.end_location = self.hand_location

        self.pictograph.add_motion(
            self.placed_hand.arrow,
            self.placed_hand,
            STATIC,
        )
        self.placed_hand.motion.arrow_location = self.hand_location
        self.placed_hand.motion.start_location = self.hand_location
        self.placed_hand.motion.end_location = self.hand_location

        self.ghost_hand.arrow.hand = self.placed_hand
        self.pictograph.addItem(self.placed_hand)
        self.pictograph.hands.append(self.placed_hand)

        self.pictograph.removeItem(self.ghost_hand)
        self.pictograph.hands.remove(self.ghost_hand)
        self.pictograph.update_pictograph()
        self.pictograph.clearSelection()

        self.placed_hand.ghost_hand = self.ghost_hand
        self.placed_hand.update_appearance()
        self.placed_hand.show()
        self.placed_hand.setSelected(True)

    ### UPDATERS ###

    def _update_hand_preview_for_new_location(self, new_location: Locations) -> None:
        self.hand_location = new_location

        self._update_ghost_hand_for_new_location(new_location)

        if not self.static_arrow:
            self._create_static_arrow()
        self._update_static_arrow()

        self.current_rotation_angle = self._get_hand_drag_rotation_angle(self)
        rotated_pixmap = self.create_pixmap_with_rotation(self.current_rotation_angle)

        if self.current_rotation_angle in [90, 270]:
            new_size = QSize(rotated_pixmap.width(), rotated_pixmap.height())
        else:
            new_size = rotated_pixmap.size()

        self.setFixedSize(new_size)
        self.preview.setFixedSize(new_size)
        self.preview.setPixmap(rotated_pixmap)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.ghost_hand not in self.pictograph.hands:
            self.pictograph.hands.append(self.ghost_hand)
        if self.ghost_hand not in self.pictograph.items():
            self.pictograph.addItem(self.ghost_hand)

        # remove the old motion from the pcitograph before adding the new one
        for motion in self.pictograph.motions[:]:
            if motion.color == self.color:
                self.pictograph.motions.remove(motion)

        self.pictograph.add_motion(
            self.ghost_hand.arrow, self.ghost_hand, STATIC, IN, 1
        )

        self.pictograph.update_pictograph()
        self.move_to_cursor(self.handbox.view.mapFromGlobal(self.pos()))

    def _update_ghost_hand_for_new_location(self, new_location) -> None:
        self.ghost_hand.color = self.color
        self.ghost_hand.hand_location = new_location

        self.ghost_hand.motion.arrow_location = self.hand_location
        self.ghost_hand.motion.start_location = self.hand_location
        self.ghost_hand.motion.end_location = self.hand_location

        self.ghost_hand.arrow = self.static_arrow
        self.ghost_hand.arrow.arrow_location = self.hand_location
        self.ghost_hand.arrow.motion.start_location = self.hand_location
        self.ghost_hand.arrow.motion.end_location = self.hand_location

        self.ghost_hand.update_color()

    ### EVENT HANDLERS ###

    def handle_mouse_move(self, event_pos: QPoint) -> None:
        if self.preview:
            self.move_to_cursor(event_pos)
            if self.is_over_pictograph(event_pos):
                if not self.has_entered_pictograph_once:
                    self.has_entered_pictograph_once = True
                    self.remove_same_color_objects()
                    self._create_static_arrow()
                    self.pictograph.add_motion(
                        self.ghost_hand.arrow,
                        self.ghost_hand,
                        STATIC,
                    )

                pos_in_main_window = self.handbox.view.mapToGlobal(event_pos)
                view_pos_in_pictograph = self.pictograph.view.mapFromGlobal(
                    pos_in_main_window
                )
                scene_pos = self.pictograph.view.mapToScene(view_pos_in_pictograph)
                new_location = self.pictograph.get_nearest_handpoint(scene_pos)

                if self.previous_drag_location != new_location and new_location:
                    self.previous_drag_location = new_location
                    self.ghost_hand.arrow.arrow_location = new_location
                    self.ghost_hand.arrow.motion.start_location = new_location
                    self.ghost_hand.arrow.motion.end_location = new_location
                    self.ghost_hand.motion.arrow_location = new_location
                    self.ghost_hand.motion.start_location = new_location
                    self.ghost_hand.motion.end_location = new_location
                    self._update_hand_preview_for_new_location(new_location)
                    self.ghost_hand.update_attributes(self.attributes)
                    self.pictograph.update_pictograph()

    def handle_mouse_release(self) -> None:
        if self.has_entered_pictograph_once:
            self.place_hand_on_pictograph()
        self.deleteLater()
        self.pictograph.update_pictograph()
        self.handbox.drag = None
        self.ghost_hand.arrow = None
        self.reset_drag_state()
        self.previous_drag_location = None

    ### HELPERS ###

    def is_over_pictograph(self, event_pos: QPoint) -> bool:
        pos_in_main_window = self.handbox.view.mapToGlobal(event_pos)
        local_pos_in_pictograph = self.pictograph.view.mapFromGlobal(pos_in_main_window)
        return self.pictograph.view.rect().contains(local_pos_in_pictograph)

    def create_pixmap_with_rotation(self, angle) -> QPixmap:
        # Generate a new pixmap based on target hand and apply the rotation
        new_svg_data = self.target_hand.set_svg_color(self.color)
        renderer = QSvgRenderer()
        renderer.load(new_svg_data)

        scaled_size = renderer.defaultSize() * self.pictograph.view.view_scale
        pixmap = QPixmap(scaled_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)

        renderer.render(painter)
        painter.end()
        rotate_transform = QTransform().rotate(angle)
        rotated_pixmap = pixmap.transformed(rotate_transform)

        return rotated_pixmap

    def _create_static_arrow(self) -> None:
        static_arrow_dict = {
            COLOR: self.color,
            MOTION_TYPE: STATIC,
            ARROW_LOCATION: self.hand_location,
            START_LOCATION: self.hand_location,
            END_LOCATION: self.hand_location,
            TURNS: 0,
        }

        self.static_arrow = StaticArrow(self.pictograph, static_arrow_dict)
        for arrow in self.pictograph.arrows[:]:
            if arrow.color == self.color:
                self.pictograph.removeItem(arrow)
                self.pictograph.arrows.remove(arrow)
        self.pictograph.addItem(self.static_arrow)
        self.pictograph.arrows.append(self.static_arrow)
        self.static_arrow.hand = self.ghost_hand
        self.static_arrow.hand.arrow = self.static_arrow

        if self.static_arrow not in self.pictograph.items():
            self.pictograph.addItem(self.static_arrow)

    def _update_static_arrow(self) -> None:
        self.static_arrow.color = self.color
        self.static_arrow.arrow_location = self.hand_location
        self.static_arrow.motion.start_location = self.hand_location
        self.static_arrow.motion.end_location = self.hand_location
        self.static_arrow.hand = self.ghost_hand
        self.static_arrow.hand.arrow = self.static_arrow
        self.static_arrow.update_appearance()
        self.pictograph.update_pictograph()
