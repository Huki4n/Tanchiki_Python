from PyQt6.QtCore import QObject, pyqtSignal


class GUICommunication(QObject):
  player_updating_signal = pyqtSignal(int, tuple)
  game_updating_signal = pyqtSignal(int, int, int, int)
