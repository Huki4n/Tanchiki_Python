from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QGridLayout, QPushButton

from constancs import Constants


class Ui_MainWindow(object):
  def __init__(self):
    self.tank_pixmap = None
    self.labels = None
    self.MainWindow = None
    self.firstPlayer = None

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

    self.MainWindow.resize(Constants.mapWidth, Constants.mapHeight)

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

  def render_finish_game(self, text, color):
    newCentralWidget = QWidget(self.MainWindow)
    newGridLayout = QGridLayout(newCentralWidget)
    newCentralWidget.setLayout(newGridLayout)

    # Создаем QLabel с текстом
    label = QLabel(text)

    # Настраиваем стиль и выравнивание текста
    label.setStyleSheet(f"color: {color}; font-size: 100px; font-weight: bold;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Выравнивание текста по центру

    # Добавляем QLabel в макет
    close_button = QPushButton('Close')
    close_button.setStyleSheet("font-size: 20px; padding: 10px;")
    close_button.clicked.connect(self.MainWindow.close)  # Подключаем к слоту закрытия окна

    # Добавляем элементы в макет
    newGridLayout.addWidget(label, 0, 0, 1, 1)
    newGridLayout.addWidget(close_button, 1, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

    # Устанавливаем новый центральный виджет
    self.MainWindow.setCentralWidget(newCentralWidget)

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
    for coord in Constants.walls_coordinate:
      row, col = coord
      self.labels[(row, col)].setStyleSheet(f"""
            QLabel {{
                background-image: url('assets/wall.jpg');
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
            }}
        """)