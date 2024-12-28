from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from database.connection import get_connection
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QGuiApplication
from api.email_service import send_email

import datetime

class NotificationsWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Powiadomienia i przypomnienia")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony
        self.username = username

        # Wyśrodkowanie okna na ekranie
        self.center_window()

        # Główny widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout główny
        self.main_layout = QVBoxLayout(self.central_widget)

        # Nagłówek
        self.main_layout.addWidget(QLabel("Przypomnienia o wizytach (7 dni do przodu)"))

        # Tabela przypomnień
        self.notifications_table = QTableWidget()
        self.notifications_table.setColumnCount(4)
        self.notifications_table.setHorizontalHeaderLabels(["ID Wizyty", "Zwierzę", "Data Wizyty", "Właściciel"])
        self.style_table()
        self.main_layout.addWidget(self.notifications_table)

        # Załaduj przypomnienia
        self.load_notifications()

        # Sekcja przycisków
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.send_notification_button = QPushButton("Wyślij przypomnienie")
        self.send_notification_button.setEnabled(False)
        self.send_notification_button.clicked.connect(self.send_notification)
        self.button_layout.addWidget(self.send_notification_button)

        # Włączanie/wyłączanie przycisku na podstawie zaznaczenia w tabeli
        self.notifications_table.cellClicked.connect(self.toggle_send_button)

    def style_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.notifications_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.notifications_table.setShowGrid(True)

        # Styl nagłówków
        self.notifications_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.notifications_table.setAlternatingRowColors(True)
        self.notifications_table.setStyleSheet("""
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
        self.notifications_table.verticalHeader().setVisible(True)
        self.notifications_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.notifications_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.notifications_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.notifications_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_notifications(self):
        """Ładuje listę wizyt do przypomnienia."""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        # Pobierz wizyty w ciągu najbliższych 7 dni
        today = datetime.date.today()  # Fixed here
        week_later = today + datetime.timedelta(days=7)
        cursor.execute("""
            SELECT v.id, a.name, v.visit_date, a.owner_name
            FROM visits v
            JOIN animals a ON v.animal_id = a.id
            WHERE v.visit_date BETWEEN %s AND %s
        """, (today, week_later))
        results = cursor.fetchall()

        self.notifications_table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.notifications_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.notifications_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()

    def toggle_send_button(self):
        """Aktywuje przycisk wysyłania przypomnienia po zaznaczeniu wiersza."""
        selected_items = self.notifications_table.selectedItems()
        if selected_items:  # Check if any items are selected
            self.send_notification_button.setEnabled(True)
        else:
            self.send_notification_button.setEnabled(False)

    def send_notification(self):
        """Loguje wysłanie przypomnienia i wysyła e-mail."""
        selected_rows = self.notifications_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz wizytę do przypomnienia!")
            return

        # Pobieramy dane z zaznaczonego rekordu
        selected_row = selected_rows[0]
        visit_id = self.notifications_table.item(selected_row.row(), 0).text()
        animal_name = self.notifications_table.item(selected_row.row(), 1).text()
        visit_date = self.notifications_table.item(selected_row.row(), 2).text()
        owner_name = self.notifications_table.item(selected_row.row(), 3).text()

        # Pobieramy adres e-mail właściciela z tabeli animals
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("""
            SELECT owner_email
            FROM animals
            WHERE id = (
                SELECT animal_id FROM visits WHERE id = %s
            )
        """, (visit_id,))
        owner_email = cursor.fetchone()

        # Sprawdzamy, czy adres e-mail jest dostępny
        if not owner_email or not owner_email[0]:
            QMessageBox.warning(self, "Brak e-maila", f"Brak adresu e-mail dla właściciela {owner_name}.")
            return

        owner_email = owner_email[0]  # Rozpakowanie wyniku
        cursor.close()
        connection.close()

        # Tworzymy wiadomość e-mail
        message = f"Przypomnienie: Wizyta dla {animal_name} zaplanowana na {visit_date}. Jeśli wizyta jest nieaktualna prosimy o kontakt."
        subject = f"Przypomnienie o wizycie - {animal_name}"

        # Wysyłamy wiadomość e-mail
        if send_email(owner_email, subject, message):
            QMessageBox.information(self, "Sukces", f"Przypomnienie e-mail zostało wysłane do {owner_name} ({owner_email}).")
        else:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas wysyłania e-maila do {owner_name}.")