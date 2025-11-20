import sys
import re
from enum import IntEnum


from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (
    QFile,
    QTimer
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QLabel,
    QComboBox
)

from Classes.Canvas import GridCanvas, RulesCanvas
from Classes.DialogWindow import WarningDialog
from Classes.ColorPicker import ColorPicker

ant_tick_period: int = 1            # [ms]
ant_repaint_grid_period: int = 20   # [ms]
ant_moves_per_tick: int = 1

CANVAS_WIDTH: int  = 100
CANVAS_HEIGHT: int = 100
resolution: int    = 4

grid_width: int    = int(CANVAS_WIDTH / resolution)
grid_height: int   = int(CANVAS_HEIGHT / resolution)
grid: list[list[int]] = []

# -- global widgets for easier access
steps_count_label: QLabel
grid_canvas: GridCanvas
rules_canvas: RulesCanvas


ant_y_pos: int = 0
ant_x_pos: int = 0
ant_direction: int = 0
ant_stopped: bool = True
ant_steps: int = 0

#RLLRLLRRRLLRLLRL
#RLLLLRRRLLL
ANTS_RULES = ""
"""
COLORS = [
    "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",

    "#A60000", "#FFA500", "#FF6262", "#202072", "#3914AF", "#6A48D7",
    "#008500", "#00CC00", "#67E667", "#A68900", "#FFD300", "#FFDE40",

    "#FF4C4C", "#4CFF4C", "#4C4CFF"
]
"""
COLORS = [
"#001f4d", "#002a66", "#003580", "#004099", "#004bb3",
"#0056cc", "#0061e6", "#006bff", "#0078ff", "#0085ff",
"#0092ff", "#00a0ff", "#00adff", "#00bbff", "#00c8ff",
"#00d5e6", "#00e2cc", "#00f0b3", "#00fd99", "#00ff80"
]

gradient_starting_color: str = "#00FF00"
gradient_ending_color: str = "#0000FF"

