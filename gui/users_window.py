from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, QMessageBox, QComboBox, QHeaderView
)
from PyQt6.QtGui import QIcon, QGuiApplication
from database.operations import create_user, delete_user, get_all_users
from PyQt6.QtCore import Qt
from passlib.hash import bcrypt

class UsersWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Zarządzanie użytkownikami")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony
        self.username = username

        # Wyśrodkowanie okna na ekranie
        self.center_window()

        # Main Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Navigation Buttons
        self.nav_layout = QHBoxLayout()
        self.main_layout.addLayout(self.nav_layout)

        self.add_user_button = QPushButton("Dodaj użytkownika")
        self.add_user_button.clicked.connect(self.open_add_user_dialog)
        self.nav_layout.addWidget(self.add_user_button)

        self.delete_user_button = QPushButton("Usuń użytkownika")
        self.delete_user_button.setEnabled(False)
        self.delete_user_button.clicked.connect(self.delete_user)
        self.nav_layout.addWidget(self.delete_user_button)

        # Users Table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["ID", "Nazwa użytkownika", "Rola", "Data utworzenia"])
        self.style_table()
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Enable row selection
        self.users_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)  # Only one row selectable
        self.users_table.cellClicked.connect(self.toggle_delete_button)
        self.main_layout.addWidget(self.users_table)

        # Load Users
        self.load_users()

    def style_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.users_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.users_table.setShowGrid(True)

        # Styl nagłówków
        self.users_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                gridline-color: #dcdcdc;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #b3d9ff;
                color: #000000;
            }
        """)

        # Pokaż pionowe nagłówki
        self.users_table.verticalHeader().setVisible(True)
        self.users_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.users_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.users_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_users(self):
        """Load all users into the table."""
        users = get_all_users()
        self.users_table.setRowCount(0)
        for row_number, user in enumerate(users):
            self.users_table.insertRow(row_number)
            for column_number, data in enumerate(user):
                self.users_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def toggle_delete_button(self):
        """Enable/disable delete button based on selection."""
        selected_rows = self.users_table.selectionModel().selectedRows()
        self.delete_user_button.setEnabled(bool(selected_rows))

    def open_add_user_dialog(self):
        """Open dialog to add a new user."""
        dialog = AddUserDialog(self)
        dialog.exec()
        self.load_users()

    def delete_user(self):
        """Deletes the selected user from the database."""
        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz użytkownika do usunięcia!")
            return

        selected_row = selected_rows[0]
        user_id = self.users_table.item(selected_row.row(), 0).text()
        user_name = self.users_table.item(selected_row.row(), 1).text()

        confirm = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć użytkownika o imieniu {user_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if delete_user(user_id):
                    QMessageBox.information(self, "Sukces", "Użytkownik został usunięty!")
                    self.load_users()  # Refresh user table after deletion
                else:
                    QMessageBox.critical(self, "Błąd", "Wystąpił błąd podczas usuwania użytkownika.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas usuwania użytkownika: {e}")

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj użytkownika")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        # Layout
        layout = QVBoxLayout(self)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nazwa użytkownika")
        layout.addWidget(QLabel("Nazwa użytkownika:"))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Hasło")
        layout.addWidget(QLabel("Hasło:"))
        layout.addWidget(self.password_input)

        self.role_input = QComboBox()
        self.role_input.addItems(["admin", "vet", "receptionist"])
        layout.addWidget(QLabel("Rola:"))
        layout.addWidget(self.role_input)

        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_user)
        layout.addWidget(self.add_button)

    def add_user(self):
        """Add a new user to the database."""
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_input.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Błąd", "Nazwa użytkownika i hasło są wymagane!")
            return

        password_hash = bcrypt.hash(password)

        if create_user(username, password_hash, role):
            QMessageBox.information(self, "Sukces", "Użytkownik został dodany!")
            self.accept()
        else:
            QMessageBox.critical(self, "Błąd", "Wystąpił błąd podczas dodawania użytkownika.")