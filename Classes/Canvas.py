from dataclasses import dataclass

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QBrush, QColor, QPixmap, QImage
from PySide6.QtCore import QRect, Qt

@dataclass
class Rule:
    rule: str
    color: str

class GridCanvas(QWidget):
    def __init__(self, _bg_color="#FFF", previous_placeholder: QWidget = None, parent=None):
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

class RulesCanvas(QWidget):
    def __init__(self, _bg_color="#FFF", previous_placeholder: QWidget = None, parent=None):
        super().__init__(parent)
        self.Bg_color = _bg_color
        self.rules = []

        self.x_offset = 25
        self.y_offset = 35
        self.rule_rect_size = 50
        self.rule_rect_spacing = self.rule_rect_size + 25

        self.right_turn_image = None
        self.left_turn_image = None
        self.right_turn_image_inverted = None   # color inverted version
        self.left_turn_image_inverted = None    # color inverted version

        self.image_scale = 0.75

        if previous_placeholder and isinstance(previous_placeholder, QWidget):
            self.setMinimumSize(previous_placeholder.minimumSize())
            self.setMaximumSize(previous_placeholder.maximumSize())
            self.resize(previous_placeholder.size())
            self.setSizePolicy(previous_placeholder.sizePolicy())
            self.setEnabled(previous_placeholder.isEnabled())
        else:
            raise AttributeError("Placeholder does not have type of QWidget")

    def setLeftAndRightImages(self, right_img_path: str, left_img_path: str):
        image_scale = int(self.image_scale * self.rule_rect_size)
        # right and left images loaded and scaled
        self.right_turn_image = QPixmap(right_img_path).scaled(image_scale, image_scale,
                                                               Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation)

        self.left_turn_image = QPixmap(left_img_path).scaled(image_scale, image_scale,
                                                             Qt.AspectRatioMode.KeepAspectRatio,
                                                             Qt.TransformationMode.SmoothTransformation)

        # inverted version of right and left images loaded and scaled
        right_turn_inverted = QImage(right_img_path)
        right_turn_inverted.invertPixels()
        self.right_turn_image_inverted = QPixmap.fromImage(right_turn_inverted)
        self.right_turn_image_inverted = self.right_turn_image_inverted.scaled(image_scale, image_scale,
                                                                               Qt.AspectRatioMode.KeepAspectRatio,
                                                                               Qt.TransformationMode.SmoothTransformation)

        left_turn_inverted = QImage(left_img_path)
        left_turn_inverted.invertPixels()
        self.left_turn_image_inverted = QPixmap.fromImage(left_turn_inverted)
        self.left_turn_image_inverted = self.left_turn_image_inverted.scaled(image_scale, image_scale,
                                                                             Qt.AspectRatioMode.KeepAspectRatio,
                                                                             Qt.TransformationMode.SmoothTransformation)

    def addRules(self, rules: str, rule_colors: list[str]):
        self.rules.clear()
        for i, c in enumerate(rules):
            self.rules.append(Rule(c, rule_colors[i]))
        self.update()

    def getImageBasedOnBGBrightness(self, image_type: str, bg_color: QColor) -> QPixmap:
        # Compute relative brightness (ITU-R BT.709 standard)
        brightness = (
                0.2126 * bg_color.redF() +
                0.7152 * bg_color.greenF() +
                0.0722 * bg_color.blueF()
        )

        match image_type:
            case "R":
                if brightness < 0.5:
                    return self.right_turn_image_inverted
                else:
                    return self.right_turn_image
            case "L":
                if brightness < 0.5:
                    return self.left_turn_image_inverted
                else:
                    return self.left_turn_image

        return QPixmap()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.Bg_color))

        painter.setPen(Qt.PenStyle.SolidLine)

        for index, rule_pair in enumerate(self.rules):
            rule_rect_x_offset = self.x_offset
            rule_rect_y_offset = self.y_offset + index * self.rule_rect_spacing
            painter.setBrush(QBrush(QColor(rule_pair.color)))
            painter.drawRect(QRect(rule_rect_x_offset, rule_rect_y_offset, self.rule_rect_size, self.rule_rect_size))

            # check if images exist
            if self.right_turn_image and self.left_turn_image and self.right_turn_image_inverted and self.left_turn_image_inverted:
                right_img = self.getImageBasedOnBGBrightness("R", QColor(rule_pair.color))
                left_img = self.getImageBasedOnBGBrightness("L", QColor(rule_pair.color))
                match rule_pair.rule:
                    case "R":
                        painter.drawPixmap(
                            rule_rect_x_offset + int(((1 - self.image_scale) / 2) * self.rule_rect_size),
                            rule_rect_y_offset + int(((1 - self.image_scale) / 2) * self.rule_rect_size),
                            right_img
                        )
                    case "L":
                        painter.drawPixmap(
                            rule_rect_x_offset + int(((1 - self.image_scale) / 2) * self.rule_rect_size),
                            rule_rect_y_offset + int(((1 - self.image_scale) / 2) * self.rule_rect_size),
                            left_img
                        )



