from PyQt6.QtCore import QPointF
import math
from settings.numerical_constants import BETA_OFFSET
from settings.string_constants import (
    CLOCKWISE,
    COUNTER_CLOCKWISE,
    IN,
    OUT,
    COLOR,
    MOTION_TYPE,
    SHIFT,
    STATIC,
    START_LOCATION,
    END_LOCATION,
    PRO,
    ANTI,
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
    END_LAYER,
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
        hand_length = hand.boundingRect().width()
        hand_width = hand.boundingRect().height()
        hand.setPos(
            self.pictograph.grid.handpoints[hand.hand_location]
            + QPointF(hand_width / 2, -hand_length / 2)
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

        # BETA → BETA - G, H, I
        for start_location, motions in motions_grouped_by_start_loc.items():
            if len(motions) == 2:
                motion1, motion2 = motions
                if (
                    motion1[START_LOCATION] == motion2[START_LOCATION]
                    and motion1[END_LOCATION] == motion2[END_LOCATION]
                ):
                    if motion1[MOTION_TYPE] == SHIFT:
                        if motion2[MOTION_TYPE] == SHIFT:
                            self.reposition_beta_to_beta(motions)

        # GAMMA → BETA - Y, Z
        if len(pro_or_anti_motions) == 1 and len(static_motions) == 1:
            # if all the staves are in layer 1 or layer 2
            if all(hand.layer == 1 for hand in self.pictograph.hands) or all(
                hand.layer == 2 for hand in self.pictograph.hands
            ):
                self.reposition_gamma_to_beta(
                    move_hand, pro_or_anti_motions, static_motions
                )

        # ALPHA → BETA - D, E, F
        converging_motions = [
            motion for motion in board_state if motion[MOTION_TYPE] not in [STATIC]
        ]
        if len(converging_motions) == 2:
            if converging_motions[0].get(START_LOCATION) != converging_motions[1].get(
                START_LOCATION
            ):
                if all(hand.layer == 1 for hand in self.pictograph.hands) or all(
                    hand.layer == 2 for hand in self.pictograph.hands
                ):
                    self.reposition_alpha_to_beta(move_hand, converging_motions)

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
                1: {
                    (NORTH, RED): RIGHT,
                    (NORTH, BLUE): LEFT,
                    (SOUTH, RED): RIGHT,
                    (SOUTH, BLUE): LEFT,
                    (EAST, RED): (UP, DOWN) if end_location == EAST else None,
                    (WEST, BLUE): (UP, DOWN) if end_location == WEST else None,
                },
                2: {
                    (NORTH, RED): UP,
                    (NORTH, BLUE): DOWN,
                    (SOUTH, RED): UP,
                    (SOUTH, BLUE): DOWN,
                    (EAST, RED): (RIGHT, LEFT) if end_location == EAST else None,
                    (WEST, BLUE): (LEFT, RIGHT) if end_location == WEST else None,
                },
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

    ### ALPHA TO BETA ### D, E, F

    def reposition_alpha_to_beta(self, move_hand, converging_arrows) -> None:
        # check if all the hands are in layer 1
        if all(hand.layer == 1 for hand in self.pictograph.hands):
            end_locations = [arrow[END_LOCATION] for arrow in converging_arrows]
            start_locations = [arrow[START_LOCATION] for arrow in converging_arrows]
            if (
                end_locations[0] == end_locations[1]
                and start_locations[0] != start_locations[1]
            ):
                for arrow in converging_arrows:
                    direction = self.determine_translation_direction(arrow)
                    if direction:
                        move_hand(
                            next(
                                hand
                                for hand in self.pictograph.hands
                                if hand.arrow.color == arrow[COLOR]
                            ),
                            direction,
                        )
        # check if all the hands are in layer 2
        elif all(hand.layer == 2 for hand in self.pictograph.hands):
            end_locations = [arrow[END_LOCATION] for arrow in converging_arrows]
            start_locations = [arrow[START_LOCATION] for arrow in converging_arrows]
            if (
                end_locations[0] == end_locations[1]
                and start_locations[0] != start_locations[1]
            ):
                for arrow in converging_arrows:
                    direction = self.determine_translation_direction(arrow)
                    if direction:
                        move_hand(
                            next(
                                hand
                                for hand in self.pictograph.hands
                                if hand.arrow.color == arrow[COLOR]
                            ),
                            direction,
                        )
        # check if one hand is in layer 1 and the other is in layer 2
        elif any(hand.layer == 1 for hand in self.pictograph.hands) and any(
            hand.layer == 2 for hand in self.pictograph.hands
        ):
            end_locations = [arrow[END_LOCATION] for arrow in converging_arrows]
            start_locations = [arrow[START_LOCATION] for arrow in converging_arrows]
            if (
                end_locations[0] == end_locations[1]
                and start_locations[0] != start_locations[1]
            ):
                for arrow in converging_arrows:
                    direction = self.determine_translation_direction(arrow)
                    if direction:
                        move_hand(
                            next(
                                hand
                                for hand in self.pictograph.hands
                                if hand.arrow.color == arrow[COLOR]
                            ),
                            direction,
                        )

    ### BETA TO BETA ### G, H, I

    def reposition_beta_to_beta(self, motions) -> None:
        motion1, motion2 = motions
        same_motion_type = motion1[MOTION_TYPE] == motion2[MOTION_TYPE] == SHIFT

        if all(hand.layer == 1 for hand in self.pictograph.hands):
            if same_motion_type:
                self.reposition_G_and_H(motion1, motion2)
            else:
                self.reposition_I(motion1, motion2)

    def reposition_G_and_H(self, motion1, motion2) -> None:
        optimal_location1 = self.get_optimal_arrow_location(motion1)
        optimal_location2 = self.get_optimal_arrow_location(motion2)

        if not optimal_location1 or not optimal_location2:
            return

        distance1 = self.get_distance_from_center(optimal_location1)
        distance2 = self.get_distance_from_center(optimal_location2)

        further_arrow = motion1 if distance1 > distance2 else motion2
        other_arrow = motion1 if further_arrow == motion2 else motion2

        further_direction = self.determine_translation_direction(further_arrow)

        further_hand = next(
            hand
            for hand in self.pictograph.hands
            if hand.arrow.color == further_arrow[COLOR]
        )
        new_position_further = self.calculate_new_position(
            further_hand.pos(), further_direction
        )
        further_hand.setPos(new_position_further)

        other_direction = self.get_opposite_direction(further_direction)
        other_hand = next(
            hand
            for hand in self.pictograph.hands
            if hand.arrow.color == other_arrow[COLOR]
        )
        new_position_other = self.calculate_new_position(
            other_hand.pos(), other_direction
        )
        other_hand.setPos(new_position_other)

    def reposition_I(self, motion1, motion2) -> None:
        pro_motion = motion1 if motion1[MOTION_TYPE] == PRO else motion2
        anti_motion = motion2 if motion1[MOTION_TYPE] == PRO else motion1

        pro_hand = next(
            (
                hand
                for hand in self.pictograph.hands
                if hand.arrow.color == pro_motion[COLOR]
            ),
            None,
        )
        anti_hand = next(
            (
                hand
                for hand in self.pictograph.hands
                if hand.arrow.color == anti_motion[COLOR]
            ),
            None,
        )

        if pro_hand and anti_hand:
            pro_hand_translation_direction = self.determine_translation_direction(
                pro_motion
            )
            anti_hand_translation_direction = self.get_opposite_direction(
                pro_hand_translation_direction
            )

            new_position_pro = self.calculate_new_position(
                pro_hand.pos(), pro_hand_translation_direction
            )
            pro_hand.setPos(new_position_pro)

            new_position_anti = self.calculate_new_position(
                anti_hand.pos(), anti_hand_translation_direction
            )
            anti_hand.setPos(new_position_anti)

    ### GAMMA TO BETA ### Y, Z

    def reposition_gamma_to_beta(self, move_hand, shifts, static_motions) -> None:
        # if all of the hands are in layer 1:
        shift, static_motion = shifts[0], static_motions[0]
        direction = self.determine_translation_direction(shift)
        if direction:
            move_hand(
                next(
                    hand
                    for hand in self.pictograph.hands
                    if hand.arrow.color == shift[COLOR]
                ),
                direction,
            )
            move_hand(
                next(
                    hand
                    for hand in self.pictograph.hands
                    if hand.arrow.color == static_motion[COLOR]
                ),
                self.get_opposite_direction(direction),
            )

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

    def determine_translation_direction(self, motion) -> Direction:
        """Determine the translation direction based on the arrow's board_state."""
        if motion[END_LAYER] == 1 and motion[MOTION_TYPE] in [SHIFT, STATIC]:
            if motion[END_LOCATION] in [NORTH, SOUTH]:
                return RIGHT if motion[START_LOCATION] == EAST else LEFT
            elif motion[END_LOCATION] in [EAST, WEST]:
                return DOWN if motion[START_LOCATION] == SOUTH else UP
        elif motion[END_LAYER] == 2 and motion[MOTION_TYPE] in [SHIFT, STATIC]:
            if motion[END_LOCATION] in [NORTH, SOUTH]:
                return UP if motion[START_LOCATION] == EAST else DOWN
            elif motion[END_LOCATION] in [EAST, WEST]:
                return RIGHT if motion[START_LOCATION] == SOUTH else LEFT

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

    def get_distance_from_center(self, arrow_pos: Dict[str, float]) -> float:
        grid_center = self.pictograph.grid.center
        arrow_x, arrow_y = arrow_pos.get("x", 0.0), arrow_pos.get("y", 0.0)
        center_x, center_y = grid_center.x(), grid_center.y()

        distance_from_center = math.sqrt(
            (arrow_x - center_x) ** 2 + (arrow_y - center_y) ** 2
        )
        return distance_from_center

    def get_optimal_arrow_location(
        self, arrow_attributes: ArrowAttributesDicts
    ) -> Dict[str, float] | None:
        current_state = self.pictograph.get_state()
        current_letter = self.pictograph.current_letter

        if current_letter is not None:
            matching_letters = self.letters[current_letter]
            optimal_location = self.find_optimal_arrow_location_entry(
                current_state, matching_letters, arrow_attributes
            )
            if optimal_location:
                return optimal_location
        return None

    def get_opposite_direction(self, movement: Direction) -> Direction:
        if movement == LEFT:
            return RIGHT
        elif movement == RIGHT:
            return LEFT
        elif movement == UP:
            return DOWN
        elif movement == DOWN:
            return UP
