import sys
import re
from enum import IntEnum


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

ant_tick_period: int = 1        # [ms]

CANVAS_WIDTH: int  = 100
CANVAS_HEIGHT: int = 100
resolution: int    = 4

grid_width: int    = int(CANVAS_WIDTH / resolution)
grid_height: int   = int(CANVAS_HEIGHT / resolution)
grid: list[list[int]] = []

grid_canvas: Canvas

ant_x_pos: int = 0
ant_y_pos: int = 0
ant_direction: int = 0
ant_stopped: bool = True

ANTS_RULES = ""

COLORS = [
    "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFA500", "#00FFFF", "#000000", "#000000",

    "#A60000", "#FF0000", "#FF6262", "#202072", "#3914AF", "#6A48D7",
    "#008500", "#00CC00", "#67E667", "#A68900", "#FFD300", "#FFDE40",

    "#FF4C4C", "#4CFF4C", "#4C4CFF"
]

class Directions(IntEnum):
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

        # Window title and fix resizing
        self.window.setWindowTitle("Langton's ant")
        self.window.setFixedSize(self.window.size())


        # Create timer for ant_loop(), but don't start it yet
        self.timer = QTimer()
        self.timer.timeout.connect(ant_loop)

        # create class variables
        self.start_button: QPushButton = QPushButton()
        self.rules_input: QLineEdit = QLineEdit()

        # Setup all widgets
        self.widgets_setup()

    def widgets_setup(self):
        # === Get all widgets from Qt designers layouts
        # Buttons
        self.start_button = self.window.findChild(QPushButton, "btn_start")
        show_rules_button = self.window.findChild(QPushButton, "btn_show_rules")
        pause_button = self.window.findChild(QPushButton, "btn_pause")
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
        if pause_button:
            pause_button.clicked.connect(self.pause_button_clicked)

        # === Replacing the placeholders with my custom Canvas class
        if grid_canvas_placeholder:
            global CANVAS_WIDTH, CANVAS_HEIGHT, grid_canvas

            layout = grid_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(grid_canvas_placeholder)

            grid_canvas = Canvas("#F0F0F0", grid_canvas_placeholder, parent=grid_canvas_placeholder.parentWidget())
            CANVAS_WIDTH = grid_canvas.width()
            CANVAS_HEIGHT = grid_canvas.height()
            updateGridSize()
            grid_canvas.setCellSize(resolution)

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
        global ant_stopped

        if ant_stopped:
            reinit_ant()                    # reinitiates the ant
            grid_canvas.clearAllCells()     # clear the canvas also

            if self.updateRulesInput():
                #print("Rules: " + ANTS_RULES)
                ant_stopped = False
                self.timer.start(ant_tick_period)
                if self.start_button:
                    self.start_button.setText("Stop")

        elif self.timer.isActive():
            ant_stopped = True
            self.timer.stop()
            if self.start_button:
                self.start_button.setText("Start")

    def pause_button_clicked(self):
        if self.timer.isActive():
            self.timer.stop()
        elif not ant_stopped:
            self.timer.start(ant_tick_period)

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
def ant_turn_right():
    global ant_direction
    ant_direction += 1      # cruel Python, ant_direction++ would be much easier
    if ant_direction > Directions.ANT_LEFT:
        ant_direction = Directions.ANT_UP

def ant_turn_left():
    global ant_direction
    ant_direction -= 1
    if ant_direction < Directions.ANT_UP:
        ant_direction = Directions.ANT_LEFT

def ant_move_forward():
    global ant_x_pos, ant_y_pos
    match ant_direction:
        case Directions.ANT_UP:
            ant_y_pos -= 1
        case Directions.ANT_RIGHT:
            ant_x_pos += 1
        case Directions.ANT_DOWN:
            ant_y_pos += 1
        case Directions.ANT_LEFT:
            ant_x_pos -= 1
        case _:
            pass

    # grid wrap around
    if ant_x_pos > grid_width - 1:
        ant_x_pos = 0
    elif ant_x_pos < 0:
        ant_x_pos = grid_width - 1

    if ant_y_pos > grid_height - 1:
        ant_y_pos = 0
    elif ant_y_pos < 0:
        ant_y_pos = grid_height - 1

def reinit_ant():
    global grid, ant_x_pos, ant_y_pos, ant_direction

    # reinit starting position
    ant_x_pos = int(grid_width / 2)
    ant_y_pos = int(grid_height / 2)
    ant_direction = Directions.ANT_DOWN

    # reinit grid
    for x in range(grid_width):
        for y in range(grid_height):
            grid[x][y] = 0

def ant_loop():
    global grid
    # Ant's current state
    ant_state = grid[ant_x_pos][ant_y_pos]
    # Ant's next direction
    direction = ANTS_RULES[ant_state]

    # Ant makes turn based on the rule at current grid state
    if direction == 'R':
        ant_turn_right()
    elif direction == 'L':
        ant_turn_left()

    # Grid state changes based on current state (advance the state by 1 or return to 0 state)
    if ant_state == len(ANTS_RULES) - 1:
        grid[ant_x_pos][ant_y_pos] = 0
    else:
        grid[ant_x_pos][ant_y_pos] = ant_state + 1

    #print(f"x = {ant_x_pos}, y = {ant_y_pos}, dir = {ant_direction}")

    # Draw the current square
    color_index = grid[ant_x_pos][ant_y_pos]
    grid_canvas.addCell(ant_x_pos, ant_y_pos, COLORS[color_index])

    # Ant moves forward
    ant_move_forward()
    pass


def updateGridSize():
    global grid_width, grid_height, grid
    grid_width = int(CANVAS_WIDTH / resolution)
    grid_height = int(CANVAS_HEIGHT / resolution)

    # create the grid with its proper size
    grid = [[0 for _ in range(grid_height)] for _ in range(grid_width)]

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