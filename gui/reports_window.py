from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QComboBox, QHeaderView
)
from database.connection import get_connection
from PyQt6.QtGui import QIcon, QGuiApplication
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ReportsWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Statystyki i Raporty")
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

        # Pole wyboru lokalizacji
        self.location_selector = QComboBox()
        self.location_selector.addItem("Wszystkie lokalizacje", None)  # Opcja dla wszystkich lokalizacji
        self.load_locations()  # Załaduj lokalizacje do pola wyboru
        self.location_selector.currentIndexChanged.connect(self.update_statistics)  # Aktualizuj statystyki po zmianie lokalizacji
        self.main_layout.addWidget(QLabel("Wybierz lokalizację:"))
        self.main_layout.addWidget(self.location_selector)

        # Nagłówki sekcji
        self.main_layout.addWidget(QLabel("Statystyki Wizyt:"))
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(3)
        self.visits_table.setHorizontalHeaderLabels(["Miesiąc", "Liczba Wizyt", "Liczba Zwierząt"])
        self.style_table()
        self.main_layout.addWidget(self.visits_table)

        self.main_layout.addWidget(QLabel("Statystyki Leczenia:"))
        self.treatment_table = QTableWidget()
        self.treatment_table.setColumnCount(2)
        self.treatment_table.setHorizontalHeaderLabels(["Najczęściej Stosowane Leki", "Średnia Liczba Wizyt na Zwierzę"])
        self.style_treatment_table()
        self.main_layout.addWidget(self.treatment_table)

        self.main_layout.addWidget(QLabel("Statystyki Płatności:"))
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(3)
        self.payments_table.setHorizontalHeaderLabels(["Miesiąc", "Liczba Wizyt", "Łączna Kwota"])
        self.style_payments_table()
        self.main_layout.addWidget(self.payments_table)

        # Sekcja przycisków eksportu
        self.export_layout = QHBoxLayout()
        self.main_layout.addLayout(self.export_layout)

        self.export_csv_button = QPushButton("Eksportuj do CSV")
        self.export_csv_button.clicked.connect(self.export_to_csv)
        self.export_layout.addWidget(self.export_csv_button)

        self.export_pdf_button = QPushButton("Eksportuj do PDF")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.export_layout.addWidget(self.export_pdf_button)

        # Wczytaj dane statystyczne
        self.load_data()

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

    def style_treatment_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.treatment_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.treatment_table.setShowGrid(True)

        # Styl nagłówków
        self.treatment_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.treatment_table.setAlternatingRowColors(True)
        self.treatment_table.setStyleSheet("""
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
        self.treatment_table.verticalHeader().setVisible(True)
        self.treatment_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.treatment_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.treatment_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.treatment_table.verticalHeader().setVisible(False)

    def style_payments_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.payments_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.payments_table.setShowGrid(True)

        # Styl nagłówków
        self.payments_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setStyleSheet("""
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
        self.payments_table.verticalHeader().setVisible(True)
        self.payments_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.payments_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.payments_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.payments_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)        

    def load_data(self):
        """Ładuje dane statystyczne do tabel z uwzględnieniem lokalizacji."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()

        # Pobierz ID lokalizacji z pola wyboru
        location_id = self.location_selector.currentData()

        # Statystyki wizyt
        if location_id:  # Jeśli wybrano konkretną lokalizację
            cursor.execute("""
                SELECT 
                    TO_CHAR(visit_date, 'YYYY-MM') AS month, 
                    COUNT(*) AS visit_count, 
                    COUNT(DISTINCT animal_id) AS animal_count
                FROM history
                WHERE location_id = %s
                GROUP BY month
                ORDER BY month
            """, (location_id,))
        else:  # Dla wszystkich lokalizacji
            cursor.execute("""
                SELECT 
                    TO_CHAR(visit_date, 'YYYY-MM') AS month, 
                    COUNT(*) AS visit_count, 
                    COUNT(DISTINCT animal_id) AS animal_count
                FROM history
                GROUP BY month
                ORDER BY month
            """)
        visit_stats = cursor.fetchall()
        self.populate_table(self.visits_table, visit_stats)

        # Statystyki leczenia
        if location_id:  # Jeśli wybrano konkretną lokalizację
            cursor.execute("""
                SELECT 
                    medication, 
                    ROUND(CAST(COUNT(*) AS NUMERIC) / NULLIF(COUNT(DISTINCT animal_id), 0), 2) AS avg_visits_per_animal
                FROM history
                WHERE location_id = %s
                GROUP BY medication
                ORDER BY avg_visits_per_animal DESC
                LIMIT 10
            """, (location_id,))
        else:  # Dla wszystkich lokalizacji
            cursor.execute("""
                SELECT 
                    medication, 
                    ROUND(CAST(COUNT(*) AS NUMERIC) / NULLIF(COUNT(DISTINCT animal_id), 0), 2) AS avg_visits_per_animal
                FROM history
                GROUP BY medication
                ORDER BY avg_visits_per_animal DESC
                LIMIT 10
            """)
        treatment_stats = cursor.fetchall()
        self.populate_table(self.treatment_table, treatment_stats)

        # Statystyki płatności
        if location_id:  # Jeśli wybrano konkretną lokalizację
            cursor.execute("""
                SELECT 
                    TO_CHAR(visit_date, 'YYYY-MM') AS month, 
                    COUNT(*) AS visit_count, 
                    SUM(payment) AS total_payment
                FROM history
                WHERE location_id = %s
                GROUP BY month
                ORDER BY month
            """, (location_id,))
        else:  # Dla wszystkich lokalizacji
            cursor.execute("""
                SELECT 
                    TO_CHAR(visit_date, 'YYYY-MM') AS month, 
                    COUNT(*) AS visit_count, 
                    SUM(payment) AS total_payment
                FROM history
                GROUP BY month
                ORDER BY month
            """)
        payment_stats = cursor.fetchall()
        self.populate_table(self.payments_table, payment_stats)

        cursor.close()
        connection.close()

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

    def populate_table(self, table, data):
        """Wypełnia tabelę danymi."""
        table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            table.insertRow(row_number)
            for column_number, value in enumerate(row_data):
                table.setItem(row_number, column_number, QTableWidgetItem(str(value)))

    def export_to_csv(self):
        """Eksportuje dane statystyk do pliku CSV."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz jako CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Eksportuj dane wizyt
                writer.writerow(["Statystyki Wizyt"])
                writer.writerow(["Miesiąc", "Liczba Wizyt", "Liczba Zwierząt"])
                for row in range(self.visits_table.rowCount()):
                    row_data = [self.visits_table.item(row, col).text() for col in range(self.visits_table.columnCount())]
                    writer.writerow(row_data)

                # Eksportuj dane leczenia
                writer.writerow([])
                writer.writerow(["Statystyki Leczenia"])
                writer.writerow(["Najczęściej Stosowane Leki", "Średnia Liczba Wizyt na Zwierzę"])
                for row in range(self.treatment_table.rowCount()):
                    row_data = [self.treatment_table.item(row, col).text() for col in range(self.treatment_table.columnCount())]
                    writer.writerow(row_data)

                # Eksportuj dane płatności
                writer.writerow([])
                writer.writerow(["Statystyki Płatności"])
                writer.writerow(["Miesiąc", "Liczba Wizyt", "Łączna Kwota"])
                for row in range(self.payments_table.rowCount()):
                    row_data = [self.payments_table.item(row, col).text() for col in range(self.payments_table.columnCount())]
                    writer.writerow(row_data)

            QMessageBox.information(self, "Sukces", f"Statystyki zapisano do pliku: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku: {e}")

    def export_to_pdf(self):
        """Eksportuje dane statystyk do pliku PDF."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz jako PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return

        try:
            pdf = canvas.Canvas(file_path, pagesize=letter)
            pdf.setFont("Helvetica", 12)

            # Statystyki Wizyt
            pdf.drawString(30, 750, "Statystyki Wizyt:")
            y_position = 730
            pdf.drawString(30, y_position, "Miesiąc | Liczba Wizyt | Liczba Zwierząt")
            y_position -= 20
            for row in range(self.visits_table.rowCount()):
                row_data = " | ".join([self.visits_table.item(row, col).text() for col in range(self.visits_table.columnCount())])
                pdf.drawString(30, y_position, row_data)
                y_position -= 20

            # Statystyki Leczenia
            y_position -= 40
            pdf.drawString(30, y_position, "Statystyki Leczenia:")
            y_position -= 20
            pdf.drawString(30, y_position, "Najczęściej Stosowane Leki | Średnia Liczba Wizyt na Zwierzę")
            y_position -= 20
            for row in range(self.treatment_table.rowCount()):
                row_data = " | ".join([self.treatment_table.item(row, col).text() for col in range(self.treatment_table.columnCount())])
                pdf.drawString(30, y_position, row_data)
                y_position -= 20

            # Statystyki Płatności
            y_position -= 40
            pdf.drawString(30, y_position, "Statystyki Płatności:")
            y_position -= 20
            pdf.drawString(30, y_position, "Miesiąc | Liczba Wizyt | Łączna Kwota")
            y_position -= 20
            for row in range(self.payments_table.rowCount()):
                row_data = " | ".join([self.payments_table.item(row, col).text() for col in range(self.payments_table.columnCount())])
                pdf.drawString(30, y_position, row_data)
                y_position -= 20

            pdf.save()
            QMessageBox.information(self, "Sukces", f"Statystyki zapisano do pliku PDF: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku PDF: {e}")

    def update_statistics(self):
        """Aktualizuje statystyki po zmianie lokalizacji."""
        self.load_data()