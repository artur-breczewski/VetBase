from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from database.connection import get_connection
from PyQt6.QtGui import QIcon, QGuiApplication
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class FinancialSummaryWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Zestawienie Finansowe")
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony
        self.username = username

        # Wyśrodkowanie okna na ekranie
        self.center_window()

        # Główny widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout główny
        self.main_layout = QVBoxLayout(self.central_widget)

        # Sekcja wyboru zakresu dat i lokalizacji
        self.filter_layout = QHBoxLayout()
        self.main_layout.addLayout(self.filter_layout)

        # Wybór miesiąca (lub roku)
        self.date_filter = QLineEdit()
        self.date_filter.setPlaceholderText("Podaj rok/miesiąc (YYYY-MM lub YYYY)")
        self.filter_layout.addWidget(QLabel("Wybierz okres:"))
        self.filter_layout.addWidget(self.date_filter)

        # Wybór lokalizacji
        self.location_selector = QComboBox()
        self.location_selector.addItem("Wszystkie lokalizacje", None)
        self.load_locations()
        self.filter_layout.addWidget(QLabel("Wybierz lokalizację:"))
        self.filter_layout.addWidget(self.location_selector)

        # Przycisk generowania raportu
        self.generate_button = QPushButton("Generuj Zestawienie")
        self.generate_button.clicked.connect(self.generate_summary)
        self.filter_layout.addWidget(self.generate_button)

        # Wykres finansowy
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.main_layout.addWidget(self.canvas)

        # Tabela podsumowania finansowego
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["Miesiąc/Rok", "Łączna Kwota"])
        self.style_table()
        self.main_layout.addWidget(self.summary_table)

        # Pole do wyświetlania sumy
        self.total_label = QLabel("Suma: 0.00 PLN")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.total_label)

    def style_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.summary_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.summary_table.setShowGrid(True)

        # Styl nagłówków
        self.summary_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setStyleSheet("""
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
        self.summary_table.verticalHeader().setVisible(True)
        self.summary_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.summary_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.summary_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.summary_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_locations(self):
        """Ładuje lokalizacje do pola wyboru."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM locations")
        locations = cursor.fetchall()
        for location_id, location_name in locations:
            self.location_selector.addItem(location_name, location_id)
        cursor.close()
        connection.close()

    def generate_summary(self):
        """Generuje zestawienie finansowe na podstawie wybranych filtrów."""
        date_filter = self.date_filter.text()
        location_id = self.location_selector.currentData()

        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()

        # Buduj zapytanie SQL
        query = """
            SELECT 
                TO_CHAR(visit_date, 'YYYY-MM') AS period, 
                SUM(payment) AS total_payment
            FROM history
        """
        conditions = []
        parameters = []

        # Filtr daty
        if date_filter:
            if len(date_filter) == 4:  # Jeśli podano tylko rok
                conditions.append("TO_CHAR(visit_date, 'YYYY') = %s")
            elif len(date_filter) == 7:  # Jeśli podano rok i miesiąc
                conditions.append("TO_CHAR(visit_date, 'YYYY-MM') = %s")
            else:
                QMessageBox.warning(self, "Błąd", "Nieprawidłowy format daty! Użyj formatu YYYY-MM lub YYYY.")
                return
            parameters.append(date_filter)

        # Filtr lokalizacji
        if location_id:
            conditions.append("location_id = %s")
            parameters.append(location_id)

        # Dodaj warunki do zapytania
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY period ORDER BY period"

        cursor.execute(query, tuple(parameters))
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        # Zaktualizuj tabelę i wykres
        self.update_table(results)
        self.update_chart(results)

    def update_table(self, results):
        """Aktualizuje tabelę podsumowania finansowego."""
        self.summary_table.setRowCount(0)
        total = 0

        for row_number, (period, total_payment) in enumerate(results):
            self.summary_table.insertRow(row_number)
            self.summary_table.setItem(row_number, 0, QTableWidgetItem(str(period)))
            self.summary_table.setItem(row_number, 1, QTableWidgetItem(f"{total_payment:.2f} PLN"))
            total += total_payment

        self.total_label.setText(f"Suma: {total:.2f} PLN")

    def update_chart(self, results):
        """Aktualizuje wykres finansowy."""
        self.ax.clear()

        if not results:
            self.ax.text(0.5, 0.5, "Brak danych do wyświetlenia", horizontalalignment='center', verticalalignment='center')
        else:
            periods = [row[0] for row in results]
            payments = [row[1] for row in results]

            self.ax.bar(periods, payments, color='red')
            self.ax.set_title("Zarobki dla wybranego okresu")
            self.ax.set_xlabel("Rok/Miesiąc")
            self.ax.set_ylabel("Kwota (PLN)")
            self.ax.tick_params(axis='x', rotation=0)

        self.canvas.draw()