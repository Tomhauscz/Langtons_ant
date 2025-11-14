from dataclasses import dataclass

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QBrush, QColor, QPixmap, QImage, QPen, QPolygon
from PySide6.QtCore import QRect, Qt, QPoint

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

        self.x_offset = 15
        self.y_offset = 35
        self.rule_rect_size = 50
        self.rule_rect_spacing = 25

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

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        for index, rule_pair in enumerate(self.rules):
            rule_rect_x_offset = self.x_offset
            rule_rect_y_offset = self.y_offset + index * (self.rule_rect_size + self.rule_rect_spacing)
            if index > 9:
                rule_rect_x_offset = self.x_offset + self.rule_rect_size + 20
                rule_rect_y_offset = self.y_offset + (19 - index) * (self.rule_rect_size  + self.rule_rect_spacing)

            # draw a square with the given color
            if index == 0:
                painter.setPen(QPen(QColor("#FF0000"), 2, Qt.PenStyle.SolidLine))
            else:
                painter.setPen(QPen(QColor("#000000"), 1, Qt.PenStyle.SolidLine))
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

            # draw arrows pointing to the next rule square
            if index < 9 and index < (len(self.rules) - 1):
                arrow_start_point = QPoint(self.x_offset + int(self.rule_rect_size / 2),
                                           self.y_offset + self.rule_rect_size +
                                           index * (self.rule_rect_size + self.rule_rect_spacing) + 1)
                if index == 0:
                    arrow_start_point.setY(arrow_start_point.y() + 1)
                arrow_end_point = QPoint(self.x_offset + int(self.rule_rect_size / 2),
                                         self.y_offset + self.rule_rect_size + self.rule_rect_spacing +
                                         index * (self.rule_rect_size + self.rule_rect_spacing) - 2)
                draw_arrow(painter, arrow_start_point, arrow_end_point, True)
            elif 9 < index < (len(self.rules) - 1):
                arrow_start_point = QPoint(self.x_offset + self.rule_rect_size + 20 + int(self.rule_rect_size / 2),
                                           self.y_offset +
                                           (19 - index) * (self.rule_rect_size + self.rule_rect_spacing) - 1)
                arrow_end_point = QPoint(self.x_offset + self.rule_rect_size + 20 + int(self.rule_rect_size / 2),
                                         self.y_offset - self.rule_rect_spacing +
                                         (19 - index) * (self.rule_rect_size + self.rule_rect_spacing) + 2)
                draw_arrow(painter, arrow_start_point, arrow_end_point, False)

        # draw the bottom U-shaped arrow or arrow back to the top
        pen = QPen(Qt.PenStyle.SolidLine)
        pen.setWidth(2)
        painter.setPen(pen)
        if 1 < len(self.rules) <= 10:
            u_arrow_bottom_points = [
                QPoint(self.x_offset + int(self.rule_rect_size / 2),
                       self.y_offset - self.rule_rect_spacing + 1 +
                       len(self.rules) * (self.rule_rect_size + self.rule_rect_spacing)),
                QPoint(self.x_offset + int(self.rule_rect_size / 2),
                       self.y_offset +
                       len(self.rules) * (self.rule_rect_size + self.rule_rect_spacing)),
                QPoint(self.x_offset + int(self.rule_rect_size / 2) + self.rule_rect_size + 20,
                       self.y_offset +
                       len(self.rules) * (self.rule_rect_size + self.rule_rect_spacing)),
                QPoint(self.x_offset + int(self.rule_rect_size / 2) + self.rule_rect_size + 20,
                       self.y_offset - self.rule_rect_spacing),
                QPoint(self.x_offset + int(self.rule_rect_size / 2),
                       self.y_offset - self.rule_rect_spacing),
                QPoint(self.x_offset + int(self.rule_rect_size / 2),
                       self.y_offset - self.rule_rect_spacing + 10)
            ]
            painter.drawPolyline(QPolygon(u_arrow_bottom_points))

        elif len(self.rules) > 10:
            # --- draw the bottom U-shaped arrow
            u_arrow_bottom_points = [
                QPoint(self.x_offset + int(self.rule_rect_size / 2),
                       self.y_offset - self.rule_rect_spacing + 1 +
                       10 * (self.rule_rect_size + self.rule_rect_spacing)),
                QPoint(self.x_offset + int(self.rule_rect_size / 2),
                       self.y_offset +
                       10 * (self.rule_rect_size + self.rule_rect_spacing)),
                QPoint(self.x_offset + int(self.rule_rect_size / 2) + self.rule_rect_size + 20,
                       self.y_offset +
                       10 * (self.rule_rect_size + self.rule_rect_spacing)),
                QPoint(self.x_offset + int(self.rule_rect_size / 2) + self.rule_rect_size + 20,
                       self.y_offset - 10 +
                       10 * (self.rule_rect_size + self.rule_rect_spacing))
            ]
            painter.drawPolyline(QPolygon(u_arrow_bottom_points))

            # draw last segment as regular arrow
            draw_arrow(painter,
                       QPoint(self.x_offset + self.rule_rect_size + 20 + int(self.rule_rect_size / 2),
                              self.y_offset - 10 +
                              10 * (self.rule_rect_size + self.rule_rect_spacing)),
                       QPoint(self.x_offset + self.rule_rect_size + 20 + int(self.rule_rect_size / 2),
                              self.y_offset - self.rule_rect_spacing + 2 +
                              10 * (self.rule_rect_size + self.rule_rect_spacing)),
                              False)

            # --- draw the top U-shaped arrow
            u_arrow_top_points = [
                QPoint(self.x_offset + self.rule_rect_size + 20 + int(self.rule_rect_size / 2),
                       self.y_offset - 1 +
                       (20 - len(self.rules)) * (self.rule_rect_size + self.rule_rect_spacing)),
                QPoint(self.x_offset + self.rule_rect_size + 20 + int(self.rule_rect_size / 2),
                       self.y_offset - self.rule_rect_spacing),
                QPoint(self.x_offset + int(self.rule_rect_size / 2),
                       self.y_offset - self.rule_rect_spacing),
                QPoint(self.x_offset + int(self.rule_rect_size / 2),
                       self.y_offset - self.rule_rect_spacing + 10)
            ]
            painter.drawPolyline(QPolygon(u_arrow_top_points))

        # draw last segment as regular arrow (same for both conditions)
        if len(self.rules) > 1:
            draw_arrow(painter,
                       QPoint(self.x_offset + int(self.rule_rect_size / 2), self.y_offset - self.rule_rect_spacing + 10),
                       QPoint(self.x_offset + int(self.rule_rect_size / 2), self.y_offset - 2),
                       True)



def draw_arrow(painter: QPainter, p1: QPoint, p2: QPoint, pointing_down: bool):
        pen = QPen(Qt.PenStyle.SolidLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(p1, p2)

        # draw the pointing
        arrow_left_point = QPoint(p2.x() - 4, (p2.y() - 7) if pointing_down else (p2.y() + 7))
        arrow_right_point = QPoint(p2.x() + 4, (p2.y() - 7) if pointing_down else (p2.y() + 7))

        painter.drawLine(arrow_left_point, p2)
        painter.drawLine(arrow_right_point, p2)