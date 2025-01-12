import sys

from PyQt6.QtWidgets import QApplication

from GameWindow.GameWindow import SignIn

app = QApplication(sys.argv)
main_window = SignIn()
main_window.show()
sys.exit(app.exec())
