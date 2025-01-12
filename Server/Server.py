import socket
import pickle
from threading import Thread

BUFFER_SIZE = 1024  # 1kb


class ClientHandler(Thread):
  mapWidth, mapHeight = 830, 780
  tankWidth, tankHeight = 54, 48

  def __init__(self, connection: socket.socket, players: set['ClientHandler']):
    super().__init__(daemon=True)
    self.players = players
    self.player_id = len(players)
    self.address: tuple = connection.getpeername()
    self.packet_template = {'msgtype': '', 'body': ''}
    self.connection = connection
    self.position = self.set_player_position()
    self.start()

  def set_player_position(self):
    if not self.players:
      return 1, self.mapHeight - self.tankHeight
    return self.mapWidth - self.tankWidth, 1

  def send_player_info(self):
    print('send player info')
    packet = {
      'msgtype': 'player_info',
      'body': {
        'id': self.player_id,
        'position': self.position
      }
    }

    for player in self.players:
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

    while True:
      data_in_bytes = self.recv()
      data: dict = pickle.loads(data_in_bytes)

      match data.get('msgtype'):
        case 'position':
          self.update_player_position(data)

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
    while True:
      print('Waiting for connection')
      client_socket, client_address = self.sock.accept()
      print('Connection from', client_address)
      self.players.add(ClientHandler(client_socket, self.players))


server = Server('localhost', 9000)
server.serve_forever()
