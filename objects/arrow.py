from typing import List
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QTransform
from data.start_end_location_map import get_start_end_locations
from objects.hand import Hand
from settings.string_constants import (
    DASH,
    MOTION_TYPE,
    COLOR,
    COUNTER_CLOCKWISE,
    CLOCKWISE,
    SHIFT,
    STATIC,
    NORTHEAST,
    SOUTHEAST,
    SOUTHWEST,
    NORTHWEST,
    START_LOCATION,
    END_LOCATION,
    ARROW_ATTRIBUTES,
    ARROW_DIR,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    ARROW_LOCATION,
    HAND_LOCATION,
    RED,
    BLUE,
    NORTH,
    SOUTH,
    WEST,
    EAST,
)
from objects.graphical_object import GraphicalObject
from objects.motion import Motion
from utilities.TypeChecking.TypeChecking import (
    ArrowAttributesDicts,
    MotionAttributesDicts,
    MotionTypes,
    RotationAngles,
    Locations,
    Direction,
    TYPE_CHECKING,
    Optional,
    Dict,
    RotationDirections,
)

if TYPE_CHECKING:
    from widgets.graph_editor.pictograph.pictograph import Pictograph
    from objects.ghosts.ghost_arrow import GhostArrow
    from objects.hand import Hand
    from widgets.graph_editor.object_panel.arrowbox.arrowbox import ArrowBox


