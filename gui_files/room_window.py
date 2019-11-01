from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utilities.geometry_utils import mirror_y
from utilities.geometry_utils import rect_to_points

BORDER = 20

DEFAULT_SIZE = (400, 400)


class RoomScene(QGraphicsScene):
    def __init__(self):
        super(RoomScene, self).__init__()
        self.size = DEFAULT_SIZE
        self.position = None

    def draw_map(self, size, rects, start_position, start_angle):  # Add rects
        self.size = size

        # Add the edges
        rects.append([-1, -1, size[0]+1, 2, 0])  # Bottom
        rects.append([-1, -1, 2, size[1]+1, 0])  # Left side
        rects.append([-1, size[1]-1, size[0]+2, 2, 0])  # Top
        rects.append([size[0]-1, -1, 2, size[1]+2, 0])  # Right side

        for rect in rects:
            rect = rect_to_points(*rect)
            rect_item = QGraphicsPolygonItem(QPolygonF(QPointF(*mirror_y(point, self.size[1])) for point in rect))
            rect_item.setBrush(QBrush(QColor(100, 100, 100)))
            pen = QPen()
            pen.setWidth(2)
            rect_item.setPen(pen)
            self.addItem(rect_item)

        self.robot = RobotTriangle(start_position, start_angle, self.size[1])

        self.addItem(self.robot)

    def rotate_robot(self, new_rotation):
        new_robot = self.robot.rotate_position(new_rotation)
        self.removeItem(self.robot)
        self.robot = new_robot
        self.addItem(self.robot)

    def move_robot(self, new_pos):
        self.robot.move_position(new_pos)



class RobotTriangle(QGraphicsPolygonItem):
    def __init__(self, position, rotation, map_height):
        self.position = position
        self.map_height = map_height
        triangle = ((position[0]-5, position[1]+5), (position[0]-5, position[1]-5), (position[0]+10, position[1]))
        polygon = QPolygonF(QPointF(*mirror_y(point, self.map_height)) for point in triangle)
        super(RobotTriangle, self).__init__(polygon)
        self.start_rotate(rotation)

        self.setBrush(QBrush(QColor(200, 30, 30)))

    def move_position(self, new_pos):
        move_by = new_pos[0] - self.position[0], new_pos[1] - self.position[1]
        self.position = new_pos
        mirrored = move_by[0], -move_by[1]
        self.moveBy(*mirrored)

    def start_rotate(self, new_rotation):
        self.setTransformOriginPoint(*mirror_y(self.position, self.map_height))
        self.setRotation(-new_rotation % 360)
        self.setBrush(QBrush(QColor(200, 30, 30)))

    def rotate_position(self, new_rotation):
        # Must create a new one, or else Qt rotation code does not work
        new_self = RobotTriangle(self.position, new_rotation, self.map_height)
        return new_self


class RoomView(QGraphicsView):
    def __init__(self):
        super(RoomView, self).__init__()

        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setWindowTitle("Perfect Visualisation")
        self.setStyleSheet("border: 0px")

        self.scene = RoomScene()
        self.setScene(self.scene)

        self.start(DEFAULT_SIZE)

    def start(self, size):
        self.scene.clear()
        self.scene.setSceneRect(0, 0, size[0], size[1])
        self.scene.size = size
        self.setFixedSize(size[0], size[1])
