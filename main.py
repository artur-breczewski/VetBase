import sys
from PyQt6.QtWidgets import QApplication
from gui.login_window import LoginWindow  # Importujemy okno logowania

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Tworzymy okno logowania
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())