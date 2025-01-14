import math
from dataclasses import dataclass

from PyQt6.QtCore import pyqtSlot, Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QTransform, QPixmap
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton

from Bullet.Bullet import Bullet
from Client.Client import SocketCommunication
from Signals.Signals import GUICommunication
from ui_main import Ui_MainWindow, walls_coordinate

BUFFER_SIZE = 1024


@dataclass(frozen=True)
class Player:
  id: int or None
  position: tuple or None


class SignIn(QWidget):
  def __init__(self):
    super().__init__()
    self.username = ''
    self.setWindowTitle('Choose the room')

    self.player = {"id": None, "position": None}

    self.chat_window = None

    self.gui_communication = GUICommunication()
    self.gui_communication.player_updating_signal.connect(self.signin_player_updating_logic)

    self.socket_communication = SocketCommunication('127.0.0.1', 9000, self.gui_communication)

    layout = QVBoxLayout()
    self.status = QLabel()
    self.input_field = QLineEdit()
    self.input_field.setPlaceholderText("Enter your name")
    btn_send: QPushButton = QPushButton('Send')

    layout.addWidget(self.status)
    layout.addWidget(self.input_field)
    layout.addWidget(btn_send)

    btn_send.clicked.connect(self.set_username)

    self.setLayout(layout)
    self.show()

  @pyqtSlot(int, tuple)
  def signin_player_updating_logic(self, player_id, position):
    self.player['id'] = player_id
    self.player['position'] = position

  @pyqtSlot()
  def set_username(self):
    username = self.input_field.text()
    if not username.isalnum():
      self.status.setText("Wrong username")
      return
    self.username = username
    self.chat_window = MainWindow(username, self.gui_communication, self.socket_communication, self.player, self)
    self.gui_communication.player_updating_signal.disconnect(self.signin_player_updating_logic)
    self.hide()


