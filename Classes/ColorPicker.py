from PySide6.QtWidgets import (
    QPushButton,
    QColorDialog
)
from PySide6.QtCore import (
    QPointF,
    Signal
)
from PySide6.QtGui import (
    QPainter,
    QLinearGradient,
    QColor
)

class ColorPicker(QPushButton):
    # Signal that allows emitting of the selected color in hex (String) format
    selectedColorSignal = Signal(str)

    def __init__(self, previous_placeholder: QPushButton = None, parent=None):
        super().__init__(parent)
        self.grad_icon_margin = 3

        self.grad_start_color: str = "#000000"
        self.grad_end_color: str = "#FFFFFF"
        self.is_starting_color: bool = True

        if previous_placeholder and isinstance(previous_placeholder, QPushButton):
            self.setMinimumSize(previous_placeholder.minimumSize())
            self.setMaximumSize(previous_placeholder.maximumSize())
            self.resize(previous_placeholder.size())
            self.setSizePolicy(previous_placeholder.sizePolicy())
            self.setEnabled(previous_placeholder.isEnabled())
        else:
            raise AttributeError("Placeholder does not have type of QPushButton")

        self.clicked.connect(self.on_click)

    def setGradient(self, color_start_hex: str, color_end_hex: str, is_start_clr: bool):
        self.grad_start_color = color_start_hex
        self.grad_end_color = color_end_hex
        self.is_starting_color = is_start_clr
        self.update()

    def paintEvent(self, event):
        # calling QPushButton paintEvent first
        super().paintEvent(event)

        painter = QPainter(self)

        grad_icon_width = self.width() - 2 * self.grad_icon_margin
        grad_icon_height = self.height() - 2 * self.grad_icon_margin

        grad = QLinearGradient(QPointF(0, 0), QPointF(grad_icon_width, 0))
        grad.setColorAt(0.0, QColor(self.grad_start_color))
        grad.setColorAt(1.0, QColor(self.grad_end_color))

        painter.fillRect(self.grad_icon_margin, self.grad_icon_margin, grad_icon_width, grad_icon_height, grad)
        painter.end()

    def on_click(self):
        initial_color = self.grad_start_color if self.is_starting_color else self.grad_end_color
        title_text = "Select gradient starting color" if self.is_starting_color else "Select gradient ending color"

        # Open Color Dialog
        selected_color = QColorDialog.getColor(
            initial=QColor(initial_color),
            parent=self,
            title=title_text
        )

        if selected_color.isValid():
            self.selectedColorSignal.emit(selected_color.name())