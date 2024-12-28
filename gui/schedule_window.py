from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QCalendarWidget, QTableWidget, QTableWidgetItem, QLabel, QHeaderView
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QIcon, QGuiApplication
from database.operations import get_visits_for_date

class ScheduleWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Harmonogram wizyt")
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

        # Kalendarz
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.load_visits_for_date)
        self.main_layout.addWidget(self.calendar)

        # Tabela wizyt
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(4)
        self.visits_table.setHorizontalHeaderLabels(["ID", "Zwierzę", "Godzina wizyty", "Opis"])
        self.style_table()
        self.main_layout.addWidget(self.visits_table)

        # Ładowanie wizyt dla wybranej daty
        self.load_visits_for_date()

    def style_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
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

        # Ukrycie pionowych linii nagłówków
        self.visits_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_visits_for_date(self):
        """Ładowanie wizyt zaplanowanych na wybrany dzień."""
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        visits = get_visits_for_date(selected_date)

        self.visits_table.setRowCount(0)
        for row_number, visit in enumerate(visits):
            self.visits_table.insertRow(row_number)
            for column_number, data in enumerate(visit):
                self.visits_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))