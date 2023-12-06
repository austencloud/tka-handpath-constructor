from PyQt6.QtWidgets import QVBoxLayout, QGraphicsSceneMouseEvent
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from objects.hand import Hand

from widgets.graph_editor.object_panel.handbox.handbox_drag import HandBoxDrag
from widgets.graph_editor.object_panel.handbox.handbox_view import HandBoxView
from settings.string_constants import (
    NORTH,
    EAST,
    HAND_LOCATION,
    SOUTH,
    WEST,
    COLOR,
    RED,
    BLUE,
    LAYER,
    ORIENTATION,
    IN,
)

from objects.grid import Grid
from widgets.graph_editor.object_panel.objectbox import ObjectBox
from utilities.TypeChecking.TypeChecking import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from widgets.main_widget import MainWidget
    from widgets.graph_editor.pictograph.pictograph import Pictograph


class Handbox(ObjectBox):
    def __init__(self, main_widget: "MainWidget", pictograph: "Pictograph") -> None:
        super().__init__(main_widget, pictograph)
        self.main_widget = main_widget
        self.main_window = main_widget.main_window
        self.view = HandBoxView(self)
        self.pictograph = pictograph
        self.grid = Grid("resources/images/grid/grid.svg")
        self.grid_position = QPointF(0, 0)
        self.grid.setPos(self.grid_position)
        self.addItem(self.grid)
        self.hands: List[Hand] = []
        self.hand_type = None
        self.drag = None
        self.handbox_layout = QVBoxLayout()
        self.handbox_layout.addWidget(self.view)
        self.hands: List[Hand] = []
        self.populate_hands()

    def populate_hands(self) -> None:
        self.clear_hands()
        initial_hand_attributes: List[Dict] = [
            {
                COLOR: RED,
                HAND_LOCATION: EAST,
            },
            {
                COLOR: BLUE,
                HAND_LOCATION: WEST,
            },
        ]

        for attributes in initial_hand_attributes:
            hand = Hand(self.pictograph, attributes)
            hand.setFlag(QGraphicsSvgItem.GraphicsItemFlag.ItemIsMovable, True)
            hand.setFlag(QGraphicsSvgItem.GraphicsItemFlag.ItemIsSelectable, True)
            self.set_hand_position(hand)
            self.addItem(hand)
            self.hands.append(hand)

    def clear_hands(self) -> None:
        for hand in self.hands:
            self.removeItem(hand)
        self.hands.clear()

    def set_hand_position(self, hand: Hand) -> None:
        handpoint = self.grid.get_circle_coordinates(f"{hand.hand_location}_hand_point")
        hand_length = hand.boundingRect().width()
        hand_width = hand.boundingRect().height()
        offset_x = -hand_length / 2
        offset_y = -hand_width / 2
        hand_position = handpoint + QPointF(offset_x, offset_y)
        hand.setPos(hand_position)
        hand.update_appearance()
        hand.setTransformOriginPoint(hand.boundingRect().center())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        scene_pos = event.scenePos()
        event_pos = self.view.mapFromScene(scene_pos)

        closest_hand = None
        min_distance = float("inf")
        for hand in self.hands:
            hand_center = hand.sceneBoundingRect().center()
            distance = (scene_pos - hand_center).manhattanLength()
            if distance < min_distance:
                closest_hand = hand
                min_distance = distance

        if closest_hand:
            self.target_hand = closest_hand
            if not self.drag:
                pictograph = self.main_widget.graph_editor.pictograph
                self.drag = HandBoxDrag(self.main_window, pictograph, self)
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag.match_target_hand(self.target_hand)
                self.drag.start_drag(event_pos)
        else:
            self.target_hand = None
            event.ignore()

    def mouseMoveEvent(self, event) -> None:
        if self.target_hand and self.drag:
            scene_pos = event.scenePos()
            event_pos = self.view.mapFromScene(scene_pos)
            self.drag.handle_mouse_move(event_pos)
        else:
            cursor_pos = event.scenePos()
            closest_hand = None
            min_distance = float("inf")

            for hand in self.hands:
                hand_center = hand.sceneBoundingRect().center()
                distance = (
                    cursor_pos - hand_center
                ).manhattanLength()  # Manhattan distance for simplicity

                if distance < min_distance:
                    closest_hand = hand
                    min_distance = distance

            for hand in self.hands:
                if hand != closest_hand:
                    hand.is_dim(True)  # Highlight all hands except the closest one
                else:
                    hand.is_dim(False)  # Do not highlight the closest one

    def mouseReleaseEvent(self, event) -> None:
        if self.target_hand and self.drag:
            scene_pos = event.scenePos()
            event_pos = self.view.mapFromScene(scene_pos)
            self.drag.handle_mouse_release()
            self.target_hand = None
        else:
            event.ignore()
