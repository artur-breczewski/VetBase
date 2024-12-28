from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, QMessageBox, QHeaderView
)
from database.connection import get_connection
from PyQt6.QtGui import QIcon, QGuiApplication

class LocationsWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Zarządzanie Lokalizacjami")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony
        self.username = username

        # Wyśrodkowanie okna na ekranie
        self.center_window()

        # Główny widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout główny
        self.main_layout = QVBoxLayout(self.central_widget)

        # Górna sekcja: przyciski
        self.nav_layout = QHBoxLayout()
        self.main_layout.addLayout(self.nav_layout)

        self.add_location_button = QPushButton("Dodaj Lokalizację")
        self.add_location_button.clicked.connect(self.open_add_location_dialog)
        self.nav_layout.addWidget(self.add_location_button)

        self.edit_location_button = QPushButton("Edytuj Lokalizację")
        self.edit_location_button.setEnabled(False)
        self.edit_location_button.clicked.connect(self.edit_location)
        self.nav_layout.addWidget(self.edit_location_button)

        self.delete_location_button = QPushButton("Usuń Lokalizację")
        self.delete_location_button.setEnabled(False)
        self.delete_location_button.clicked.connect(self.delete_location)
        self.nav_layout.addWidget(self.delete_location_button)

        # Tabela lokalizacji
        self.locations_table = QTableWidget()
        self.locations_table.setColumnCount(5)
        self.locations_table.setHorizontalHeaderLabels(["ID", "Nazwa", "Adres", "Telefon", "E-mail"])
        self.style_table()
        self.locations_table.cellClicked.connect(self.toggle_action_buttons)
        self.main_layout.addWidget(self.locations_table)

        # Załaduj lokalizacje
        self.load_locations()

    def style_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.locations_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.locations_table.setShowGrid(True)

        # Styl nagłówków
        self.locations_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.locations_table.setAlternatingRowColors(True)
        self.locations_table.setStyleSheet("""
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
        self.locations_table.verticalHeader().setVisible(True)
        self.locations_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.locations_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.locations_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.locations_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_locations(self):
        """Ładuje lokalizacje z bazy danych do tabeli."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("SELECT id, name, address, phone, email FROM locations")
        results = cursor.fetchall()

        self.locations_table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.locations_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.locations_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()

    def toggle_action_buttons(self):
        """Włącza lub wyłącza przyciski akcji w zależności od zaznaczenia wiersza."""
        selected_rows = self.locations_table.selectionModel().selectedIndexes()

        # Sprawdzamy, czy zaznaczono co najmniej jedną komórkę w wierszu
        if selected_rows:
            self.edit_location_button.setEnabled(True)
            self.delete_location_button.setEnabled(True)
        else:
            self.edit_location_button.setEnabled(False)
            self.delete_location_button.setEnabled(False)

    def open_add_location_dialog(self):
        """Otwiera okno dialogowe do dodania lokalizacji."""
        dialog = AddLocationDialog(self)
        dialog.exec()
        self.load_locations()

    def edit_location(self):
        """Edytuje zaznaczoną lokalizację."""
        selected_rows = self.locations_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz lokalizację do edycji!")
            return

        selected_row = selected_rows[0]
        location_id = self.locations_table.item(selected_row.row(), 0).text()

        dialog = EditLocationDialog(self, location_id)
        dialog.exec()
        self.load_locations()

    def delete_location(self):
        """Usuwa zaznaczoną lokalizację."""
        selected_rows = self.locations_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz lokalizację do usunięcia!")
            return

        selected_row = selected_rows[0]
        location_id = self.locations_table.item(selected_row.row(), 0).text()
        location_name = self.locations_table.item(selected_row.row(), 1).text()

        confirm = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć lokalizację o nazwie {location_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
                return

            cursor = connection.cursor()
            cursor.execute("DELETE FROM locations WHERE id = %s", (location_id,))
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Sukces", "Lokalizacja została usunięta!")
            self.load_locations()


class AddLocationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj Lokalizację")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Nazwa:"))
        layout.addWidget(self.name_input)

        self.address_input = QLineEdit()
        layout.addWidget(QLabel("Adres:"))
        layout.addWidget(self.address_input)

        self.phone_input = QLineEdit()
        layout.addWidget(QLabel("Telefon:"))
        layout.addWidget(self.phone_input)

        self.email_input = QLineEdit()
        layout.addWidget(QLabel("E-mail:"))
        layout.addWidget(self.email_input)

        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_location)
        layout.addWidget(self.add_button)

    def add_location(self):
        """Dodaje nową lokalizację do bazy danych."""
        name = self.name_input.text()
        address = self.address_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()

        if not name or not address:
            QMessageBox.warning(self, "Błąd", "Nazwa i adres są wymagane!")
            return

        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO locations (name, address, phone, email) VALUES (%s, %s, %s, %s)",
            (name, address, phone, email)
        )
        connection.commit()
        cursor.close()
        connection.close()

        QMessageBox.information(self, "Sukces", "Lokalizacja została dodana!")
        self.accept()


class EditLocationDialog(QDialog):
    def __init__(self, parent=None, location_id=None):
        super().__init__(parent)
        self.location_id = location_id
        self.setWindowTitle("Edytuj Lokalizację")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Nazwa:"))
        layout.addWidget(self.name_input)

        self.address_input = QLineEdit()
        layout.addWidget(QLabel("Adres:"))
        layout.addWidget(self.address_input)

        self.phone_input = QLineEdit()
        layout.addWidget(QLabel("Telefon:"))
        layout.addWidget(self.phone_input)

        self.email_input = QLineEdit()
        layout.addWidget(QLabel("E-mail:"))
        layout.addWidget(self.email_input)

        self.save_button = QPushButton("Zapisz")
        self.save_button.clicked.connect(self.save_changes)
        layout.addWidget(self.save_button)

        self.load_location_data()

    def load_location_data(self):
        """Ładuje dane lokalizacji do formularza."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            self.reject()
            return

        cursor = connection.cursor()
        cursor.execute("SELECT name, address, phone, email FROM locations WHERE id = %s", (self.location_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            self.name_input.setText(result[0])
            self.address_input.setText(result[1])
            self.phone_input.setText(result[2])
            self.email_input.setText(result[3])

    def save_changes(self):
        """Zapisuje zmiany w lokalizacji."""
        name = self.name_input.text()
        address = self.address_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()

        if not name or not address:
            QMessageBox.warning(self, "Błąd", "Nazwa i adres są wymagane!")
            return

        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute(
            "UPDATE locations SET name = %s, address = %s, phone = %s, email = %s WHERE id = %s",
            (name, address, phone, email, self.location_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

        QMessageBox.information(self, "Sukces", "Zmiany zostały zapisane!")
        self.accept()