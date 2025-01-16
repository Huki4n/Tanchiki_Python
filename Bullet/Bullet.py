from PyQt6.QtCore import QTimer, QRect, Qt
from PyQt6.QtGui import QPainter, QPixmap, QTransform
from PyQt6.QtWidgets import QLabel
import math


class Bullet:
  bulletWidth, bulletHeight = 10, 6
  bulletSize = (bulletWidth, bulletHeight)

  def __init__(self, parent, start_pos, angle, players, player_id, socket_communication, current_player_bullet):
    """
    Инициализация снаряда.

    :param parent: Родительский виджет (игровое поле).
    :param start_pos: Начальная позиция (x, y).
    :param angle: Угол движения снаряда.
    :param players: Список танков (словарь {player_id: QLabel}).
    """

    self.socket_communication = socket_communication
    self.parent = parent
    self.angle = angle
    self.speed = 20
    self.players = players
    self.player_id = player_id
    self.current_player_bullet = current_player_bullet

    # Создание QLabel для снаряда
    pixmap = QPixmap("assets/bullet.png")

    # Поворачиваем изображение на заданный угол
    transform = QTransform().rotate(angle)
    rotated_pixmap = pixmap.transformed(transform, mode=Qt.TransformationMode.SmoothTransformation)

    # Создание QLabel для отображения снаряда
    self.label = QLabel(self.parent)
    self.label.setPixmap(rotated_pixmap)
    self.label.setGeometry(start_pos[0], start_pos[1], rotated_pixmap.width(), rotated_pixmap.height())
    self.label.setStyleSheet("background-color: transparent;")
    self.label.show()

    # Таймер для движения
    if self.current_player_bullet:
      self.timer = QTimer(parent)
      self.timer.timeout.connect(self.bullet_move)
      self.timer.start(30)

  def bullet_move(self):
    """Отправка данных о движении пули на сервер."""
    dx = self.speed * math.cos(math.radians(self.angle))
    dy = self.speed * math.sin(math.radians(self.angle))

    current_pos = self.label.pos()
    new_x = int(round(current_pos.x() + dx))
    new_y = int(round(current_pos.y() + dy))

    # Отправляем обновленную позицию на сервер
    if self.current_player_bullet:
      self.socket_communication.send_data_queue.put(('bullet_move', (new_x, new_y, self.angle, self.player_id,)))

    self.label.move(new_x, new_y)

  def destroy(self):
    """Удаление снаряда."""
    if self.current_player_bullet:
      self.timer.stop()
    self.label.deleteLater()
