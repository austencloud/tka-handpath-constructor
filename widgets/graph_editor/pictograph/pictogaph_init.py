from typing import TYPE_CHECKING, Dict, Tuple

from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import QPointF

from objects.ghosts.ghost_arrow import GhostArrow
from objects.ghosts.ghost_hand import GhostHand
from objects.grid import Grid
from objects.letter_item import LetterItem
from objects.hand import Hand
from objects.motion import Motion
from settings.string_constants import (
    ARROW_LOCATION,
    BLUE,
    COLOR,
    EAST,
    END_LOCATION,
    MOTION_TYPE,
    NORTH,
    NORTHEAST,
    NORTHWEST,
    RED,
    SHIFT,
    SOUTH,
    SOUTHEAST,
    SOUTHWEST,
    START_LOCATION,
    WEST,
    HAND_LOCATION,
)
from utilities.TypeChecking.TypeChecking import Colors
from widgets.graph_editor.pictograph.pictograph_view import PictographView

if TYPE_CHECKING:
    from widgets.graph_editor.pictograph.pictograph import Pictograph


class PictographInit:
    def __init__(self, pictograph: "Pictograph") -> None:
        self.pictograph = pictograph
        self.main_widget = pictograph.main_widget
        self.window_width = pictograph.main_widget.main_window.main_window_width
        self.window_height = pictograph.main_widget.main_window.main_window_height

    def init_view(self) -> QGraphicsView:
        view = PictographView(self.pictograph)
        return view

    def init_grid(self) -> Grid:
        grid = Grid("resources/images/grid/grid.svg")
        grid_position = QPointF(0, 0)
        grid.setPos(grid_position)
        self.pictograph.addItem(grid)
        grid.init_center()
        grid.init_handpoints()
        grid.init_layer2_points()
        self.pictograph.grid = grid
        return grid

    def init_hand_set(self) -> Dict[Colors, Hand]:
        red_hand_dict = {COLOR: RED, HAND_LOCATION: NORTH}
        blue_hand_dict = {COLOR: BLUE, HAND_LOCATION: SOUTH}

        red_hand = Hand(self.pictograph, red_hand_dict)
        blue_hand = Hand(self.pictograph, blue_hand_dict)

        red_hand.set_svg_color(RED)
        blue_hand.set_svg_color(BLUE)

        hand_set = {RED: red_hand, BLUE: blue_hand}
        return hand_set

    def init_ghost_arrows(self) -> dict[str, GhostArrow]:
        default_red_ghost_arrow_attributes = {
            COLOR: RED,
            ARROW_LOCATION: NORTHEAST,
            START_LOCATION: NORTH,
            END_LOCATION: EAST,
        }

        default_blue_ghost_arrow_attributes = {
            COLOR: BLUE,
            ARROW_LOCATION: SOUTHWEST,
            START_LOCATION: SOUTH,
            END_LOCATION: WEST,
        }

        red_ghost_arrow = GhostArrow(
            self.pictograph, default_red_ghost_arrow_attributes
        )
        blue_ghost_arrow = GhostArrow(
            self.pictograph, default_blue_ghost_arrow_attributes
        )

        ghost_arrows = {RED: red_ghost_arrow, BLUE: blue_ghost_arrow}
        return ghost_arrows

    def init_motion_set(self) -> dict[str, dict[str, dict[str, dict[str, str]]]]:
        red_motion_attributes = {
            COLOR: RED,
            MOTION_TYPE: SHIFT,
            ARROW_LOCATION: NORTHEAST,
            START_LOCATION: NORTH,
            END_LOCATION: EAST,
        }
        red_motion = Motion(self.pictograph, self.pictograph.ghost_arrows[RED], None, red_motion_attributes)
        self.pictograph.ghost_arrows[RED].motion = red_motion
        self.pictograph.ghost_arrows[RED].setup_svg_file()
        self.pictograph.ghost_arrows[RED].setup_attributes(red_motion_attributes)
        blue_motion_attributes = {
            COLOR: BLUE,
            MOTION_TYPE: SHIFT,
            ARROW_LOCATION: SOUTHWEST,
            START_LOCATION: SOUTH,
            END_LOCATION: WEST,
        }
        blue_motion = Motion(self.pictograph, self.pictograph.ghost_arrows[BLUE], None, blue_motion_attributes)
        self.pictograph.ghost_arrows[BLUE].motion = blue_motion
        self.pictograph.ghost_arrows[BLUE].setup_svg_file()
        self.pictograph.ghost_arrows[BLUE].setup_attributes(blue_motion_attributes)
        
        motion_set = {RED: red_motion, BLUE: blue_motion}
        return motion_set
    
    def init_ghost_hands(self) -> dict[str, GhostHand]:
        default_red_ghost_hand_attributes = {
            COLOR: RED,
            HAND_LOCATION: EAST,
        }

        default_blue_ghost_hand_attributes = {
            COLOR: BLUE,
            HAND_LOCATION: WEST,
        }

        red_ghost_hand = GhostHand(self.pictograph, default_red_ghost_hand_attributes)
        blue_ghost_hand = GhostHand(self.pictograph, default_blue_ghost_hand_attributes)

        ghost_hands = {RED: red_ghost_hand, BLUE: blue_ghost_hand}
        return ghost_hands

    def init_letter_item(self) -> QGraphicsSvgItem:
        letter_item = LetterItem(self.pictograph)
        self.pictograph.addItem(letter_item)
        letter_item.position_letter_item(letter_item)
        return letter_item

    def init_locations(self, grid: Grid) -> dict[str, Tuple[int, int, int, int]]:
        grid_center = grid.get_circle_coordinates("center_point").toPoint()

        grid_center_x = grid_center.x()
        grid_center_y = grid_center.y()

        ne_boundary = (
            grid_center_x,
            0,
            self.pictograph.width(),
            grid_center_y,
        )
        se_boundary = (
            grid_center_x,
            grid_center_y,
            self.pictograph.width(),
            self.pictograph.height(),
        )
        sw_boundary = (0, grid_center_y, grid_center_x, self.pictograph.height())
        nw_boundary = (
            0,
            0,
            grid_center_x,
            grid_center_y,
        )
        locations = {
            NORTHEAST: ne_boundary,
            SOUTHEAST: se_boundary,
            SOUTHWEST: sw_boundary,
            NORTHWEST: nw_boundary,
        }
        return locations
