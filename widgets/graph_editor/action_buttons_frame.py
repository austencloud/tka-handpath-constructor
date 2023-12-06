from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout
from objects.arrow import Arrow
from settings.string_constants import ICON_DIR, CLOCKWISE, COUNTER_CLOCKWISE
from utilities.json_handler import JsonHandler
from widgets.graph_editor.pictograph.pictograph import Pictograph
from utilities.TypeChecking.TypeChecking import RotationDirections


class ActionButtonsFrame(QFrame):
    """
    A frame that contains action buttons for manipulating arrows in the pictograph.

    Args:
        pictograph (Pictograph): The pictograph widget.
        json_handler (JsonHandler): The JSON handler.
    """

    def __init__(
        self,
        pictograph: "Pictograph",
        json_handler: "JsonHandler",
    ) -> None:
        super().__init__()

        self.pictograph = pictograph
        self.json_handler = json_handler
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        # remove all space from the edges fo the frame to its contents

        self.setMaximumHeight(int(self.pictograph.view.height()))

        buttons_settings = [
            (
                "update_locations.png",
                "Update Optimal Locationss",
                lambda: self.json_handler.update_optimal_locations_in_json(
                    self.pictograph.get_current_arrow_coordinates()
                ),
            ),
            (
                "delete.png",
                "Delete",
                self.delete_selected_arrow,
            ),
            ("rotate_right.png", "Rotate Right", self.rotate_selected_arrow, CLOCKWISE),
            (
                "rotate_cw.png",
                "Rotate Left",
                self.rotate_selected_arrow,
                COUNTER_CLOCKWISE,
            ),
            (
                "mirror.png",
                "Mirror",
                self.mirror_selected_arrow,
            ),
            (
                "add_to_sequence.png",
                "Add to Sequence",
                lambda: self.pictograph.add_to_sequence(),
            ),
        ]

        for icon_filename, tooltip, action, *args in buttons_settings:
            button = self.create_and_configure_button(
                icon_filename, tooltip, action, *args
            )
            self.layout().addWidget(button)

    def create_and_configure_button(
        self, icon_filename, tooltip, on_click, *args
    ) -> QPushButton:
        """
        Create and configure a QPushButton.

        Args:
            icon_filename (str): The filename of the button icon.
            tooltip (str): The tooltip text.
            on_click (function): The function to be called when the button is clicked.
            *args: Additional arguments to be passed to the on_click function.

        Returns:
            QPushButton: The configured button.
        """
        icon_path = ICON_DIR + icon_filename
        button = QPushButton(QIcon(icon_path), "")
        button.setToolTip(tooltip)
        button.setFont(QFont("Helvetica", 14))
        button.clicked.connect(lambda: on_click(*args))
        return button

    def delete_selected_arrow(self) -> None:
        """
        Delete the selected arrow from the pictograph.
        """
        arrow: Arrow = (
            self.pictograph.selectedItems()[0]
            if self.pictograph.selectedItems()
            and isinstance(self.pictograph.selectedItems()[0], Arrow)
            else None
        )
        if arrow:
            arrow.delete()

    def rotate_selected_arrow(self, direction: RotationDirections) -> None:
        """
        Rotate the selected arrow in the specified direction.

        Args:
            direction (RotationDirections): The direction to rotate the arrow, either 'cw' or 'ccw'.

        """
        arrow: Arrow = (
            self.pictograph.selectedItems()[0]
            if self.pictograph.selectedItems()
            and isinstance(self.pictograph.selectedItems()[0], Arrow)
            else None
        )
        if arrow:
            arrow.rotate_arrow(direction)

    def mirror_selected_arrow(self) -> None:
        """
        Mirror the selected arrow.
        """
        arrow: Arrow = (
            self.pictograph.selectedItems()[0]
            if self.pictograph.selectedItems()
            and isinstance(self.pictograph.selectedItems()[0], Arrow)
            else None
        )
        if arrow:
            arrow.swap_rot_dir()
