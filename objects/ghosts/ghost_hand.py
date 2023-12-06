from objects.hand import Hand
from settings.string_constants import COLOR
from utilities.TypeChecking.TypeChecking import TYPE_CHECKING, HandAttributesDicts

if TYPE_CHECKING:
    from widgets.graph_editor.pictograph.pictograph import Pictograph


class GhostHand(Hand):
    """
    Represents a ghost hand object, displaying the position that a hand will be while dragging if the user were to drop it.

    Inherits from the Hand class.

    Attributes:
        pictograph (Pictograph): The pictograph object.
        color (str): The color of the hand.
        target_hand (Hand): The hand that the ghost hand is copying.

    Methods:
        __init__: Initialize a GhostHand object.

    """

    def __init__(
        self, pictograph: "Pictograph", attributes: HandAttributesDicts
    ) -> None:
        super().__init__(pictograph, attributes)
        self.setOpacity(0.2)
        self.pictograph = pictograph
        self.color = attributes[COLOR]
        self.target_hand: "Hand" = None
        self.setup_svg_renderer(self.svg_file)
