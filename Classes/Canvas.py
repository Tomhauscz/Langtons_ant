from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt

class Canvas(QWidget):
    def __init__(self,  _bg_color="#FFF", previous_placeholder: QWidget = None, parent=None):
        super().__init__(parent)
        self.Bg_color = _bg_color


        if previous_placeholder and isinstance(previous_placeholder, QWidget):
            self.setMinimumSize(previous_placeholder.minimumSize())
            self.setMaximumSize(previous_placeholder.maximumSize())
            self.resize(previous_placeholder.size())
            self.setSizePolicy(previous_placeholder.sizePolicy())
            self.setEnabled(previous_placeholder.isEnabled())
        else:
            raise AttributeError("Placeholder does not have type of QWidget")


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.Bg_color))