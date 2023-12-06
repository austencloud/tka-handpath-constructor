from data.start_end_location_map import get_start_end_locations
from objects.graphical_object import GraphicalObject
from PyQt6.QtCore import QPointF
from settings.string_constants import *
import re

from PyQt6.QtWidgets import QGraphicsSceneMouseEvent
from utilities.TypeChecking.TypeChecking import (
    HandAttributesDicts,
    Locations,
    Locations,
    RotationDirections,
    MotionTypes,
    Colors,
    Dict,
    Tuple,
    ColorsHex,
)
from typing import TYPE_CHECKING, Dict, Tuple

if TYPE_CHECKING:
    from objects.arrow import Arrow
    from widgets.graph_editor.pictograph.pictograph import Pictograph
    from objects.motion import Motion
    from widgets.graph_editor.object_panel.handbox.handbox import Handbox
    from objects.arrow import StaticArrow


class Hand(GraphicalObject):
    def __init__(self, scene, attributes: Dict) -> None:
        super().__init__(scene)
        self._setup_attributes(scene, attributes)
        self.update_appearance()

    def _setup_attributes(self, scene, attributes: "HandAttributesDicts") -> None:
        self.scene: Pictograph | Handbox = scene
        self.motion: Motion = None

        self.drag_offset = QPointF(0, 0)
        self.previous_location: Locations = None
        self.arrow: Arrow = None
        self.static_arrow: StaticArrow = None
        self.ghost_hand: Hand = None
        self.color: Colors = attributes[COLOR]
        self.hand_location: Locations = attributes[HAND_LOCATION]

        self.side = "left" if self.color == "blue" else "right"
        self.svg_file = f"resources/images/hands/{self.side}_hand.svg"

        self.center = self.boundingRect().center()
        if attributes:
            self.setup_svg_renderer(self.svg_file)
            self.update_attributes(attributes)

    ### MOUSE EVENTS ###

    def mousePressEvent(self, event) -> None:
        self.setSelected(True)
        if isinstance(self.scene, self.scene.__class__):
            if not self.ghost_hand:
                self.ghost_hand = self.scene.ghost_hands[self.color]
            self.ghost_hand.color = self.color
            self.ghost_hand.hand_location = self.hand_location
            self.ghost_hand.layer = self.layer
            self.ghost_hand.update_appearance()
            self.scene.addItem(self.ghost_hand)
            self.ghost_hand.arrow = self.arrow
            self.scene.hands.append(self.ghost_hand)
            self.scene.hands.remove(self)
            self.scene.update_pictograph()
            self.scene.hands.append(self)
            for item in self.scene.items():
                if item != self:
                    item.setSelected(False)
            self.previous_location = self.hand_location

    def update_location(self, new_pos: QPointF) -> None:
        new_location = self.get_closest_diamond_point(new_pos)

        if new_location != self.previous_location:
            self.hand_location = new_location
            from objects.arrow import StaticArrow

            if isinstance(self.arrow, StaticArrow):
                self.arrow.motion.start_location = new_location
                self.arrow.motion.end_location = new_location
                self.motion.arrow_location = new_location
                self.motion.start_location = new_location
                self.motion.end_location = new_location
            self.update_appearance()
            self.update_arrow_location(new_location)

            (
                self.ghost_hand.arrow.motion.end_location,
                self.ghost_hand.arrow.motion.start_location,
            ) = (
                new_location,
                new_location,
            )
            self.ghost_hand.color = self.color
            self.ghost_hand.hand_location = self.hand_location
            self.ghost_hand.layer = self.layer
            self.ghost_hand.update_appearance()

            self.scene.hands.remove(self)
            if self.arrow.motion.motion_type == STATIC:
                self.arrow.motion.start_location = new_location
                self.arrow.motion.end_location = new_location

            self.scene.update_pictograph()
            self.scene.hands.append(self)
            new_pos = new_pos - self.get_object_center()
            self.setPos(new_pos)
            self.previous_location = new_location

    def update_arrow_location(self, new_location: Locations) -> None:
        if self.arrow.motion.motion_type == SHIFT:
            shift_location_map: Dict[
                Tuple(Locations, RotationDirections, MotionTypes),
                Dict[Locations, Locations],
            ] = (
                {
                    (NORTHEAST, CLOCKWISE): {NORTH: NORTHWEST, SOUTH: SOUTHEAST},
                    (NORTHWEST, CLOCKWISE): {EAST: NORTHEAST, WEST: SOUTHWEST},
                    (SOUTHWEST, CLOCKWISE): {NORTH: NORTHWEST, SOUTH: SOUTHEAST},
                    (SOUTHEAST, CLOCKWISE): {WEST: SOUTHWEST, EAST: NORTHEAST},
                    (NORTHEAST, COUNTER_CLOCKWISE): {WEST: NORTHWEST, EAST: SOUTHEAST},
                    (NORTHWEST, COUNTER_CLOCKWISE): {
                        SOUTH: SOUTHWEST,
                        NORTH: NORTHEAST,
                    },
                    (SOUTHWEST, COUNTER_CLOCKWISE): {EAST: SOUTHEAST, WEST: NORTHWEST},
                    (SOUTHEAST, COUNTER_CLOCKWISE): {
                        NORTH: NORTHEAST,
                        SOUTH: SOUTHWEST,
                    },
                    WEST: SOUTHWEST,
                },
            )

            current_location = self.arrow.arrow_location
            rotation_direction = self.arrow.rotation_direction
            motion_type = self.arrow.motion.motion_type
            new_location = shift_location_map.get(
                (current_location, rotation_direction, motion_type), {}
            ).get(new_location)

            if new_location:
                self.arrow.arrow_location = new_location
                start_location, end_location = get_start_end_locations(
                    motion_type, rotation_direction, new_location
                )
                self.arrow.motion.start_location = start_location
                self.arrow.motion.end_location = end_location
                self.arrow.update_appearance()
                self.arrow.motion.arrow_location = new_location
                self.arrow.motion.start_location = start_location
                self.arrow.motion.end_location = end_location
                self.pictograph.update_pictograph()

        elif self.arrow.motion.motion_type == STATIC:
            self.arrow.motion.arrow_location = new_location
            self.arrow.motion.start_location = new_location
            self.arrow.motion.end_location = new_location

            self.arrow.arrow_location = new_location
            self.arrow.motion.start_location = new_location
            self.arrow.motion.end_location = new_location
            self.arrow.update_appearance()

    def mouseReleaseEvent(self, event) -> None:
        if isinstance(self.scene, self.scene.__class__):
            self.scene.removeItem(self.ghost_hand)
            self.scene.hands.remove(self.ghost_hand)
            self.ghost_hand.arrow = None
            self.scene.update_pictograph()
            self.finalize_hand_drop(event)

    def finalize_hand_drop(self, event: "QGraphicsSceneMouseEvent") -> None:
        closest_handpoint = self.get_closest_handpoint(event.scenePos())
        new_location = self.get_closest_diamond_point(event.scenePos())

        self.hand_location = new_location
        self.axis = self.update_axis(self.hand_location)
        self.update_appearance()
        self.setPos(closest_handpoint)

        if self.arrow:
            self.arrow.update_appearance()
        self.previous_location = new_location
        self.scene.update_pictograph()

    def set_hand_transform_origin_to_center(self: "Hand") -> None:
        self.center = self.get_object_center()
        self.setTransformOriginPoint(self.center)

    def set_hand_attrs_from_arrow(self, target_arrow: "Arrow") -> None:
        self.color = target_arrow.color
        self.hand_location = target_arrow.motion.end_location
        self.update_appearance()

    def get_attributes(self) -> HandAttributesDicts:
        return {attr: getattr(self, attr) for attr in HAND_ATTRIBUTES}

    def get_closest_handpoint(self, mouse_pos: QPointF) -> QPointF:
        closest_distance = float("inf")
        closest_handpoint = None
        for point in self.scene.grid.handpoints.values():
            distance = (point - mouse_pos).manhattanLength()
            if distance < closest_distance:
                closest_distance = distance
                closest_handpoint = point
        return closest_handpoint

    def get_closest_diamond_point(self, mouse_pos: QPointF) -> Locations:
        closest_distance = float("inf")
        closest_location = None
        for location, point in self.scene.grid.handpoints.items():
            distance = (point - mouse_pos).manhattanLength()
            if distance < closest_distance:
                closest_distance = distance
                closest_location = location
        return closest_location

    ### HELPERS ###

    def swap_layer(self) -> None:
        if self.layer == 1:
            self.layer = 2
        else:
            self.layer = 1
        self.update_rotation()

    def set_svg_color(self, new_color: Colors) -> bytes:
        new_hex_color: ColorsHex = COLOR_MAP.get(new_color)

        with open(self.svg_file, "r") as f:
            svg_data = f.read()

        style_tag_pattern = re.compile(
            r"\.st0{fill\s*:\s*(#[a-fA-F0-9]{6})\s*;}", re.DOTALL
        )
        match = style_tag_pattern.search(svg_data)

        if match:
            old_hex_color: ColorsHex = match.group(1)
            svg_data = svg_data.replace(old_hex_color, new_hex_color)
        return svg_data.encode("utf-8")

    def delete(self) -> None:
        self.scene.removeItem(self)
        self.scene.hands.remove(self)
        self.scene.update_pictograph()

    def _create_static_arrow(self) -> None:
        static_arrow_dict = {
            COLOR: self.color,
            MOTION_TYPE: STATIC,
            ARROW_LOCATION: self.hand_location,
            START_LOCATION: self.hand_location,
            END_LOCATION: self.hand_location,
        }

        self.static_arrow = StaticArrow(self.pictograph, static_arrow_dict)
        self.static_arrow.update_svg(f"resources/images/arrows/{self.static_arrow.motion.motion_type}.svg")
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
