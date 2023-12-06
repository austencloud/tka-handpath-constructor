from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QGraphicsView,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtGui import QPalette, QColor
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from widgets.main_widget import MainWidget


class LayoutManager:
    def __init__(self, main_widget: "MainWidget") -> None:
        self.main_widget = main_widget
        self.main_window = main_widget.main_window
        self.layouts: Dict[str, QHBoxLayout | QVBoxLayout] = {}
        self.init_layouts()
        self.assign_layouts_to_window()
        self.main_layout: QHBoxLayout = self.layouts["main"]
        self.left_layout: QVBoxLayout = self.layouts["right"]
        self.right_layout: QVBoxLayout = self.layouts["left"]
        self.graph_editor_layout: QHBoxLayout = self.layouts["graph_editor"]


        self.graph_editor = self.main_widget.graph_editor
        self.pictograph = self.main_widget.graph_editor.pictograph

    def configure_layouts(self) -> None:
        self.configure_main_layout()
        self.add_black_border_to_widgets()

    def init_layouts(self) -> None:
        self.layouts = {
            "main": QHBoxLayout(),
            "right": QVBoxLayout(),
            "left": QVBoxLayout(),
            "graph_editor": QHBoxLayout(),
            "sequence": QHBoxLayout(),
            "objectbox": QVBoxLayout(),
            "pictograph": QVBoxLayout(),
            "word": QHBoxLayout(),
            "pictograph_and_buttons": QHBoxLayout(),
            "letter_buttons": QVBoxLayout(),
            "keyboard": QVBoxLayout(),
        }

    def configure_main_layout(self) -> None:
        self.layouts["right"].addLayout(self.layouts["graph_editor"])
        self.layouts["main"].addLayout(self.layouts["right"])

        self.graph_editor_layout.addWidget(self.graph_editor)
        self.main_widget.setLayout(self.layouts["main"])
        self.main_widget.layout().setSpacing(0)
        self.main_widget.layout().setContentsMargins(0, 0, 0, 0)

    def add_black_border_to_widgets(self) -> None:
        self.add_black_border(self.main_widget.graph_editor.pictograph)
        self.add_black_border(self.main_widget.graph_editor.pictograph)
        self.add_black_border(self.main_widget.graph_editor.handbox)

    def assign_layouts_to_window(self) -> None:
        for layout_name, layout in self.layouts.items():
            setattr(self.main_window, f"{layout_name}_layout", layout)

    def add_black_border(
        self, widget: QWidget | QGraphicsView | QLabel | QPushButton | QFrame
    ) -> None:
        if isinstance(widget, QFrame):
            try:
                widget.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
                widget.setLineWidth(1)
                palette = widget.palette()
                palette.setColor(QPalette.ColorRole.WindowText, QColor("black"))
                widget.setPalette(palette)
            except AttributeError:
                print(f"Widget {widget} does not have a setFrameStyle method.")
