import sys
import re

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QMessageBox
)

from Classes.Canvas import Canvas

CANVAS_WIDTH: int  = 100
CANVAS_HEIGHT: int = 100
resolution: int    = 4

grid_width: int    = int(CANVAS_WIDTH / resolution)
grid_height: int   = int(CANVAS_HEIGHT / resolution)
grid: list[list[int]]  = []
grid_initialized: bool = False

ANTS_RULES = ""

COLORS = [
    "#6A6A6A", "#FFFFFF",
    "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFA500", "#00FFFF", "#000000", "#000000",

    "#A60000", "#FF0000", "#FF6262", "#202072", "#3914AF", "#6A48D7",
    "#008500", "#00CC00", "#67E667", "#A68900", "#FFD300", "#FFDE40",

    "#FF4C4C", "#4CFF4C", "#4C4CFF"
]

ANT_UP      = 0
ANT_RIGHT   = 1
ANT_DOWN    = 2
ANT_LEFT    = 3

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

        # create class variables
        self.rules_input = None

        # Setup all widgets
        self.widgets_setup()


    def widgets_setup(self):
        # === Get all widgets from Qt designers layouts
        # Buttons
        start_button = self.window.findChild(QPushButton, "btn_start")
        show_rules_button = self.window.findChild(QPushButton, "btn_show_rules")
        clear_button = self.window.findChild(QPushButton, "btn_clear")
        self.rules_input = self.window.findChild(QLineEdit, "rules_input")

        # Canvases
        grid_canvas_placeholder = self.window.findChild(QWidget, "canvas_grid")
        rules_canvas_placeholder = self.window.findChild(QWidget, "canvas_rules")

        # === Assign clicked signals to functions
        if start_button:
            start_button.clicked.connect(self.start_button_clicked)
        if show_rules_button:
            show_rules_button.clicked.connect(self.show_rules_button_clicked)
        if clear_button:
            clear_button.clicked.connect(clear_button_clicked)

        # === Replacing the placeholders with my custom Canvas class
        if grid_canvas_placeholder:
            global CANVAS_WIDTH, CANVAS_HEIGHT

            layout = grid_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(grid_canvas_placeholder)

            grid_canvas = Canvas("#F0F0F0", grid_canvas_placeholder, parent=grid_canvas_placeholder.parentWidget())
            CANVAS_WIDTH = grid_canvas.width()
            CANVAS_HEIGHT = grid_canvas.height()
            updateGridSize()

            layout.removeWidget(grid_canvas_placeholder)
            grid_canvas_placeholder.deleteLater()  # delete placeholder
            layout.insertWidget(index, grid_canvas)

        if rules_canvas_placeholder:
            layout = rules_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(rules_canvas_placeholder)

            rules_canvas = Canvas("#F0F0F0", rules_canvas_placeholder, parent=rules_canvas_placeholder.parentWidget())

            layout.removeWidget(rules_canvas_placeholder)
            rules_canvas_placeholder.deleteLater()  # delete placeholder
            layout.insertWidget(index, rules_canvas)

    def start_button_clicked(self):
        if self.updateRulesInput():
            print("Rules: " + ANTS_RULES)
        pass

    def show_rules_button_clicked(self):
        print("SHOW RULES button clicked!")
        pass

    def updateRulesInput(self) -> bool:
        global ANTS_RULES

        if not self.rules_input:
            raise RuntimeError("Input widget could not be located!")

        input_text = self.rules_input.text()
        if not re.fullmatch(r"^[lLrR]*$", input_text):
            ANTS_RULES = ""
            show_rules_input_error_popup("Wrong input!! R,L,r,l options available only!\n\nR,r - right\nL,l - left")
            return False

        if len(input_text) < 2 or len(input_text) > 20:
            ANTS_RULES = ""
            show_rules_input_error_popup("Rules length error!!\n\nMinimum 2 rules\nMaximum 20 rules")
            return False

        ANTS_RULES = str.upper(input_text)
        return True

    def show(self):
        self.window.show()


# ==== Globally defined functions ====
def clear_button_clicked():
    print("CLEAR button clicked!")
    pass



def updateGridSize():
    global grid_width, grid_height, grid, grid_initialized
    grid_width = int(CANVAS_WIDTH / resolution)
    grid_height = int(CANVAS_HEIGHT / resolution)

    grid = [[0 for _ in range(grid_height)] for _ in range(grid_width)]
    grid_initialized = True

def show_rules_input_error_popup(error_message: str):
    msg = QMessageBox()
    msg.setWindowTitle("Ant's rules input error")
    msg.setText(error_message)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    ret = msg.exec()  # shows dialog window

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow("ui/LangtonsAnt.ui")
    window.show()

    sys.exit(app.exec())