from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTextEdit, QFileDialog, QComboBox, QHeaderView
from database.connection import get_connection
from database.operations import add_history_record
from database.operations import get_filtered_history
from gui.search_history_window import SearchHistoryWindow
from gui.notifications_window import NotificationsWindow
from PyQt6.QtGui import QIcon, QGuiApplication



class AddHistoryDialog(QDialog):
    def __init__(self, parent=None, animal_id=None, visit_date=None, registered_by=None, description_reason=None, location_id=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj Historię Leczenia")
        self.setFixedSize(400, 550)  # Zwiększamy rozmiar, aby zmieścić pole kwoty
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        # Wyśrodkowanie okna na ekranie
        self.center_window()
        
        # Inicjalizacja zmiennych
        self.animal_id = animal_id
        self.visit_date = visit_date
        self.registered_by = registered_by
        self.description_reason = description_reason
        self.location_id = location_id

        # Pobierz imię zwierzęcia
        animal_name = self.get_animal_name(animal_id)

        # Layout główny
        layout = QVBoxLayout(self)

        # Wyświetlanie danych w formularzu
        layout.addWidget(QLabel(f"Zwierzę: {animal_name}"))  # Wyświetla imię zwierzęcia zamiast ID
        layout.addWidget(QLabel(f"Data Wizyty: {visit_date}"))
        layout.addWidget(QLabel(f"Rejestrujący: {registered_by}"))
        layout.addWidget(QLabel(f"Opis Wizyty: {description_reason}"))

        # Lokalizacja
        self.location_selector = QComboBox()
        self.load_locations(location_id)
        layout.addWidget(QLabel("Lokalizacja:"))
        layout.addWidget(self.location_selector)

        # Opis zabiegów
        self.description_input = QTextEdit()
        layout.addWidget(QLabel("Opis Zabiegów:"))
        layout.addWidget(self.description_input)

        # Podane leki
        self.medication_input = QTextEdit()
        layout.addWidget(QLabel("Podane Leki:"))
        layout.addWidget(self.medication_input)

        # Kwota za wizytę
        self.payment_input = QLineEdit()
        self.payment_input.setPlaceholderText("Kwota za wizytę")
        layout.addWidget(QLabel("Kwota:"))
        layout.addWidget(self.payment_input)

        # Załączniki
        self.attachments_label = QLabel("Załączniki: brak")
        layout.addWidget(self.attachments_label)

        self.add_attachment_button = QPushButton("Dodaj Załącznik")
        self.add_attachment_button.clicked.connect(self.add_attachment)
        layout.addWidget(self.add_attachment_button)

        # Przycisk dodania
        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_history)
        layout.addWidget(self.add_button)

        self.attachments = []

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def get_animal_name(self, animal_id):
        """Pobiera imię zwierzęcia na podstawie jego ID."""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM animals WHERE id = %s", (animal_id,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            if result:
                return result[0]
            else:
                return "Nieznane zwierzę"
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się pobrać imienia zwierzęcia: {e}")
            return "Błąd"

    def add_attachment(self):
        """Dodaj załącznik."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik")
        if file_path:
            self.attachments.append(file_path)
            self.attachments_label.setText("Załączniki: " + ", ".join(self.attachments))

    def load_locations(self, selected_location_id):
        """Ładuje lokalizacje do selektora."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM locations")
        locations = cursor.fetchall()
        for location_id, name in locations:
            self.location_selector.addItem(name, location_id)
        self.location_selector.setCurrentIndex(
            next((i for i, loc in enumerate(locations) if loc[0] == selected_location_id), 0)
        )
        cursor.close()
        connection.close()

    def add_history(self):
        """Zapisuje dane historii leczenia do bazy danych."""
        indications = self.description_input.toPlainText()
        medication = self.medication_input.toPlainText()
        payment = self.payment_input.text()
        location_id = self.location_selector.currentData()

        if not indications or not payment:
            QMessageBox.warning(self, "Błąd", "Opis zabiegów i kwota są wymagane!")
            return

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO history (animal_id, visit_date, registered_by, description_reason, indications, medication, payment, location_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.animal_id, self.visit_date, self.registered_by, self.description_reason, indications, medication, payment, location_id))
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Sukces", "Historia leczenia została dodana!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się dodać historii leczenia: {e}")

class HistoryWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Historia Leczenia")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony
        self.username = username  # Przechowujemy nazwę użytkownika

        # Wyśrodkowanie okna na ekranie
        self.center_window()

        # Główny widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout główny
        self.main_layout = QVBoxLayout(self.central_widget)

        # Sekcja filtrów
        self.filter_layout = QHBoxLayout()
        self.main_layout.addLayout(self.filter_layout)

        self.date_filter = QLineEdit()
        self.date_filter.setPlaceholderText("Data wizyty (YYYY-MM-DD)")
        self.filter_layout.addWidget(self.date_filter)

        self.doctor_filter = QLineEdit()
        self.doctor_filter.setPlaceholderText("Lekarz prowadzący")
        self.filter_layout.addWidget(self.doctor_filter)

        self.medication_filter = QLineEdit()
        self.medication_filter.setPlaceholderText("Podane leki")
        self.filter_layout.addWidget(self.medication_filter)

        self.filter_button = QPushButton("Filtruj")
        self.filter_button.clicked.connect(self.apply_filters)
        self.filter_layout.addWidget(self.filter_button)

        # Przycisk Wyszukiwania Zaawansowanego
        self.search_button = QPushButton("Zaawansowane Wyszukiwanie")
        self.search_button.clicked.connect(self.open_search_window)
        self.main_layout.addWidget(self.search_button)        

        # Tabela historii leczenia
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Zwierzę", "Data wizyty", "Lekarz", "Opis zabiegów", "Podane leki", "Kwota" 
        ])
        self.style_table()
        self.main_layout.addWidget(self.history_table)

        # Wczytaj całą historię
        self.load_history()

    def style_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.history_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.history_table.setShowGrid(True)

        # Styl nagłówków
        self.history_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet("""
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
        self.history_table.verticalHeader().setVisible(True)
        self.history_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.history_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.history_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_history(self, filters=None):
        """Wczytuje historię leczenia z bazy danych."""
        history = get_filtered_history(filters)  # Pobieranie danych z bazy
        self.history_table.setRowCount(0)
        for row_number, record in enumerate(history):
            self.history_table.insertRow(row_number)
            for column_number, data in enumerate(record):
                self.history_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))  # Dodawanie danych do tabeli

    def apply_filters(self):
        """Zastosuj filtry wyszukiwania."""
        filters = {
            "date": self.date_filter.text(),
            "doctor": self.doctor_filter.text(),
            "medication": self.medication_filter.text()
        }
        self.load_history(filters)

    def open_search_window(self):
        """Otwiera okno zaawansowanego wyszukiwania."""
        self.search_window = SearchHistoryWindow(self)
        self.search_window.show()   