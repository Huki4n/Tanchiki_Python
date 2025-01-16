import pickle
import socket
from queue import SimpleQueue
from threading import Thread

BUFFER_SIZE = 1024


class SocketCommunication:
  STOP = b'///'

  def __init__(self, host, port, gui_communication):
    self.send_data_queue = SimpleQueue()
    self.gui_communication = gui_communication

    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')
    self.sock.connect((host, port))
    print('Socket connected')

    Thread(target=self.send_data_stream_daemon, daemon=True).start()
    Thread(target=self.recv_data_stream_daemon, daemon=True).start()

  def recv(self) -> bytearray:
    result = bytearray()
    while True:
      data: bytes = self.sock.recv(BUFFER_SIZE)
      result.extend(data)
      if result.endswith(SocketCommunication.STOP):
        break
    return result[:-3]

  def send(self, msg: bytes):
    self.sock.send(msg + SocketCommunication.STOP)

  def send_data_stream_daemon(self):
    while True:
      # wait the data from GUI which we need to send to server
      msgtype, body = self.send_data_queue.get(block=True)
      # form the "packet" (our protocol) for sending to server
      packet = dict(msgtype=msgtype, body=body)
      # send it in BYTES by using dumps -> using serialization
      self.send(pickle.dumps(packet))

  def recv_data_stream_daemon(self):
    while True:
      # get the answer from server which we need to send to GUI
      answer_in_bytes: bytes = self.recv()
      # convert the bytes into the object by using loads -> deserealization
      data: dict = pickle.loads(answer_in_bytes)
      # extract the information from it, choose what to do
      msgtype = data['msgtype']
      body = data['body']

      match msgtype:
        case 'position':
          player_id, position, angle = body
          x, y = position
          self.gui_communication.game_updating_signal.emit(player_id, x, y, angle)
        case 'player_info':
          player_id = body['id']
          position = body['position']
          self.gui_communication.player_updating_signal.emit(player_id, position)
        case 'bullet_hit':
          hit_type = body['hit_type']
          target_id = body['target_id']
          shooter_id = body['shooter_id']

          self.gui_communication.bullet_hit_signal.emit(hit_type, target_id, shooter_id)
        case 'bullet_move':
          x, y, angle, player_id = body
          self.gui_communication.bullet_move_signal.emit(player_id, angle, x, y)
