from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt

from typing import TYPE_CHECKING

from widgets.graph_editor.object_panel.objectbox_view import ObjectBoxView

if TYPE_CHECKING:
    from widgets.graph_editor.object_panel.handbox.handbox import Handbox


class HandBoxView(ObjectBoxView):
    def __init__(self, handbox: "Handbox") -> None:
        super().__init__(handbox)
        self.setFixedSize(
            int(handbox.main_window.height() * 1 / 6),
            int(handbox.main_window.height() * 1 / 6),
        )
        self.setScene(handbox)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.handbox = handbox

        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)  # Call the parent class's resizeEvent
        if self.scene():
            self.scale(
                self.width() / self.scene().width(),
                self.height() / self.scene().height(),
            )