class Arrow(GraphicalObject):
    def __init__(self, scene, attributes) -> None:
        super().__init__(scene)
        self.setAcceptHoverEvents(True)
        self.hand: Hand = None
        self.motion: Motion = None

    def setup_svg_file(self) -> None:
        self.svg_file = f"{ARROW_DIR}{self.motion.motion_type}.svg"
        if self.svg_file:
            self.setup_svg_renderer(self.svg_file)

    ### SETUP ###

    def update_appearance(self) -> None:
        super().update_appearance()
        self.update_rotation()

    def update_svg(self, svg_file: str) -> None:
        self.setup_svg_renderer(svg_file)

    def get_motion_type(self) -> MotionTypes:
        directions = [
            NORTH,
            NORTHEAST,
            EAST,
            SOUTHEAST,
            SOUTH,
            SOUTHWEST,
            WEST,
            NORTHWEST,
        ]
        num_directions = len(directions)

        # Function to find the index of a direction
        def find_index(direction):
            return directions.index(direction)

        start_location = self.motion.start_location if self.motion else None
        end_location = self.motion.end_location if self.motion else None

        if start_location and end_location:
            if start_location == end_location:
                return STATIC

            start_index = find_index(start_location)
            end_index = find_index(end_location)

            # Calculate the index difference in the circular list
            index_diff = (end_index - start_index) % num_directions

            if index_diff == 1 or index_diff == num_directions - 1:
                return SHIFT  # Adjacent
            elif index_diff == num_directions // 2:
                return DASH  # Opposite

        return STATIC

    def setup_attributes(self, attributes: "MotionAttributesDicts") -> None:
        self.drag_offset = QPointF(0, 0)


        self.arrow_location: Locations = attributes[ARROW_LOCATION]
        self.is_svg_mirrored: bool = False

        self.center_x = self.boundingRect().width() / 2
        self.center_y = self.boundingRect().height() / 2

        if attributes:
            self.set_attributes_from_dict(attributes)
            self.update_appearance()
            self.attributes = attributes

        self.update_mirror()
        self.center = self.boundingRect().center()

    ### MOUSE EVENTS ###

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        self.setSelected(True)

        if hasattr(self, "ghost_arrow"):
            if self.ghost_arrow:
                self.update_ghost_on_click()
        if hasattr(self, "hand"):
            if self.hand:
                self.update_hand_on_click()

        self.scene.arrows.remove(self)
        self.scene.update_pictograph()
        self.scene.arrows.append(self)

        for item in self.scene.items():
            if item != self:
                item.setSelected(False)
        # Notify the pictograph scene about the selection change
        if self.scene:
            self.scene.update_attr_panel()

    def update_hand_on_click(self) -> None:
        self.hand.color = self.color
        self.hand.hand_location = self.motion.end_location
        self.hand.axis = self.hand.update_axis(self.motion.end_location)

    def update_ghost_on_click(self) -> None:
        from widgets.graph_editor.pictograph.pictograph import Pictograph

        if isinstance(self.scene, Pictograph):
            self.ghost_arrow: "GhostArrow" = self.scene.ghost_arrows[self.color]
            self.ghost_arrow.hand = self.hand
            self.ghost_arrow.set_attributes_from_dict(self.attributes)
            self.ghost_arrow.set_arrow_attrs_from_arrow(self)
            self.ghost_arrow.update_appearance()
            self.ghost_arrow.transform = self.transform
            self.scene.addItem(self.ghost_arrow)
            self.scene.arrows.append(self.ghost_arrow)

    def update_location(self, new_pos: QPointF) -> None:
        new_location = self.scene.get_closest_box_point(new_pos)

        self.arrow_location = new_location
        self.motion.arrow_location = new_location

        self.set_start_end_locations()

        self.ghost_arrow.set_arrow_attrs_from_arrow(self)
        self.ghost_arrow.update_appearance()

        self.hand.set_hand_attrs_from_arrow(self)
        self.hand.update_appearance()

        self.update_appearance()

        self.scene.arrows.remove(self)
        for hand in self.scene.hands:
            if hand.color == self.color:
                hand.arrow = self
                self.hand = hand
        self.scene.update_pictograph()
        self.scene.arrows.append(self)

    def set_drag_pos(self, new_pos: QPointF) -> None:
        self.setPos(new_pos)

    def mouseReleaseEvent(self, event) -> None:
        self.scene.removeItem(self.ghost_arrow)
        if self.ghost_arrow in self.scene.arrows:
            self.scene.arrows.remove(self.ghost_arrow)

        self.ghost_arrow.hand = None
        self.scene.update_pictograph()

    ### UPDATERS ###

    def update_mirror(self) -> None:
        if self.is_svg_mirrored:
            self.mirror()
        else:
            self.unmirror()

    def update_rotation(self) -> None:
        angle = self.get_arrow_rotation_angle()
        self.setRotation(angle)

    def set_start_end_locations(self) -> None:
        (
            self.motion.start_location,
            self.motion.end_location,
        ) = get_start_end_locations(
            self.motion_type, self.rotation_direction, self.arrow_location
        )
        self.motion.start_location = self.motion.start_location
        self.motion.end_location = self.motion.end_location

    def set_arrow_attrs_from_arrow(self, target_arrow: "Arrow") -> None:
        self.color = target_arrow.color
        self.motion_type = target_arrow.motion_type
        self.arrow_location = target_arrow.arrow_location
        self.rotation_direction = target_arrow.rotation_direction
        self.motion.start_location = target_arrow.motion.start_location
        self.motion.end_location = target_arrow.motion.end_location

        self.motion.color = target_arrow.color
        self.motion.motion_type = target_arrow.motion_type
        self.motion.arrow_location = target_arrow.arrow_location
        self.motion.rotation_direction = target_arrow.rotation_direction
        self.motion.start_location = target_arrow.motion.start_location
        self.motion.end_location = target_arrow.motion.end_location

    def update_hand_during_drag(self) -> None:
        for hand in self.scene.hand_set.values():
            if hand.color == self.color:
                if hand not in self.scene.hands:
                    self.scene.hands.append(hand)

                hand.set_attributes_from_dict(
                    {
                        COLOR: self.color,
                        HAND_LOCATION: self.motion.end_location,
                    }
                )
                hand.arrow = self.ghost_arrow

                if hand not in self.scene.items():
                    self.scene.addItem(hand)
                hand.show()
                hand.update_appearance()
                self.scene.update_pictograph()

    def set_arrow_transform_origin_to_center(self) -> None:
        self.center = self.boundingRect().center()
        self.setTransformOriginPoint(self.center)

    ### GETTERS ###

    def get_svg_data(self, svg_file: str) -> bytes:
        with open(svg_file, "r") as f:
            svg_data = f.read()
        return svg_data.encode("utf-8")

    def get_arrow_rotation_angle(
        self, arrow: Optional["Arrow"] = None
    ) -> RotationAngles:
        arrow = arrow or self
        location_to_angle = self.get_location_to_angle_map(
            arrow.motion.motion_type
        )
        return location_to_angle.get(self.arrow_location, 0)

    def get_location_to_angle_map(
        self, motion_type: MotionTypes
    ) -> Dict[str, Dict[str, int]]:
        if motion_type == SHIFT:
            return {
                    NORTHEAST: 0,
                    SOUTHEAST: 90,
                    SOUTHWEST: 180,
                    NORTHWEST: 270,
                },

    def get_attributes(self) -> ArrowAttributesDicts:
        return {attr: getattr(self, attr) for attr in ARROW_ATTRIBUTES}

    ### MANIPULATION ###

    def move_wasd(self, direction: Direction) -> None:
        wasd_location_map = {
            UP: {SOUTHEAST: NORTHEAST, SOUTHWEST: NORTHWEST},
            LEFT: {NORTHEAST: NORTHWEST, SOUTHEAST: SOUTHWEST},
            DOWN: {NORTHEAST: SOUTHEAST, NORTHWEST: SOUTHWEST},
            RIGHT: {NORTHWEST: NORTHEAST, SOUTHWEST: SOUTHEAST},
        }
        current_location = self.arrow_location
        new_location = wasd_location_map.get(direction, {}).get(
            current_location, current_location
        )
        self.arrow_location = new_location
        self.motion.arrow_location = new_location
        (
            new_start_location,
            new_end_location,
        ) = get_start_end_locations(
            self.motion_type, self.rotation_direction, new_location
        )

        updated_arrow_dict = {
            COLOR: self.color,
            MOTION_TYPE: self.motion_type,
            ARROW_LOCATION: new_location,
            START_LOCATION: new_start_location,
            END_LOCATION: new_end_location,
        }

        self.update_attributes(updated_arrow_dict)
        self.hand.hand_location = new_end_location
        self.hand.update_appearance()
        self.motion.update_attr_from_arrow()

        self.scene.update_pictograph()

    def rotate_arrow(self, rotation_direction: RotationDirections) -> None:
        diamond_mode_locations = [NORTH, EAST, SOUTH, WEST]
        box_mode_locations = [NORTHEAST, SOUTHEAST, SOUTHWEST, NORTHWEST]

        if isinstance(self, StaticArrow):
            self.rotate_diamond_mode_static_arrow(
                rotation_direction, diamond_mode_locations
            )
        else:
            self.rotate_diamond_mode_shift(rotation_direction, box_mode_locations)

    def rotate_diamond_mode_shift(
        self, rotation_direction, box_mode_locations: List[Locations]
    ) -> None:
        current_location_index = box_mode_locations.index(self.arrow_location)
        new_location_index = (
            (current_location_index + 1) % 4
            if rotation_direction == CLOCKWISE
            else (current_location_index - 1) % 4
        )

        new_arrow_location = box_mode_locations[new_location_index]
        (
            new_start_location,
            new_end_location,
        ) = get_start_end_locations(self.motion_type, new_arrow_location)

        self.motion.arrow_location = new_arrow_location
        self.motion.start_location = new_start_location
        self.motion.end_location = new_end_location

        self.arrow_location = new_arrow_location
        self.motion.start_location = new_start_location
        self.motion.end_location = new_end_location
        self.hand.hand_location = new_end_location

        self.update_appearance()
        self.hand.update_appearance()
        self.scene.update_pictograph()

    def rotate_diamond_mode_static_arrow(
        self, rotation_direction, diamond_mode_locations: List[Locations]
    ):
        current_location_index = diamond_mode_locations.index(self.arrow_location)
        new_location_index = (
            (current_location_index + 1) % 4
            if rotation_direction == CLOCKWISE
            else (current_location_index - 1) % 4
        )
        new_location = diamond_mode_locations[new_location_index]
        self.motion.arrow_location = new_location
        self.motion.start_location = new_location
        self.motion.end_location = new_location
        self.arrow_location = new_location
        self.motion.start_location = new_location
        self.motion.end_location = new_location
        self.hand.hand_location = new_location

        self.motion.update_attr_from_arrow()
        self.hand.update_appearance()
        self.scene.update_pictograph()

    def swap_color(self) -> None:
        if self.color == RED:
            new_color = BLUE
        elif self.color == BLUE:
            new_color = RED

        self.color = new_color
        self.update_appearance()

        self.hand.color = new_color
        self.hand.update_appearance()

        self.scene.update_pictograph()

    def swap_rot_dir(self) -> None:
        pass

        if self.is_svg_mirrored:
            self.unmirror()
        elif not self.is_svg_mirrored:
            self.mirror()

        old_start_location = self.motion.start_location
        old_end_location = self.motion.end_location
        new_start_location = old_end_location
        new_end_location = old_start_location

        svg_file = self.get_svg_file(self.motion_type)
        self.update_svg(svg_file)

        self.motion.start_location: Locations = new_start_location
        self.motion.end_location: Locations = new_end_location

        self.hand.color = self.color
        self.hand.hand_location = new_end_location

        self.update_appearance()
        self.hand.update_appearance()
        if hasattr(self, "ghost_arrow"):
            if not isinstance(self, self.ghost_arrow.__class__) and self.ghost_arrow:
                self.ghost_arrow.is_svg_mirrored = self.is_svg_mirrored
                self.ghost_arrow.update_attributes(self.attributes)
        self.scene.update_pictograph()

    def mirror(self) -> None:
        transform = QTransform()
        transform.translate(self.center_x, self.center_y)
        transform.scale(-1, 1)
        transform.translate(-self.center_x, -self.center_y)
        self.setTransform(transform)
        if hasattr(self, "ghost_arrow"):
            self.ghost_arrow.setTransform(transform)
            self.ghost_arrow.is_svg_mirrored = True
        self.is_svg_mirrored = True

    def unmirror(self) -> None:
        transform = QTransform()
        transform.translate(self.center.x(), self.center.y())
        transform.scale(1, 1)
        transform.translate(-self.center.x(), -self.center.y())
        self.setTransform(transform)
        if hasattr(self, "ghost_arrow"):
            self.ghost_arrow.setTransform(transform)
            self.ghost_arrow.is_svg_mirrored = False
        self.is_svg_mirrored = False

    def delete(self, keep_hand: bool = False) -> None:
        self.scene.removeItem(self)
        if self in self.scene.arrows:
            self.scene.arrows.remove(self)
            self.scene.motions.remove(self.motion)
            self.pictograph.graph_editor.attr_panel.update_panel(self.color)
        if keep_hand:
            self.hand._create_static_arrow()
        else:
            self.hand.delete()

        self.scene.update_pictograph()


class StaticArrow(Arrow):
    def __init__(self, pictograph, attributes) -> None:
        super().__init__(pictograph, attributes)
        self._disable_interactivity()
        self.hide()

    def _disable_interactivity(self) -> None:
        self.setFlag(QGraphicsSvgItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsSvgItem.GraphicsItemFlag.ItemIsMovable, False)
