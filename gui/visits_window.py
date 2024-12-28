from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QLabel, QLineEdit, QDateTimeEdit, QMessageBox, QComboBox, QHeaderView
)
from database.connection import get_connection
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QIcon, QGuiApplication
from gui.history_dialog import AddHistoryDialog

class VisitsWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Zarządzanie wizytami")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony
        self.username = username  # Przechowujemy nazwę zalogowanego użytkownika

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

        self.add_visit_button = QPushButton("Dodaj wizytę")
        self.add_visit_button.clicked.connect(self.open_add_visit_dialog)
        self.nav_layout.addWidget(self.add_visit_button)

        self.delete_visit_button = QPushButton("Usuń wizytę")
        self.delete_visit_button.setEnabled(False)
        self.delete_visit_button.clicked.connect(self.delete_visit)
        self.nav_layout.addWidget(self.delete_visit_button)

        self.edit_visit_button = QPushButton("Edytuj wizytę")
        self.edit_visit_button.setEnabled(False)
        self.edit_visit_button.clicked.connect(self.edit_visit)
        self.nav_layout.addWidget(self.edit_visit_button)

        self.complete_visit_button = QPushButton("Odbyto wizytę")
        self.complete_visit_button.setEnabled(False)
        self.complete_visit_button.clicked.connect(self.complete_visit)
        self.nav_layout.addWidget(self.complete_visit_button)

        # Tabela wizyt
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(6)
        self.visits_table.setHorizontalHeaderLabels([
            "ID", "Zwierzę", "Data rezerwacji", "Data wizyty", "Rejestrujący", "Opis"
        ])
        self.visits_table.cellClicked.connect(self.toggle_action_buttons)
        self.visits_table.selectionModel().selectionChanged.connect(self.toggle_action_buttons)
        self.main_layout.addWidget(self.visits_table)

         # Styl tabeli
        self.style_table()

        # Wczytaj wizyty
        self.load_visits()

    def style_table(self):
        """Stylizuje tabelę, aby była bardziej przejrzysta, i dodaje możliwość zaznaczania całych rekordów."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.visits_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.visits_table.setShowGrid(True)

        # Styl nagłówków
        self.visits_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.visits_table.setAlternatingRowColors(True)
        self.visits_table.setStyleSheet("""
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
        self.visits_table.verticalHeader().setVisible(True)
        self.visits_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.visits_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.visits_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Naprzemienne kolory wierszy
        self.visits_table.setAlternatingRowColors(True)
        self.visits_table.setStyleSheet("""
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

        # Ukrycie pionowych linii nagłówków
        self.visits_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_visits(self):
        """Ładuje wizyty z bazy danych do tabeli"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("""
            SELECT v.id, a.name, v.reservation_date, v.visit_date, v.registered_by, v.description
            FROM visits v
            JOIN animals a ON v.animal_id = a.id
        """)
        results = cursor.fetchall()

        self.visits_table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.visits_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.visits_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()

    def toggle_action_buttons(self):
        """Aktywuje przyciski akcji (usuń/edytuj/odbyto wizytę) po zaznaczeniu wiersza"""
        selected_rows = self.visits_table.selectionModel().selectedRows()
        if selected_rows:
            self.delete_visit_button.setEnabled(True)
            self.edit_visit_button.setEnabled(True)
            self.complete_visit_button.setEnabled(True)
        else:
            self.delete_visit_button.setEnabled(False)
            self.edit_visit_button.setEnabled(False)
            self.complete_visit_button.setEnabled(False)

    def open_add_visit_dialog(self):
        """Otwiera okno dialogowe do dodania wizyty"""
        dialog = AddVisitDialog(self, username=self.username)
        dialog.exec()
        self.load_visits()

    def delete_visit(self):
        """Usuwa wybraną wizytę"""
        selected_rows = self.visits_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz wizytę do usunięcia!")
            return

        selected_row = selected_rows[0]
        visit_id = self.visits_table.item(selected_row.row(), 0).text()

        confirm = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć zaznaczoną wizytę?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
                return

            cursor = connection.cursor()
            cursor.execute("DELETE FROM visits WHERE id = %s", (visit_id,))
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Sukces", "Wizyta została usunięta!")
            self.load_visits()

    def edit_visit(self):
        """Otwiera okno dialogowe do edycji wybranej wizyty"""
        selected_rows = self.visits_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz wizytę do edycji!")
            return

        selected_row = selected_rows[0]
        visit_id = self.visits_table.item(selected_row.row(), 0).text()

        # Otwieramy dialog edycji
        dialog = EditVisitDialog(self, visit_id)
        dialog.exec()
        self.load_visits()

    def complete_visit(self):
        """Przenosi wizytę do historii leczenia z możliwością dodania płatności."""
        selected_rows = self.visits_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz wizytę, którą chcesz zakończyć!")
            return

        selected_row = selected_rows[0]
        visit_id = self.visits_table.item(selected_row.row(), 0).text()
        animal_name = self.visits_table.item(selected_row.row(), 1).text()
        visit_date = self.visits_table.item(selected_row.row(), 3).text()
        description_reason = self.visits_table.item(selected_row.row(), 5).text()

        try:
            # Pobierz `animal_id`
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT animal_id FROM visits WHERE id = %s", (visit_id,))
            result = cursor.fetchone()
            animal_id = result[0]

            # Otwórz formularz dodawania historii
            dialog = AddHistoryDialog(
                self,
                animal_id=animal_id,
                visit_date=visit_date,
                registered_by=self.username,
                description_reason=description_reason
            )
            dialog.exec()

            if dialog.result() == QDialog.DialogCode.Accepted:
                cursor.execute("DELETE FROM visits WHERE id = %s", (visit_id,))
                connection.commit()
                QMessageBox.information(self, "Sukces", "Wizyta została zakończona i przeniesiona do historii!")
                self.load_visits()

            cursor.close()
            connection.close()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd: {e}")


class EditVisitDialog(QDialog):
    def __init__(self, parent=None, visit_id=None):
        super().__init__(parent)
        self.visit_id = visit_id
        self.setWindowTitle("Edytuj wizytę")
        self.setFixedSize(400, 400)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        # Layout
        layout = QVBoxLayout(self)

        # Pola formularza
        self.animal_selector = QComboBox()
        self.load_animals()
        layout.addWidget(QLabel("Zwierzę:"))
        layout.addWidget(self.animal_selector)

        # Data rezerwacji - domyślna dzisiejsza data
        self.reservation_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.reservation_date_input.setCalendarPopup(True)
        layout.addWidget(QLabel("Data rezerwacji:"))
        layout.addWidget(self.reservation_date_input)

        # Data wizyty - domyślna dzisiejsza data
        self.visit_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.visit_date_input.setCalendarPopup(True)
        layout.addWidget(QLabel("Data wizyty:"))
        layout.addWidget(self.visit_date_input)

        # Opis wizyty
        self.description_input = QLineEdit()
        layout.addWidget(QLabel("Opis wizyty:"))
        layout.addWidget(self.description_input)

        # Przyciski zapisu
        self.save_button = QPushButton("Zapisz zmiany")
        self.save_button.clicked.connect(self.save_changes)
        layout.addWidget(self.save_button)

        # Załaduj dane wizyty
        self.load_visit_data()

    def load_animals(self):
        """Ładuje listę zwierząt do pola wyboru."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM animals")
        animals = cursor.fetchall()
        for animal_id, name in animals:
            self.animal_selector.addItem(name, animal_id)

        cursor.close()
        connection.close()

    def load_visit_data(self):
        """Ładuje dane wizyty."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("""
            SELECT animal_id, reservation_date, visit_date, description
            FROM visits
            WHERE id = %s
        """, (self.visit_id,))
        visit = cursor.fetchone()

        if visit:
            animal_id, reservation_date, visit_date, description = visit
            # Ustaw dane w polach
            self.animal_selector.setCurrentIndex(self.animal_selector.findData(animal_id))
            self.reservation_date_input.setDateTime(reservation_date)
            self.visit_date_input.setDateTime(visit_date)
            self.description_input.setText(description)

        cursor.close()
        connection.close()

    def save_changes(self):
        """Zapisuje zmiany w wizytach."""
        animal_id = self.animal_selector.currentData()
        reservation_date = self.reservation_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        visit_date = self.visit_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        description = self.description_input.text()

        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE visits
                SET animal_id = %s, reservation_date = %s, visit_date = %s, description = %s
                WHERE id = %s
            """, (animal_id, reservation_date, visit_date, description, self.visit_id))
            connection.commit()
            QMessageBox.information(self, "Sukces", "Zmiany zostały zapisane!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd: {e}")
        finally:
            connection.close()

