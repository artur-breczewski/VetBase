from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication
from PyQt6.QtCore import Qt
from database.connection import get_connection
from gui.main_window import MainWindow
from PyQt6.QtGui import QIcon, QScreen
import bcrypt


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logowanie")
        self.setFixedSize(400, 200)  # Ustawienie stałego rozmiaru okna
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        # Główny widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Pole nazwy użytkownika
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nazwa użytkownika")
        self.main_layout.addWidget(QLabel("Nazwa użytkownika:"))
        self.main_layout.addWidget(self.username_input)

        # Pole hasła
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Hasło")
        self.main_layout.addWidget(QLabel("Hasło:"))
        self.main_layout.addWidget(self.password_input)

        # Przycisk logowania
        self.login_button = QPushButton("Zaloguj")
        self.login_button.clicked.connect(self.handle_login)
        self.main_layout.addWidget(self.login_button)

        # Wiadomość o błędzie
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.main_layout.addWidget(self.error_label)

    def center_window(self):
        """Ustawia okno logowania w centralnej pozycji na ekranie."""
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, self.width(), self.height())

    def handle_login(self):
        """Obsługuje proces logowania użytkownika."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_label.setText("Proszę wprowadzić nazwę użytkownika i hasło.")
            return

        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("SELECT id, password_hash, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            self.error_label.setText("Nieprawidłowy użytkownik lub hasło.")
            return

        user_id, password_hash, role = user

        # Weryfikacja hasła
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            self.open_main_window(user_id, role)
        else:
            self.error_label.setText("Nieprawidłowy użytkownik lub hasło.")

    def open_main_window(self, user_id, role):
        """Otwiera główne okno aplikacji po zalogowaniu."""
        self.main_window = MainWindow(user_id, self.username_input.text(), role)
        self.main_window.show()
        self.close()