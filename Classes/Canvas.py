from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtCore import QRect, Qt

class Canvas(QWidget):
    def __init__(self,  _bg_color="#FFF", previous_placeholder: QWidget = None, parent=None):
        super().__init__(parent)
        self.Bg_color = _bg_color
        self.cell_size = 1
        self.cells = {}


        if previous_placeholder and isinstance(previous_placeholder, QWidget):
            self.setMinimumSize(previous_placeholder.minimumSize())
            self.setMaximumSize(previous_placeholder.maximumSize())
            self.resize(previous_placeholder.size())
            self.setSizePolicy(previous_placeholder.sizePolicy())
            self.setEnabled(previous_placeholder.isEnabled())
        else:
            raise AttributeError("Placeholder does not have type of QWidget")

    def setCellSize(self, cell_size: int):
        self.cell_size = cell_size

    def addCell(self, x: int, y: int, color: str):
        # adding or updating existing cell
        self.cells[(x, y)] = color
        self.update()

    def clearCell(self, x: int, y: int):
        if (x, y) in self.cells:
            del self.cells[(x, y)]
            self.update()

    def clearAllCells(self):
        self.cells.clear()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.Bg_color))

        painter.setPen(Qt.PenStyle.NoPen)

        for (x, y), color in self.cells.items():
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRect(QRect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))