class MainWindow(QMainWindow, Ui_MainWindow):

  def __init__(self, username, gui_communication, socket_communication, player, parent_window: SignIn):
    super().__init__()
    self.setupUi(self)
    self.setWindowTitle(username)
    self.username = username
    self.parent_window = parent_window
    self.player = player

    self.gui_communication = gui_communication
    self.socket_communication = socket_communication

    self.pressed_keys = set()
    self.players = {}
    self.tank_pixmaps = {}
    self.bullets = []

    self.shoot_delay = 1000
    self.can_shoot = True

    self.current_direction = "top"

    self.directions = {
      frozenset([Qt.Key.Key_W]): "top",
      frozenset([Qt.Key.Key_S]): "bottom",
      frozenset([Qt.Key.Key_A]): "left",
      frozenset([Qt.Key.Key_D]): "right",
    }

    self.gui_communication.player_updating_signal.connect(self.player_updating_logic)
    self.gui_communication.game_updating_signal.connect(self.game_updating_logic)

    self.add_player_to_map(self.player['position'], self.player['id'])

    if self.player['id'] == 1:
      self.add_player_to_map((1, self.mapHeight - self.tankHeight), 0)

    self.shoot_timer = QTimer()
    self.shoot_timer.timeout.connect(self.reset_shoot_flag)
    self.shoot_timer.start(self.shoot_delay)
    #
    self.show()

  def reset_shoot_flag(self):
    self.can_shoot = True

  @pyqtSlot(int, tuple)
  def player_updating_logic(self, player_id, position):
    self.add_player_to_map(position, player_id)

  @pyqtSlot(int, int, int, int)
  def game_updating_logic(self, player_id, x, y, angle):
    if player_id in self.players:
      self.players[player_id].move(x, y)
      self.rotate_tank(self.players[player_id], player_id, angle)

  @pyqtSlot()
  def game_updater(self):
    allowed_keys = {Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D}
    self.pressed_keys = {key for key in self.pressed_keys if key in allowed_keys}

    direction = self.directions.get(frozenset(self.pressed_keys))
    player_id = self.player['id']  # Получаем ID текущего игрока

    if direction:
      x, y, angle = self.move_player(player_id, direction)  # Передаем player_id в move_player
      self.socket_communication.send_data_queue.put(('position', (player_id, (x, y), angle)))  # Отправляем также player_id

  @pyqtSlot(QKeyEvent)
  def keyPressEvent(self, event: QKeyEvent):
    self.pressed_keys.add(event.key())

    if event.key() == Qt.Key.Key_Space:
      if self.can_shoot:
        self.shoot_bullet(self.player['id'])

    self.game_updater()

  @pyqtSlot(QKeyEvent)
  def keyReleaseEvent(self, event: QKeyEvent):
    self.pressed_keys.discard(event.key())
    self.game_updater()

  def add_player_to_map(self, position, player_id):
    x, y = position
    tank_pixmap = QPixmap('assets/tank.png').scaled(self.tankWidth, self.tankHeight)

    if player_id == 1:
      transform = QTransform().rotate(180)
      tank_pixmap = tank_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

    self.tank_pixmaps[player_id] = tank_pixmap

    player_label = QLabel(self.centralWidget)
    player_label.setStyleSheet("QLabel { border: 1px solid red; }")
    player_label.setGeometry(x, y, self.tankWidth, self.tankHeight)
    player_label.setPixmap(tank_pixmap)
    player_label.show()
    player_label.setScaledContents(True)

    self.players[player_id] = player_label

  def move_player(self, player_id, direction):
    angle = 0

    if player_id == 1:
      angle = 180

    if player_id not in self.players:
      return None

    directions = {
      'left': (-self.speed, 0, -90 if player_id == 0 else 90),  # Угол 180 градусов для левого направления
      'right': (self.speed, 0, 90 if player_id == 0 else -90),  # Угол 0 градусов для правого направления
      'top': (0, -self.speed, 0 if player_id == 0 else 180),  # Угол 270 градусов для верхнего направления
      'bottom': (0, self.speed, 180 if player_id == 0 else 0),  # Угол 90 градусов для нижнего направления
    }

    player_label = self.players[player_id]
    currPos = player_label.pos()

    if direction in directions:
      dx, dy, angle = directions[direction]
      newX = currPos.x() + dx
      newY = currPos.y() + dy

      if self.can_move(newX, newY):

        # Меняем направление танка, только если оно изменилось
        if self.current_direction != direction:
          self.current_direction = direction
          self.rotate_tank(player_label, player_id, angle)

        return newX, newY, angle

    return currPos.x(), currPos.y(), angle

  # HELPER METHODS
  def can_move(self, newX, newY):
    cellWidth = self.mapWidth / 13
    cellHeight = self.mapHeight / 14

    left = newX
    right = newX + self.tankWidth
    top = newY
    bottom = newY + self.tankHeight

    points_to_check = [
      (math.floor(top / cellHeight), math.floor(left / cellWidth)),
      (math.floor(top / cellHeight), math.floor(right / cellWidth)),
      (math.floor(bottom / cellHeight), math.floor(left / cellWidth)),
      (math.floor(bottom / cellHeight), math.floor(right / cellWidth)),
    ]

    for point in points_to_check:
      if point in walls_coordinate:
        return False

    return (0 <= newX <= self.mapWidth - self.tankWidth
            and 0 <= newY <= self.mapHeight - self.tankHeight)

  def rotate_tank(self, player_label, player_id, angle):
    transform = QTransform().rotate(angle)
    rotated_pixmap = self.tank_pixmaps[player_id].transformed(transform, Qt.TransformationMode.SmoothTransformation)
    player_label.setPixmap(rotated_pixmap)

  def shoot_bullet(self, player_id):
    """Создание снаряда."""
    if player_id not in self.players:
      return

    # Получаем позицию танка
    player_label = self.players[player_id]
    player_pos = player_label.pos()

    bullet_directions = {
      "right": [(
        player_pos.x() + self.tankWidth - Bullet.bulletWidth // 2,
        player_pos.y() + self.tankHeight // 2,
      ), 0],
      "bottom": [(
        player_pos.x() + self.tankWidth // 2 - Bullet.bulletWidth // 4,
        player_pos.y() + self.tankHeight - Bullet.bulletHeight * 2,
      ), 90],
      "left": [(
        player_pos.x() + Bullet.bulletWidth // 2,
        player_pos.y() + self.tankHeight // 2,
      ), -180],
      "top": [(
        player_pos.x() + self.tankWidth // 2 - Bullet.bulletWidth // 4,
        player_pos.y(),
      ), -90],
    }

    start_pos = bullet_directions[self.current_direction][0]
    angle = bullet_directions[self.current_direction][1]

    # Создание снаряда
    bullet = Bullet(
      parent=self.centralWidget,
      start_pos=start_pos,
      angle=angle,
      players=self.players,
      on_hit_callback=self.handle_bullet_hit,
    )

    self.bullets.append(bullet)

  def handle_bullet_hit(self, hit_type, target_id):
    if hit_type == "wall":
      print("Bullet hit a wall.")
    elif hit_type == "player":
      print(f"Bullet hit player {target_id}.")
