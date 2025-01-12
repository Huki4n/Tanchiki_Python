from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QGridLayout

walls_coordinate = [
  (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
  (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
  (1, 5), (2, 5), (3, 5), (4, 5),
  (1, 7), (2, 7), (3, 7), (4, 7),
  (1, 9), (2, 9), (3, 9), (4, 9), (5, 9),
  (1, 11), (2, 11), (3, 11), (4, 11), (5, 11),
  (5, 5),
  (5, 7),
  (7, 2), (7, 3),
  (7, 9), (7, 10),
  (9, 1), (10, 1), (11, 1), (12, 1),
  (9, 3), (10, 3), (11, 3), (12, 3),
  (8, 5), (9, 5), (10, 5), (11, 5),
  (9, 6),
  (8, 7), (9, 7), (10, 7), (11, 7),
  (9, 9), (10, 9), (11, 9), (12, 9),
  (9, 11), (10, 11), (11, 11), (12, 11),
]


class Ui_MainWindow(object):
  def __init__(self):
    self.tank_pixmap = None
    self.labels = None
    self.MainWindow = None
    self.firstPlayer = None
    self.MainWindow = None

    self.mapWidth, self.mapHeight = 830, 780
    self.tankWidth, self.tankHeight = 54, 48
    self.speed = 4

  def setupUi(self, MainWindow):
    self.MainWindow = MainWindow
    self.renderMap()

  def renderMap(self):
    self.base_render()

    self.add_blocks_to_layout()
    self.add_walls_to_map()

  def base_render(self):
    if not self.MainWindow.objectName():
      self.MainWindow.setObjectName(u"MainWindow")

    self.MainWindow.resize(self.mapWidth, self.mapHeight)

    self.centralWidget = QWidget(self.MainWindow)
    self.centralWidget.setObjectName(u"centralwidget")

    self.centralWidget.setEnabled(True)
    self.centralWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    self.gridLayout_2 = QGridLayout(self.centralWidget)

    self.gridLayout_2.setObjectName(u"gridLayout_2")

    self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
    self.gridLayout_2.setSpacing(0)

    self.centralWidget.setLayout(self.gridLayout_2)
    self.MainWindow.setCentralWidget(self.centralWidget)

  def add_blocks_to_layout(self):
    self.labels = dict()

    for row in range(14):
      for col in range(13):
        label = QLabel(self.centralWidget)
        label.setStyleSheet(f"""
                 QLabel {{
                     background-image: url('assets/empty_dark.jpg');
                     background-repeat: no-repeat;
                     background-position: center;
                     background-size: 48px 48px;
                 }}
               """)

        self.gridLayout_2.addWidget(label, row, col)
        self.labels[(row, col)] = label

  def add_walls_to_map(self):
    for coord in walls_coordinate:
      row, col = coord
      self.labels[(row, col)].setStyleSheet(f"""
            QLabel {{
                background-image: url('assets/wall.jpg');
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
                border: 1px solid red;
            }}
        """)