class AddVisitDialog(QDialog):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj wizytę")
        self.setFixedSize(400, 450)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony
        self.username = username  # Przechowujemy nazwę zalogowanego użytkownika

        # Layout główny
        layout = QVBoxLayout(self)

        # Przycisk otwierający wyszukiwanie zwierzęcia
        self.animal_search_button = QPushButton("Wyszukaj zwierzę")
        self.animal_search_button.clicked.connect(self.open_animal_search_dialog)
        layout.addWidget(self.animal_search_button)

        # Pole wyświetlające wybrane zwierzę
        self.selected_animal_label = QLabel("Wybrane zwierzę: Brak")
        layout.addWidget(self.selected_animal_label)

        # Data rezerwacji - ustawiona na dzisiejszą datę
        self.reservation_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.reservation_date_input.setCalendarPopup(True)
        layout.addWidget(QLabel("Data rezerwacji:"))
        layout.addWidget(self.reservation_date_input)

        # Data wizyty - ustawiona na dzisiejszą datę
        self.visit_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.visit_date_input.setCalendarPopup(True)
        layout.addWidget(QLabel("Data wizyty:"))
        layout.addWidget(self.visit_date_input)

        # Opis wizyty
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Opis wizyty")
        layout.addWidget(QLabel("Opis wizyty:"))
        layout.addWidget(self.description_input)

        # Pole automatycznego wprowadzenia nazwy rejestrującego użytkownika
        self.registered_by_input = QLineEdit(self.username)
        self.registered_by_input.setReadOnly(True)
        layout.addWidget(QLabel("Rejestrujący:"))
        layout.addWidget(self.registered_by_input)

        self.location_selector = QComboBox()
        self.load_locations()
        layout.addWidget(QLabel("Lokalizacja:"))
        layout.addWidget(self.location_selector)

        # Przyciski
        self.add_button = QPushButton("Dodaj wizytę")
        self.add_button.clicked.connect(self.add_visit)
        layout.addWidget(self.add_button)

        # ID wybranego zwierzęcia (domyślnie None)
        self.selected_animal_id = None

    def open_animal_search_dialog(self):
        """Otwiera okno wyszukiwania zwierząt."""
        dialog = AnimalSearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Pobierz wybrane zwierzę
            self.selected_animal_id, animal_info = dialog.get_selected_animal()
            self.selected_animal_label.setText(f"Wybrane zwierzę: {animal_info}")

    def load_locations(self):
        """Ładuje lokalizacje do selektora."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM locations")
        locations = cursor.fetchall()
        for location_id, name in locations:
            self.location_selector.addItem(name, location_id)

        cursor.close()
        connection.close()

    def add_visit(self):
        """Dodaje wizytę do bazy danych."""
        if not self.selected_animal_id:
            QMessageBox.warning(self, "Błąd", "Nie wybrano zwierzęcia!")
            return

        reservation_date = self.reservation_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        visit_date = self.visit_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        description = self.description_input.text()
        registered_by = self.username
        location_id = self.location_selector.currentData()

        if not reservation_date or not visit_date or not description:
            QMessageBox.warning(self, "Błąd", "Wszystkie pola są wymagane!")
            return

        try:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
                return

            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO visits (animal_id, reservation_date, visit_date, registered_by, description, location_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.selected_animal_id, reservation_date, visit_date, registered_by, description, location_id))
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Sukces", "Wizyta została dodana!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas dodawania wizyty: {e}")

class AnimalSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wyszukaj zwierzę")
        self.setFixedSize(600, 400)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        layout = QVBoxLayout(self)

        # Pole wyszukiwania
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Wyszukaj po imieniu, właścicielu lub rasie")
        self.search_input.textChanged.connect(self.search_animals)
        layout.addWidget(self.search_input)

        # Tabela wyników
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["ID", "Imię", "Właściciel", "Rasa"])
        layout.addWidget(self.results_table)

        # Przyciski
        self.select_button = QPushButton("Wybierz")
        self.select_button.setEnabled(False)
        self.select_button.clicked.connect(self.accept)
        layout.addWidget(self.select_button)

        # Załaduj wszystkie zwierzęta
        self.load_all_animals()

        # Wybór w tabeli
        self.results_table.cellClicked.connect(self.enable_select_button)

        self.selected_animal = None

    def load_all_animals(self):
        """Ładuje wszystkie zwierzęta do tabeli."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("SELECT id, name, owner_name, breed FROM animals")
        animals = cursor.fetchall()

        self.results_table.setRowCount(0)
        for row_number, row_data in enumerate(animals):
            self.results_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.results_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()

    def search_animals(self):
        """Wyszukuje zwierzęta na podstawie wpisanego tekstu, ignorując wielkość liter."""
        search_text = self.search_input.text()

        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        query = """
            SELECT id, name, owner_name, breed
            FROM animals
            WHERE name ILIKE %s
               OR owner_name ILIKE %s
               OR breed ILIKE %s
        """
        cursor.execute(query, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
        animals = cursor.fetchall()

        self.results_table.setRowCount(0)
        for row_number, row_data in enumerate(animals):
            self.results_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.results_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()

    def enable_select_button(self, row, column):
        """Aktywuje przycisk wyboru."""
        self.select_button.setEnabled(True)
        animal_id = self.results_table.item(row, 0).text()
        animal_info = self.results_table.item(row, 1).text()
        self.selected_animal = (animal_id, animal_info)

    def get_selected_animal(self):
        """Zwraca wybrane zwierzę."""
        return self.selected_animal