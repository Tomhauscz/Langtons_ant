import sys
import re

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (
    QFile,
    QTimer
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit
)

from Classes.Canvas import Canvas
from Classes.DialogWindow import WarningDialog

ant_tick_period: int = 1000        # [ms]

CANVAS_WIDTH: int  = 100
CANVAS_HEIGHT: int = 100
resolution: int    = 4

grid_width: int    = int(CANVAS_WIDTH / resolution)
grid_height: int   = int(CANVAS_HEIGHT / resolution)
grid: list[list[int]]  = []
grid_initialized: bool = False

ant_x_pos: int = 0
ant_y_pos: int = 0
ant_moving: bool = False

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

QGuiApplication.beep = lambda: None

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

        # Create timer for ant_loop(), but don't start it yet
        self.timer = QTimer()
        self.timer.timeout.connect(ant_loop)

        # create class variables
        self.start_button: QPushButton = QPushButton()
        self.rules_input: QLineEdit = QLineEdit()
        self.grid_canvas = None

        # Setup all widgets
        self.widgets_setup()


    def widgets_setup(self):
        # === Get all widgets from Qt designers layouts
        # Buttons
        self.start_button = self.window.findChild(QPushButton, "btn_start")
        show_rules_button = self.window.findChild(QPushButton, "btn_show_rules")
        clear_button = self.window.findChild(QPushButton, "btn_clear")
        # Text input (QLineEdit)
        self.rules_input = self.window.findChild(QLineEdit, "rules_input")

        # Canvases
        grid_canvas_placeholder = self.window.findChild(QWidget, "canvas_grid")
        rules_canvas_placeholder = self.window.findChild(QWidget, "canvas_rules")

        # === Assign clicked signals to functions
        if self.start_button:
            self.start_button.clicked.connect(self.start_button_clicked)
        if show_rules_button:
            show_rules_button.clicked.connect(self.show_rules_button_clicked)
        if clear_button:
            clear_button.clicked.connect(clear_button_clicked)

        # === Replacing the placeholders with my custom Canvas class
        if grid_canvas_placeholder:
            global CANVAS_WIDTH, CANVAS_HEIGHT

            layout = grid_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(grid_canvas_placeholder)

            self.grid_canvas = Canvas("#F0F0F0", grid_canvas_placeholder, parent=grid_canvas_placeholder.parentWidget())
            CANVAS_WIDTH = self.grid_canvas.width()
            CANVAS_HEIGHT = self.grid_canvas.height()
            updateGridSize()
            self.grid_canvas.setCellSize(resolution)

            layout.removeWidget(grid_canvas_placeholder)
            grid_canvas_placeholder.deleteLater()  # delete placeholder
            layout.insertWidget(index, self.grid_canvas)

        if rules_canvas_placeholder:
            layout = rules_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(rules_canvas_placeholder)

            rules_canvas = Canvas("#F0F0F0", rules_canvas_placeholder, parent=rules_canvas_placeholder.parentWidget())

            layout.removeWidget(rules_canvas_placeholder)
            rules_canvas_placeholder.deleteLater()  # delete placeholder
            layout.insertWidget(index, rules_canvas)

    def start_button_clicked(self):
        global ant_moving
        if ant_moving:
            if self.timer.isActive():
                ant_moving = False
                self.timer.stop()
                if self.start_button:
                    self.start_button.setText("Start")

        elif self.updateRulesInput():
            print("Rules: " + ANTS_RULES)
            ant_moving = True
            self.timer.start(ant_tick_period)
            if self.start_button:
                self.start_button.setText("Stop")
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
            show_rules_input_warn_popup("Wrong input!! R,L,r,l options available only!\n\nR,r - right\nL,l - left")
            return False

        if len(input_text) < 2 or len(input_text) > 20:
            ANTS_RULES = ""
            show_rules_input_warn_popup("Rules length error!!\n\nMinimum 2 rules\nMaximum 20 rules")
            return False

        ANTS_RULES = str.upper(input_text)
        return True

    def show(self):
        self.window.show()


# ==== Globally defined functions ====
def ant_loop():
    print("Ant loop executed!")
    pass

def clear_button_clicked():
    print("CLEAR button clicked!")
    pass


def updateGridSize():
    global grid_width, grid_height, grid, grid_initialized
    grid_width = int(CANVAS_WIDTH / resolution)
    grid_height = int(CANVAS_HEIGHT / resolution)

    grid = [[0 for _ in range(grid_height)] for _ in range(grid_width)]
    grid_initialized = True

def show_rules_input_warn_popup(warn_message: str):
    # Could be done with QMessageBox, but I do not like the way OS handles it
    """
    msg = QMessageBox()
    msg.setWindowTitle("Ant's rules input error")
    msg.setText(warn_message)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    ret = msg.exec()  # shows dialog window
    """
    warning_dialog = WarningDialog()
    warning_dialog.setTitle("Ant's rules input warning")
    warning_dialog.setMessage(warn_message)
    warning_dialog.exec()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow("ui/LangtonsAnt.ui")
    window.show()

    sys.exit(app.exec())