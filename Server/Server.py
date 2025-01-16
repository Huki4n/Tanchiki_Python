import math
import socket
import pickle
from threading import Thread

from PyQt6.QtCore import QRect

from Bullet.Bullet import Bullet
from constancs import Constants

BUFFER_SIZE = 1024  # 1kb


class ClientHandler(Thread):
  def __init__(self, connection: socket.socket, players: set['ClientHandler']):
    super().__init__(daemon=True)
    self.players = players
    self.player_id = len(players)
    self.address: tuple = connection.getpeername()
    self.packet_template = {'msgtype': '', 'body': ''}
    self.connection = connection
    self.position = self.set_player_position()
    self.start()

  def update_bullet_position(self, data):
    """Обновление позиции пули и проверка на попадание."""
    x, y, angle, player_id = data['body']

    # Проверяем столкновения с игроками
    bullet_rect = QRect(x, y, Bullet.bulletWidth, Bullet.bulletHeight)

    for player in self.players:
      if player.player_id != player_id:
        player_rect = QRect(
          player.position[0], player.position[1],
          Constants.tankWidth, Constants.tankHeight
        )

        if bullet_rect.intersects(player_rect):
          self.notify_hit("player", player.player_id, player_id)
          return

    # Проверяем столкновения со стенами
    col = math.floor(x / (Constants.mapWidth / 13))
    row = math.floor(y / (Constants.mapHeight / 14))

    if (row, col) in Constants.walls_coordinate:
      self.notify_hit("wall", None, player_id)
      return

    if not self.can_bullet_move(x, y):
      self.notify_hit("border", None, player_id)
      return

    # Если нет попадания, обновляем пулю
    for player in self.players:
      player.send(pickle.dumps(data))

  def notify_hit(self, hit_type, target_id, shooter_id):
    """Уведомление всех игроков о попадании."""
    packet = {
      "msgtype": "bullet_hit",
      "body": {
        "hit_type": hit_type,
        "target_id": target_id,
        "shooter_id": shooter_id,
      },
    }

    for player in self.players:
      player.send(pickle.dumps(packet))

  def set_player_position(self):
    if not self.players:
      return 1, Constants.mapHeight - Constants.tankHeight
    return Constants.mapWidth - Constants.tankWidth, 1

  def send_player_info(self):
    print('send player info')

    packet = {
      'msgtype': 'player_info',
      'body': {
        'id': self.player_id,
        'position': self.position
      }
    }

    for player in list(self.players):
      player.send(pickle.dumps(packet))

  def update_player_position(self, data):
    player_id, position, angle = data['body']
    x, y = position
    self.position = (x, y)

    for player in self.players:
      data_in_bytes: bytes = pickle.dumps(data)
      player.send(data_in_bytes)

  def run(self):
    self.send_player_info()

    try:
      while True:
        data_in_bytes = self.recv()
        data: dict = pickle.loads(data_in_bytes)

        match data.get('msgtype'):
          case 'position':
            self.update_player_position(data)
          case "bullet_move":
            self.update_bullet_position(data)

    except (ConnectionResetError, BrokenPipeError):
      print(f"Connection lost with player {self.player_id}.")
      self.players.remove(self)
    finally:
      self.connection.close()

      # match data.get('msgtype'):

  def recv(self) -> bytearray:
    result = bytearray()
    while True:
      data: bytes = self.connection.recv(BUFFER_SIZE)
      result.extend(data)
      if result.endswith(Server.STOP):
        break
    return result[:-3]

  def send(self, msg: bytes):
    self.connection.send(msg + Server.STOP)

  def can_bullet_move(self, x, y):
    """Проверка, может ли снаряд двигаться (не выходит за пределы карты)."""
    return (0 <= x <= Constants.mapWidth - Bullet.bulletWidth and
            0 <= y <= Constants.mapHeight - Bullet.bulletHeight)


class Server:
  STOP = b'///'

  def __init__(self, host, port):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')
    self.sock.bind((host, port))
    print('Socket binded')
    self.sock.listen(1)
    print('Socket now listening')
    self.players = set()

  def serve_forever(self):
    try:
      while True:
        print('Waiting for connection')
        client_socket, client_address = self.sock.accept()
        print('Connection from', client_address)
        self.players.add(ClientHandler(client_socket, self.players))
    except KeyboardInterrupt:
      print("\nShutting down server.")
    finally:
      self.sock.close()


server = Server('localhost', 9000)
server.serve_forever()
