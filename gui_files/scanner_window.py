from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utilities.geometry_utils import mirror_y

DEFAULT_SIZE = (400, 400)
BORDER = 5


class ScannerScene(QGraphicsScene):
    def __init__(self):
        super(ScannerScene, self).__init__()
        self.setItemIndexMethod(QGraphicsScene.NoIndex)  # Optimisation
        self.size = DEFAULT_SIZE
        self.points = []
        for _ in range(720):
            point = QGraphicsEllipseItem()
            point.setBrush(QBrush(QColor(0, 0, 0)))
            self.addItem(point)
            self.points.append(point)
        self.robot = QGraphicsEllipseItem()
        self.robot.setBrush(QBrush(QColor(200, 30, 30)))
        self.addItem(self.robot)

    def draw_points(self, points):
        for i, point in enumerate(points):
            point = mirror_y(point, self.size[1])
            point_pos = (point[0]-3, point[1]-3, 6, 6)
            self.points[i].setRect(*point_pos)

    def draw_robot(self, position):
        self.robot.setRect(*mirror_y((position[0]-5, position[1]+5), self.size[1]), 10, 10)

    def draw_lines(self, lines):
        for line in lines:
            qline = QGraphicsLineItem(*mirror_y(line[0], self.size[1]), *mirror_y(line[1], self.size[1]))
            self.addItem(qline)


class ScannerView(QGraphicsView):
    def __init__(self):
        super(ScannerView, self).__init__()
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setStyleSheet("border: 0px")
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.scene = ScannerScene()
        self.setScene(self.scene)

        self.start(DEFAULT_SIZE)

    def start(self, size):
        self.scene.setSceneRect(-BORDER, -BORDER, size[0] + BORDER, size[1] + BORDER)
        self.scene.size = size

        self.setFixedSize(size[0]+2*BORDER, size[1]+2*BORDER)
