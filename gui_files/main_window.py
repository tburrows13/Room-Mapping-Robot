import json

from PyQt5.QtWidgets import *

from gui_files.room_window import RoomView
from gui_files.scanner_window import ScannerView
from gui_files.discovered_map_window import DiscoveredMapView
from gui_files.gui_controller import GUIController
from gui_files.config_dialog import ConfigDialog
from gui_files.scenario_loader import ScenarioLoader
from database_manager import DatabaseManager


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        layout = QVBoxLayout()

        upper_windows = QHBoxLayout()
        lower_windows = QHBoxLayout()

        map_window = RoomView()
        scanner = ScannerView()
        discovered_map = DiscoveredMapView()
        upper_windows.addWidget(map_window)
        upper_windows.addWidget(scanner)
        upper_windows.addWidget(discovered_map)

        buttons = QHBoxLayout()

        self.start_button = QPushButton("Start")
        buttons.addWidget(self.start_button)

        self.config_button = QPushButton("Setup")
        buttons.addWidget(self.config_button)

        self.load_scenario_button = QPushButton("Load Scenario")
        buttons.addWidget(self.load_scenario_button)

        self.save_button = QPushButton("Save Scenario")
        buttons.addWidget(self.save_button)

        export_button = QPushButton("Export Map")
        buttons.addWidget(export_button)

        self.forward_button = QPushButton("Forward")
        buttons.addWidget(self.forward_button)

        self.anticlockwise_button = QPushButton("Turn Anti-Clockwise")
        buttons.addWidget(self.anticlockwise_button)

        self.clockwise_button = QPushButton("Turn Clockwise")
        buttons.addWidget(self.clockwise_button)

        lower_windows.addLayout(buttons)
        layout.addLayout(upper_windows)
        layout.addLayout(lower_windows)
        self.setLayout(layout)

        self.setWindowTitle("Room Scanner")

        self.forward_button.setDisabled(True)
        self.anticlockwise_button.setDisabled(True)
        self.clockwise_button.setDisabled(True)

        self.controller = GUIController(map_window, scanner, discovered_map)
        self.start_button.clicked.connect(self.start_GUI_controller)
        self.forward_button.clicked.connect(self.controller.send_command_forward)
        self.clockwise_button.clicked.connect(self.controller.send_command_rotate_clockwise)
        self.anticlockwise_button.clicked.connect(self.controller.send_command_rotate_anticlockwise)
        self.save_button.clicked.connect(self.save_scenario)
        export_button.clicked.connect(self.export_map)
        self.config_button.clicked.connect(self.open_config_window)
        self.load_scenario_button.clicked.connect(self.open_load_window)

        self.database = DatabaseManager()

        self.start_pos = None
        self.previous_start_pos = None
        self.square_size = None
        self.open_config_window(close_immediately=True)  # So that the default settings are retrieved and stored

    def open_config_window(self, close_immediately=False):
        self.dialog = ConfigDialog(self.previous_start_pos, self.square_size)
        self.dialog.setModal(True)
        self.dialog.finished.connect(self.get_config_window_info)
        if close_immediately:
            self.dialog.close()
        else:
            self.dialog.open()

    def get_config_window_info(self, finish_code):
        if finish_code == 1:
            # Get the data back from the window
            # If it doesn't exist, disable the start button
            self.robot_name = self.dialog.robot_layout.robot_select_dropdown.currentText()
            self.room_name = self.dialog.room_layout.room_select_dropdown.currentText()
            start_pos_x = self.dialog.room_layout.start_pos_x.text()
            start_pos_y = self.dialog.room_layout.start_pos_y.text()
            square_size = self.dialog.square_size_text_edit.text()

            if self.room_name is None or self.room_name is None or square_size == "" or start_pos_x == "" or start_pos_y == "":
                self.start_button.setDisabled(True)
            else:
                self.start_button.setDisabled(False)
                self.start_pos = int(start_pos_x), int(start_pos_y)
                self.previous_start_pos = int(start_pos_x), int(start_pos_y)
                self.start_angle = 90
                self.square_size = int(square_size)
                self.cartographer_grid = None
        else:
            self.start_button.setDisabled(True)

    def open_load_window(self):
        dialog = ScenarioLoader()
        dialog.exec_()

        scenario_name = dialog.scenario_select.currentText()
        if scenario_name == "":
            return

        scenario_data = self.database.get_scenario_by_name(scenario_name)
        self.robot_name, self.room_name, self.square_size, self.cartographer_grid, robot_x, robot_y, self.start_angle = scenario_data
        self.cartographer_grid = json.loads(self.cartographer_grid)
        self.start_pos = robot_x, robot_y
        self.previous_start_pos = None
        self.start_GUI_controller()

    def start_GUI_controller(self):
        if self.start_button.text() == "Start":
            # Change it to a stop button
            self.start_button.setText("Stop")

            # Disable/enable buttons
            self.forward_button.setDisabled(False)
            self.anticlockwise_button.setDisabled(False)
            self.clockwise_button.setDisabled(False)
            self.config_button.setDisabled(True)
            self.load_scenario_button.setDisabled(True)
            self.forward_button.repaint()
            self.anticlockwise_button.repaint()
            self.clockwise_button.repaint()
            self.config_button.repaint()
            self.load_scenario_button.repaint()

            # Load all data from the database
            robot_data = self.database.get_robot_by_name(self.robot_name)
            rects = self.database.get_rects_by_room_name(self.room_name)
            room_size = self.database.get_room_width_height_by_room_name(self.room_name)
            self.controller.run(robot_data, room_size, rects, self.start_pos, self.start_angle, self.square_size, self.cartographer_grid)

        elif self.start_button.text() == "Stop":
            self.start_button.setText("Start")

            # Disable/enable buttons
            self.forward_button.setDisabled(True)
            self.anticlockwise_button.setDisabled(True)
            self.clockwise_button.setDisabled(True)
            self.config_button.setDisabled(False)
            self.load_scenario_button.setDisabled(False)
            self.forward_button.repaint()
            self.anticlockwise_button.repaint()
            self.clockwise_button.repaint()
            self.config_button.repaint()
            self.load_scenario_button.repaint()

    def save_scenario(self):
        name_getter = QDialog()
        question = QLabel("Input Name:")
        line_edit = QLineEdit()
        submit = QPushButton("Confirm")
        submit.setDefault(True)
        submit.clicked.connect(name_getter.close)

        layout = QHBoxLayout()
        layout.addWidget(question)
        layout.addWidget(line_edit)
        layout.addWidget(submit)
        name_getter.setLayout(layout)
        name_getter.exec_()

        name = line_edit.text()
        if name == "":
            return

        cartographer_grid = self.controller.controller.cartographer.grid
        robot_x, robot_y = self.controller.controller.hardware.pos
        robot_angle = self.controller.controller.hardware.rotation

        self.database.add_scenario(name, self.room_name, self.robot_name, self.square_size, cartographer_grid, robot_x, robot_y, robot_angle)

    def export_map(self):
        filename = QFileDialog.getSaveFileName(filter="Images (*.png)")[0]
        if filename == "":
            return
        self.controller.discovered_map_scene.save_image(filename)

    def close(self):
        self.database.connection.close()
        super(MainWindow, self).close()


def main():
    import sys
    global app, mainWindow  # Stops a SEGFAULT
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
