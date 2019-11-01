from utilities.degree_math import *

from PyQt5.QtCore import QThread


class RobotController(QThread):
    def __init__(self, room_size, hardware, cartographer, movement_queue, scanner_draw_points, scanner_draw_lines, scanner_draw_robot, scanner_clear):
        """This class will have no information from the simulation, besides what it passes to Hardware"""
        super(RobotController, self).__init__()
        self.hardware = hardware
        self.cartographer = cartographer

        self.movement_queue = movement_queue

        self.scanner_draw_points  = scanner_draw_points
        self.scanner_draw_lines = scanner_draw_lines
        self.scanner_draw_robot = scanner_draw_robot
        self.scanner_clear = scanner_clear

        self.pos = self.hardware.pos
        self.rotation = self.hardware.rotation

    def run(self):
        """
        We can control the robot in any way we like within this function but we will need to listen to the
        movement queues in order to process user-inputted moves
        """
        scanned_points = self.scan()
        self.update_gui(scanned_points)
        while True:
            if not self.movement_queue.empty():
                command = self.movement_queue.get()
                if command == "forward":
                    self.move(20)
                    if self.movement_queue.empty():
                        scanned_points = self.scan()
                        self.update_gui(scanned_points)

                elif command == "turn clockwise":
                    self.rotate(-45)

                elif command == "turn anticlockwise":
                    self.rotate(45)
                else:
                    raise ValueError("String not recognised")

    def move(self, distance):
        self.hardware.move_forward(distance)
        new_x = self.pos[0] + distance * cos(self.rotation)
        new_y = self.pos[1] + distance * sin(self.rotation)
        self.pos = (new_x, new_y)

    def rotate(self, angle):
        self.hardware.rotate(angle)
        self.rotation += angle

    def scan(self):
        distances = self.hardware.scan()
        points = []
        for angle in distances:
            points.append((self.pos[0] + distances[angle] * cos(angle), self.pos[1] + distances[angle] * sin(angle)))
        return points

    def update_gui(self, points):
        """
        Send all the necessary information to the scanner and discovered map windows
        It is possible to send points of different colour, or lines (using self.scanner_draw_lines)
        """
        self.cartographer.update(self.pos, points)

        self.scanner_draw_points.emit(points, (0, 0, 0))
        self.scanner_draw_robot.emit(self.pos)
