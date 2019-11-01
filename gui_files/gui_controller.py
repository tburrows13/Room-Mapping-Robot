from queue import Queue

from PyQt5.QtCore import pyqtSignal, QObject

from hardware import Hardware
from cartographer import Cartographer
from robot_controller import RobotController


class GUIController(QObject):
    """
    Sets up the different parts that populate the windows
    """
    map_change_pos = pyqtSignal(tuple)
    map_change_rotation = pyqtSignal(float)

    scanner_draw_points = pyqtSignal(list, tuple)
    scanner_draw_lines = pyqtSignal(list)
    scanner_draw_robot = pyqtSignal(tuple)
    scanner_clear = pyqtSignal()

    cartographer_grid_values_callback = pyqtSignal(list)

    def __init__(self, map_window, scanner_window, discovered_map_window):
        super(GUIController, self).__init__()
        self.map_window = map_window
        self.scanner_window = scanner_window
        self.discovered_map_window = discovered_map_window
        self.map_scene = map_window.scene
        self.scanner_scene = scanner_window.scene
        self.discovered_map_scene = discovered_map_window.scene

        self.map_change_pos.connect(self.map_scene.move_robot)
        self.map_change_rotation.connect(self.map_scene.rotate_robot)

        self.scanner_draw_points.connect(self.scanner_scene.draw_points)
        self.scanner_draw_lines.connect(self.scanner_scene.draw_lines)
        self.scanner_draw_robot.connect(self.scanner_scene.draw_robot)
        self.scanner_clear.connect(self.scanner_scene.clear)

        self.cartographer_grid_values_callback.connect(self.discovered_map_scene.update_grid)

        self.controller = None

        self.commands_queue = Queue()

    def run(self, robot_config_values, room_size, rects, start_pos, start_angle, square_size, cartographer_grid):
        self.is_running = True

        self.commands_queue = Queue()

        # Clear map and set sizes for views
        self.map_window.start(room_size)
        self.map_scene.draw_map(room_size, rects, start_pos, start_angle)
        self.scanner_window.start(room_size)
        self.discovered_map_window.start(room_size, square_size)

        # Create some objects for the RobotController to use, as we have all the data here
        hardware = Hardware(start_pos, start_angle, room_size, rects, robot_config_values, self.map_change_pos, self.map_change_rotation)
        cartographer = Cartographer(room_size, square_size, self.cartographer_grid_values_callback, cartographer_grid)

        self.controller = RobotController(room_size, hardware, cartographer, self.commands_queue, self.scanner_draw_points, self.scanner_draw_lines, self.scanner_draw_robot, self.scanner_clear)

        self.controller.start()

    def send_command_forward(self):
        self.commands_queue.put("forward")

    def send_command_rotate_clockwise(self):
        self.commands_queue.put("turn clockwise")

    def send_command_rotate_anticlockwise(self):
        self.commands_queue.put("turn anticlockwise")

