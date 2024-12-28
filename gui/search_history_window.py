from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit,
    QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView
)
from database.connection import get_connection
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QGuiApplication

class SearchHistoryWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Zaawansowane Wyszukiwanie - Historia Leczenia")
        self.setGeometry(100, 100, 1200, 600)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony
        self.username = username

        # Wyśrodkowanie okna na ekranie
        self.center_window()

        # Główny widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout główny
        self.main_layout = QVBoxLayout(self.central_widget)

        # Sekcja wyszukiwania
        self.filter_layout = QHBoxLayout()
        self.main_layout.addLayout(self.filter_layout)

        # Pola wyszukiwania
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Imię")
        self.name_input.textChanged.connect(self.filter_results)
        self.filter_layout.addWidget(QLabel("Imię:"))
        self.filter_layout.addWidget(self.name_input)

        self.breed_input = QLineEdit()
        self.breed_input.setPlaceholderText("Rasa")
        self.breed_input.textChanged.connect(self.filter_results)
        self.filter_layout.addWidget(QLabel("Rasa:"))
        self.filter_layout.addWidget(self.breed_input)

        self.owner_input = QLineEdit()
        self.owner_input.setPlaceholderText("Właściciel")
        self.owner_input.textChanged.connect(self.filter_results)
        self.filter_layout.addWidget(QLabel("Właściciel:"))
        self.filter_layout.addWidget(self.owner_input)

        self.visit_date_input = QLineEdit()
        self.visit_date_input.setPlaceholderText("Data wizyty (YYYY-MM-DD)")
        self.visit_date_input.textChanged.connect(self.filter_results)
        self.filter_layout.addWidget(QLabel("Data wizyty:"))
        self.filter_layout.addWidget(self.visit_date_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Opis wizyty")
        self.description_input.textChanged.connect(self.filter_results)
        self.filter_layout.addWidget(QLabel("Opis wizyty:"))
        self.filter_layout.addWidget(self.description_input)

        # Tabela wyników
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "ID Zwierzęcia", "Imię Zwierzęcia", "Gatunek", "Rasa", 
            "Właściciel", "Data Wizyty", "Opis Wizyty"
        ])
        self.style_table()
        self.main_layout.addWidget(self.results_table)

        # Wczytaj początkowe dane
        self.load_initial_data()

    def style_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.results_table.setShowGrid(True)

        # Styl nagłówków
        self.results_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
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
        self.results_table.verticalHeader().setVisible(True)
        self.results_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.results_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_initial_data(self):
        """Ładowanie wszystkich danych z historii leczenia"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                a.id, a.name, a.species, a.breed, 
                a.owner_name, h.visit_date, h.description_reason
            FROM animals a
            JOIN history h ON a.id = h.animal_id
        """)
        results = cursor.fetchall()

        self.populate_table(results)

        cursor.close()
        connection.close()

    def populate_table(self, data):
        """Wypełnia tabelę danymi"""
        self.results_table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.results_table.insertRow(row_number)
            for column_number, value in enumerate(row_data):
                self.results_table.setItem(row_number, column_number, QTableWidgetItem(str(value)))

    def filter_results(self):
        """Filtruje wyniki w tabeli na podstawie wprowadzonych kryteriów"""
        name = self.name_input.text()
        breed = self.breed_input.text()
        owner = self.owner_input.text()
        visit_date = self.visit_date_input.text()
        description = self.description_input.text()

        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        query = """
            SELECT 
                a.id, a.name, a.species, a.breed, 
                a.owner_name, h.visit_date, h.description_reason
            FROM animals a
            JOIN history h ON a.id = h.animal_id
            WHERE 
                a.name ILIKE %s AND 
                a.breed ILIKE %s AND 
                a.owner_name ILIKE %s AND 
                (h.visit_date::text ILIKE %s OR h.visit_date IS NULL) AND 
                (h.description_reason ILIKE %s OR h.description_reason IS NULL)
        """
        cursor.execute(query, (
            f"%{name}%", f"%{breed}%", f"%{owner}%", 
            f"%{visit_date}%", f"%{description}%"
        ))
        results = cursor.fetchall()

        self.populate_table(results)

        cursor.close()
        connection.close()