class Directions(IntEnum):
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

        # Window title and fix resizing
        self.window.setWindowTitle("Langton's ant")
        self.window.setFixedSize(self.window.size())


        # Create timer for ant_loop() and ant_repaint_grid(), but don't start them yet
        self.ant_loop_timer = QTimer()
        self.ant_loop_timer.setInterval(ant_tick_period)
        self.ant_loop_timer.timeout.connect(ant_loop)
        self.ant_repaint_grid_timer = QTimer()
        self.ant_repaint_grid_timer.setInterval(ant_repaint_grid_period)
        self.ant_repaint_grid_timer.timeout.connect(ant_repaint_grid)


        # create class variables
        self.start_button: QPushButton = QPushButton()
        self.pause_button: QPushButton = QPushButton()
        self.grad_start_button_clr_picker = None
        self.grad_end_button_clr_picker = None
        self.rules_input: QLineEdit = QLineEdit()
        self.speed_combo_box: QComboBox = QComboBox()

        # Setup all widgets
        self.widgets_setup()

    def widgets_setup(self):
        global steps_count_label

        # === Get all widgets from Qt designers layouts
        # Buttons
        self.start_button = self.window.findChild(QPushButton, "btn_start")
        self.pause_button = self.window.findChild(QPushButton, "btn_pause")
        grad_start_col_btn_placeholder = self.window.findChild(QPushButton, "start_color_button")
        grad_end_col_btn_placeholder = self.window.findChild(QPushButton, "end_color_button")

        # Text input (QLineEdit)
        self.rules_input = self.window.findChild(QLineEdit, "rules_input")

        # Label
        steps_count_label = self.window.findChild(QLabel, "label_ant_steps_count")

        # Combo Box
        self.speed_combo_box = self.window.findChild(QComboBox, "speed_combo_box")

        # Canvases
        grid_canvas_placeholder = self.window.findChild(QWidget, "canvas_grid")
        rules_canvas_placeholder = self.window.findChild(QWidget, "canvas_rules")

        # === Assign clicked signals to functions
        if self.start_button:
            self.start_button.clicked.connect(self.start_button_clicked)
        if self.pause_button:
            self.pause_button.clicked.connect(self.pause_button_clicked)
            self.pause_button.setEnabled(False)

        # === Assign initial text to label
        if steps_count_label:
            steps_count_label.setText("0")

        # === Assign speed combo box list items
        if self.speed_combo_box:
            self.speed_combo_box.addItem("1x", 1)
            self.speed_combo_box.addItem("2x", 2)
            self.speed_combo_box.addItem("5x", 5)
            self.speed_combo_box.addItem("10x", 10)
            self.speed_combo_box.addItem("20x", 20)
            self.speed_combo_box.addItem("50x", 50)
            self.speed_combo_box.addItem("100x", 100)
            self.speed_combo_box.addItem("200x", 200)
            self.speed_combo_box.addItem("500x", 500)
            self.speed_combo_box.addItem("1000x", 1000)

            self.speed_combo_box.currentIndexChanged.connect(self.speed_combo_box_changed)

        # === Replacing the placeholders with my custom Canvas class
        if grid_canvas_placeholder:
            global CANVAS_WIDTH, CANVAS_HEIGHT, grid_canvas, COLORS

            layout = grid_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(grid_canvas_placeholder)

            grid_canvas = GridCanvas(
                "#F0F0F0", grid_canvas_placeholder, parent=grid_canvas_placeholder.parentWidget())
            CANVAS_WIDTH = grid_canvas.width()
            CANVAS_HEIGHT = grid_canvas.height()
            updateGridSize()
            grid_canvas.setCellSize(resolution)

            # update COLORS list
            update_colors_list(20)
            grid_canvas.setColors(COLORS)

            layout.removeWidget(grid_canvas_placeholder)
            grid_canvas_placeholder.deleteLater()  # delete placeholder
            layout.insertWidget(index, grid_canvas)

        if rules_canvas_placeholder:
            global rules_canvas
            layout = rules_canvas_placeholder.parentWidget().layout()
            index = layout.indexOf(rules_canvas_placeholder)

            rules_canvas = RulesCanvas(
                "#F0F0F0", rules_canvas_placeholder, parent=rules_canvas_placeholder.parentWidget())
            rules_canvas.setLeftAndRightImages("ui/right_turn_sign.png", "ui/left_turn_sign.png")

            layout.removeWidget(rules_canvas_placeholder)
            rules_canvas_placeholder.deleteLater()  # delete placeholder
            layout.insertWidget(index, rules_canvas)

        if grad_start_col_btn_placeholder:
            layout = grad_start_col_btn_placeholder.parentWidget().layout()
            index = layout.indexOf(grad_start_col_btn_placeholder)

            self.grad_start_button_clr_picker = ColorPicker(
                grad_start_col_btn_placeholder, parent=grad_start_col_btn_placeholder.parentWidget())
            self.grad_start_button_clr_picker.setGradient(
                gradient_starting_color,
                get_middle_color(gradient_starting_color, gradient_ending_color),
                True
            )

            layout.removeWidget(grad_start_col_btn_placeholder)
            grad_start_col_btn_placeholder.deleteLater()  # delete placeholder
            layout.insertWidget(index, self.grad_start_button_clr_picker)

            self.grad_start_button_clr_picker.selectedColorSignal.connect(self.grad_start_btn_clicked)

        if grad_end_col_btn_placeholder:
            layout = grad_end_col_btn_placeholder.parentWidget().layout()
            index = layout.indexOf(grad_end_col_btn_placeholder)

            self.grad_end_button_clr_picker = ColorPicker(
                grad_end_col_btn_placeholder, parent=grad_end_col_btn_placeholder.parentWidget())
            self.grad_end_button_clr_picker.setGradient(
                get_middle_color(gradient_starting_color, gradient_ending_color),
                gradient_ending_color,
                False
            )

            layout.removeWidget(grad_end_col_btn_placeholder)
            grad_end_col_btn_placeholder.deleteLater()  # delete placeholder
            layout.insertWidget(index, self.grad_end_button_clr_picker)

            self.grad_end_button_clr_picker.selectedColorSignal.connect(self.grad_end_btn_clicked)

    def start_button_clicked(self):
        global ant_stopped

        if ant_stopped:
            reinit_ant()                    # reinitiates the ant
            grid_canvas.clearAllCells()     # clear the canvas also

            if self.updateRulesInput():
                #print("Rules: " + ANTS_RULES)
                ant_stopped = False
                self.ant_loop_timer.start()
                self.ant_repaint_grid_timer.start()

                # update COLORS list
                update_colors_list(len(ANTS_RULES))
                grid_canvas.setColors(COLORS)

                rules_canvas.addRules(ANTS_RULES, COLORS) # show rules
                if self.start_button:
                    self.start_button.setText("Stop")
                if self.pause_button:
                    self.pause_button.setEnabled(True)

        else:
            ant_stopped = True
            self.ant_loop_timer.stop()
            self.ant_repaint_grid_timer.stop()
            if self.start_button:
                self.start_button.setText("Start")
            if self.pause_button:
                self.pause_button.setText("Pause")
                self.pause_button.setEnabled(False)

    def pause_button_clicked(self):
        if self.ant_loop_timer.isActive():
            self.ant_loop_timer.stop()
            self.ant_repaint_grid_timer.stop()
            self.pause_button.setText("Play")
        elif not ant_stopped:
            self.ant_loop_timer.start()
            self.ant_repaint_grid_timer.start()
            self.pause_button.setText("Pause")

    def speed_combo_box_changed(self):
        global ant_moves_per_tick
        speed = self.speed_combo_box.currentData()
        ant_moves_per_tick = speed

    def grad_start_btn_clicked(self, selected_color: str):
        global COLORS, gradient_starting_color
        gradient_starting_color = selected_color

        # update COLORS list and widgets
        self.update_colors()
        pass

    def grad_end_btn_clicked(self, selected_color):
        global gradient_ending_color
        gradient_ending_color = selected_color

        # update COLORS list and widgets
        self.update_colors()
        pass

    def update_colors(self):
        global COLORS, rules_canvas

        # update gradient color of ColorPicker buttons
        if self.grad_start_button_clr_picker:
            self.grad_start_button_clr_picker.setGradient(
                gradient_starting_color,
                get_middle_color(gradient_starting_color, gradient_ending_color),
                True
            )

        if self.grad_end_button_clr_picker:
            self.grad_end_button_clr_picker.setGradient(
                get_middle_color(gradient_starting_color, gradient_ending_color),
                gradient_ending_color,
                False
            )

        # update COLORS list
        update_colors_list(len(ANTS_RULES))

        # change colors of the rules and the grid
        if rules_canvas and grid_canvas:
            rules_canvas.addRules(ANTS_RULES, COLORS)
            grid_canvas.setColors(COLORS)

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
def color_gradient(color_start_hex: str, color_end_hex: str, steps: int) -> list[str]:
    c_start = tuple(int(color_start_hex[i:i+2], 16) for i in (1, 3, 5))
    c_end = tuple(int(color_end_hex[i:i+2], 16) for i in (1, 3, 5))

    colors: list[str] = []
    for i in range(steps):
        t = i / (steps - 1)
        r = lin_interpolation(c_start[0], c_end[0], t)
        g = lin_interpolation(c_start[1], c_end[1], t)
        b = lin_interpolation(c_start[2], c_end[2], t)
        colors.append(f"#{r:02X}{g:02X}{b:02X}")

    return colors

