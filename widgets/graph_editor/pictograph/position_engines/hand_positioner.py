from PyQt6.QtCore import QPointF
import math
from settings.numerical_constants import BETA_OFFSET
from settings.string_constants import (
    COLOR,
    MOTION_TYPE,
    SHIFT,
    STATIC,
    START_LOCATION,
    END_LOCATION,
    NORTH,
    SOUTH,
    EAST,
    WEST,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    RED,
    BLUE,
)
from typing import TYPE_CHECKING, Dict, List
from objects.hand import Hand
from utilities.TypeChecking.TypeChecking import (
    ArrowAttributesDicts,
    MotionAttributesDicts,
    LetterDictionary,
    Direction,
    Locations,
)

if TYPE_CHECKING:
    from widgets.graph_editor.pictograph.pictograph import Pictograph


class HandPositioner:
    current_state: List[MotionAttributesDicts]
    matching_letters: List[LetterDictionary]
    arrow_dict: List[MotionAttributesDicts]
    letters: LetterDictionary

    def __init__(self, pictograph: "Pictograph") -> None:
        self.pictograph = pictograph
        self.view = pictograph.view
        self.letters = pictograph.letters

    def update_hand_positions(self) -> None:
        for hand in self.pictograph.hands:
            self.set_default_hand_locations(hand)
        if self.hands_in_beta():
            self.reposition_beta_hands()

    def set_default_hand_locations(self, hand: "Hand") -> None:
        hand.setTransformOriginPoint(0, 0)
        hand_height = hand.boundingRect().height()
        hand_width = hand.boundingRect().width()
        hand.setPos(
            self.pictograph.grid.handpoints[hand.hand_location]
            + QPointF(-hand_width / 2, -hand_height / 2)
        )

    def reposition_beta_hands(self) -> None:
        board_state = self.pictograph.get_state()

        def move_hand(hand: Hand, direction) -> None:
            new_position = self.calculate_new_position(hand.pos(), direction)
            hand.setPos(new_position)

        motions_grouped_by_start_loc: Dict[Locations, List[MotionAttributesDicts]] = {}
        for motion in board_state:
            motions_grouped_by_start_loc.setdefault(motion[START_LOCATION], []).append(
                motion
            )

        pro_or_anti_motions = [
            motion for motion in board_state if motion[MOTION_TYPE] == SHIFT
        ]
        static_motions = [
            motion for motion in board_state if motion[MOTION_TYPE] == STATIC
        ]

        # STATIC BETA
        if len(static_motions) > 1:
            self.reposition_static_beta(move_hand, static_motions)

    ### STATIC BETA ### β

    def reposition_static_beta(
        self, move_hand: callable, static_motions: List[MotionAttributesDicts]
    ) -> None:
        for motion in static_motions:
            hand = next(
                (s for s in self.pictograph.hands if s.arrow.color == motion[COLOR]),
                None,
            )
            if not hand:
                continue

            end_location = motion[END_LOCATION]
            layer_reposition_map = {
                
                    (NORTH, RED): RIGHT,
                    (NORTH, BLUE): LEFT,
                    (SOUTH, RED): RIGHT,
                    (SOUTH, BLUE): LEFT,
                    (EAST, RED): (UP, DOWN) if end_location == EAST else None,
                    (WEST, BLUE): (UP, DOWN) if end_location == WEST else None,
                

            }

            direction: Direction = layer_reposition_map[hand.layer].get(
                (hand.hand_location, motion[COLOR]), None
            )

            if direction:
                if isinstance(direction, str):
                    move_hand(hand, direction)
                elif isinstance(direction, tuple):
                    move_hand(hand, direction[0])
                    other_hand = next(
                        (
                            s
                            for s in self.pictograph.hands
                            if s.hand_location == hand.hand_location and s != hand
                        ),
                        None,
                    )
                    if other_hand:
                        move_hand(other_hand, direction[1])

    ### HELPERS ###

    def hands_in_beta(self) -> bool | None:
        visible_staves: List[Hand] = []
        for hand in self.pictograph.hands:
            if hand.isVisible():
                visible_staves.append(hand)
        if len(visible_staves) == 2:
            if visible_staves[0].hand_location == visible_staves[1].hand_location:
                return True
            else:
                return False

    def calculate_new_position(
        self,
        current_position: QPointF,
        direction: Direction,
    ) -> QPointF:
        offset = (
            QPointF(BETA_OFFSET, 0)
            if direction in [LEFT, RIGHT]
            else QPointF(0, BETA_OFFSET)
        )
        if direction in [RIGHT, DOWN]:
            return current_position + offset
        else:
            return current_position - offset

    ### GETTERS

    def get_opposite_direction(self, movement: Direction) -> Direction:
        if movement == LEFT:
            return RIGHT
        elif movement == RIGHT:
            return LEFT
