from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QPalette
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from widgets.graph_editor.attr_panel.attr_box_widgets.start_end_widget import (
        StartEndWidget,
    )

    from widgets.graph_editor.attr_panel.attr_box_widgets.motion_types_widget import (
        MotionTypesWidget,
    )


class CustomButton(QPushButton):
    def __init__(
        self, widget: Union["StartEndWidget", "MotionTypesWidget"]
    ):
        super().__init__(widget)
        self._color = self.palette().color(QPalette.ColorRole.Button)
        self.widget = widget
        self.button_size = int(self.widget.attr_box.attr_box_width * 0.2 * 0.8)
        self.border_radius = self.button_size / 2
        self.setStyleSheet(self.get_button_style())


    def get_button_style(self):
        return (
            f"QPushButton {{"
            f"   background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(200, 200, 200, 255));"
            f"   border-radius: {self.border_radius}px;"
            f"   border: 1px solid black;"
            f"   min-width: {self.button_size}px;"
            f"   min-height: {self.button_size}px;"  # Adjust height to match width for a circle
            f"   max-width: {self.button_size}px;"
            f"   max-height: {self.button_size}px;"
            f"}}"
            f"QPushButton:hover {{"
            f"   background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(230, 230, 230, 255), stop:1 rgba(200, 200, 200, 255));"
            f"}}"
            f"QPushButton:pressed {{"
            f"   background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(204, 228, 247, 255), stop:1 rgba(164, 209, 247, 255));"
            f"}}"
        )
