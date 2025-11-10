import sys

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout
)

from Classes.Canvas import Canvas

CANVAS_WIDTH    = 800
CANVAS_HEIGHT   = 800
resolution      = 4
grid_width      = CANVAS_WIDTH / resolution
grid_height     = CANVAS_HEIGHT / resolution

PANEL_WIDTH = 200

WINDOW_WIDTH = CANVAS_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = CANVAS_HEIGHT


class MainWindow(QWidget):
    def __init__(self, ui_file_path):
        super().__init__()

        # Loading UI file
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        if not self.window:
            raise RuntimeError("Failed to load the UI file.")

        # Window title
        self.window.setWindowTitle("Langton's ant")

        grid_canvas_placeholder = self.window.findChild(QWidget, "canvas_grid")
        rules_canvas_placeholder = self.window.findChild(QWidget, "canvas_rules")

        # === Replacing the placeholders with my custom Canvas class
        if grid_canvas_placeholder:
            layout = grid_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(grid_canvas_placeholder)

            grid_canvas = Canvas("#F00", grid_canvas_placeholder, parent=grid_canvas_placeholder.parentWidget())
            print("Grid_canvas size: " + str(grid_canvas.width()) + "x" + str(grid_canvas.height()))

            layout.removeWidget(grid_canvas_placeholder)
            grid_canvas_placeholder.deleteLater()                 # delete placeholder
            layout.insertWidget(index, grid_canvas)

        if rules_canvas_placeholder:
            layout = rules_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(rules_canvas_placeholder)

            rules_canvas = Canvas("#00F", rules_canvas_placeholder, parent=rules_canvas_placeholder.parentWidget())
            print("Rules_canvas size: " + str(rules_canvas.width()) + "x" + str(rules_canvas.height()))

            layout.removeWidget(rules_canvas_placeholder)
            rules_canvas_placeholder.deleteLater()                 # delete placeholder
            layout.insertWidget(index, rules_canvas)

    def show(self):
        self.window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow("ui/LangtonsAnt.ui")
    window.show()

    sys.exit(app.exec())