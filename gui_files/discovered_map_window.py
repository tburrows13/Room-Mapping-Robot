from math import ceil

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utilities.geometry_utils import mirror_y

DEFAULT_SIZE = (400, 400)
BLACK = (255, 255, 255)


class DiscoveredMapScene(QGraphicsScene):
    def __init__(self):
        super(DiscoveredMapScene, self).__init__()
        self.setItemIndexMethod(QGraphicsScene.NoIndex)  # Optimisation

        self.size = DEFAULT_SIZE

    def setup_grid(self, square_size):
        self.grid = [[]]
        for y in range(ceil(self.size[1]/square_size)):
            for x in range(ceil(self.size[0]/square_size)):
                # (y+1) because mirroring it means that the square is built below the point, not above it
                square = QGraphicsRectItem(*mirror_y((x*square_size, (y+1)*square_size), self.size[1]), square_size, square_size)
                brush = QBrush(QColor(*(0.5*value for value in BLACK)))
                square.setBrush(brush)

                self.addItem(square)
                self.grid[y].append(square)
            self.grid.append([])

    def update_grid(self, grid_values):
        skipped = 0
        for y, row in enumerate(self.grid):
            for x, square in enumerate(row):
                new_color = tuple((round((1-grid_values[y][x])*value) for value in BLACK))
                old_color = square.brush().color().getRgb()[:-1]  # The last element is alpha
                if new_color != old_color:
                    brush = QBrush(QColor(*new_color))
                    square.setBrush(brush)
                    square.update()
                skipped += 1

    def save_image(self, filename):
        """
        Save the image that is currently displayed by the scene into a png file
        """

        source_image = self.sceneRect()

        # Create a target QImage
        image = QImage(source_image.width(), source_image.height(), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        imageF = QRectF(image.rect())

        self.render(painter, imageF, source_image)
        painter.end()

        # Save the image to a file.
        image.save(filename)


class DiscoveredMapView(QGraphicsView):
    def __init__(self):
        super(DiscoveredMapView, self).__init__()

        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setWindowTitle("Discovered Map")
        self.setStyleSheet("border: 0px")
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.scene = DiscoveredMapScene()
        self.setScene(self.scene)

        self.start(DEFAULT_SIZE, 10)

    def start(self, size, square_size):
        self.scene.setSceneRect(0, 0, size[0], size[1])
        self.scene.size = size
        self.setFixedSize(size[0], size[1])
        self.scene.setup_grid(square_size)