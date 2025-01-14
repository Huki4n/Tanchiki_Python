from PyQt6.QtCore import QTimer, QRect, Qt
from PyQt6.QtGui import QPainter, QPixmap, QTransform
from PyQt6.QtWidgets import QLabel
import math

from ui_main import walls_coordinate


class Bullet:
  bulletWidth, bulletHeight = 10, 6
  bulletSize = (bulletWidth, bulletHeight)
  mapWidth, mapHeight = 830, 780
  tankWidth, tankHeight = 54, 48

  def __init__(self, parent, start_pos, angle, players, on_hit_callback):
    """
    Инициализация снаряда.

    :param parent: Родительский виджет (игровое поле).
    :param start_pos: Начальная позиция (x, y).
    :param angle: Угол движения снаряда.
    :param players: Список танков (словарь {player_id: QLabel}).
    :param on_hit_callback: Функция для вызова при попадании (в танк или стену).
    """

    self.parent = parent
    self.angle = angle
    self.speed = 20
    self.players = players
    self.on_hit_callback = on_hit_callback

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
    self.timer = QTimer(parent)
    self.timer.timeout.connect(self.bullet_move)
    self.timer.start(30)

  def bullet_move(self):

    """Движение снаряда."""
    dx = self.speed * math.cos(math.radians(self.angle))
    dy = self.speed * math.sin(math.radians(self.angle))

    current_pos = self.label.pos()
    new_x = int(round(current_pos.x() + dx))
    new_y = int(round(current_pos.y() + dy))

    if not self.can_bullet_move(new_x, new_y) or self.check_collision(new_x, new_y):
      self.destroy()
      return

    self.label.move(new_x, new_y)

  def can_bullet_move(self, x, y):
    """Проверка, может ли снаряд двигаться (не выходит за пределы карты)."""
    return (0 <= x <= self.mapWidth - self.bulletWidth and
            0 <= y <= self.mapHeight - self.bulletHeight)

  def check_collision(self, x, y):
    """Проверка столкновений с танками или стенами."""
    # Проверка столкновения со стенами
    cell_width = self.mapWidth / 13
    cell_height = self.mapHeight / 14

    col = math.floor(x / cell_width)
    row = math.floor(y / cell_height)

    if (row, col) in walls_coordinate:
      self.on_hit_callback("wall", None)
      return True

    # Проверка столкновения с танками
    bullet_rect = QRect(x, y, *self.bulletSize)
    for player_id, player_label in self.players.items():
      if bullet_rect.intersects(player_label.geometry()):
        self.on_hit_callback("player", player_id)
        return True

    return False

  def destroy(self):
    """Удаление снаряда."""
    self.timer.stop()
    self.label.deleteLater()