def lin_interpolation(a, b, t):
    return int(a + (b - a) * t)

def get_middle_color(color_start_hex: str, color_end_hex: str) -> str:
    color_start = QColor(color_start_hex)
    color_end = QColor(color_end_hex)

    r = (color_start.red()   + color_end.red()) // 2
    g = (color_start.green() + color_end.green()) // 2
    b = (color_start.blue()  + color_end.blue()) // 2

    return f"#{r:02X}{g:02X}{b:02X}"

def update_colors_list(gradient_steps: int):
    global COLORS
    COLORS.clear()
    COLORS = color_gradient(gradient_starting_color, gradient_ending_color, gradient_steps)

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
    global grid, ant_x_pos, ant_y_pos, ant_direction, ant_steps

    # reinit starting position
    ant_x_pos = int(grid_width / 2)
    ant_y_pos = int(grid_height / 2)
    ant_direction = Directions.ANT_DOWN
    ant_steps = 0

    # reinit grid
    for x in range(grid_width):
        for y in range(grid_height):
            grid[x][y] = 0

def ant_loop():
    global ant_moves_per_tick, grid, ant_steps

    for _ in range(ant_moves_per_tick):
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
        grid_canvas.addCell(ant_x_pos, ant_y_pos, color_index)

        # Ant moves forward
        ant_move_forward()

    # Advance steps
    ant_steps += ant_moves_per_tick
    steps_count_label.setText(str(ant_steps))
    pass

def ant_repaint_grid():
    grid_canvas.repaint_grid()

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