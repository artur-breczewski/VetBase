from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPalette, QBrush, QPixmap, QIcon
from gui.animals_window import AnimalsWindow
from gui.visits_window import VisitsWindow
from gui.history_dialog import HistoryWindow
from gui.reports_window import ReportsWindow
from gui.locations_window import LocationsWindow
from gui.summary_window import FinancialSummaryWindow
from gui.users_window import UsersWindow
from gui.notifications_window import NotificationsWindow
from gui.schedule_window import ScheduleWindow  # Importujemy Harmonogram


class MainWindow(QMainWindow):
    def __init__(self, user_id, username, role):
        super().__init__()
        self.setWindowTitle("VetBase v1.10")        
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony aplikacji
        self.user_id = user_id
        self.username = username
        self.role = role

        # Automatyczne maksymalizowanie okna
        self.showMaximized()

        # Główny widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("mainWidget")
        self.setCentralWidget(self.central_widget)

        # Ustawienie tła
        self.set_background()

        # Layout główny
        self.main_layout = QHBoxLayout(self.central_widget)

        # Lewa sekcja: przyciski
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setContentsMargins(20, 20, 20, 20)
        self.buttons_layout.setSpacing(15)
        self.main_layout.addLayout(self.buttons_layout, 1)

        # Prawa sekcja: obrazek
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap("").scaled(
            800, 800, Qt.AspectRatioMode.KeepAspectRatioByExpanding
        ))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.image_label, 2)

        # Tworzenie przycisków w zależności od uprawnień użytkownika
        self.create_buttons()

    def set_background(self):
        """Ustawia tło aplikacji."""
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(QPixmap("images/background/background.jpg")))
        self.setPalette(palette)

    def create_buttons(self):
        """Tworzy przyciski z ikonami w zależności od uprawnień użytkownika."""
        if self.role in ["admin", "vet", "receptionist"]:  # Dostęp dla wszystkich ról
            self.add_button("Zarządzaj Wizytami", "images/icons/calendar.png", VisitsWindow) # gotowe
            self.add_button("Moduł Powiadomień", "images/icons/notification.png", NotificationsWindow) # gotowe
            self.add_button("Harmonogram Wizyt", "images/icons/schedule.png", ScheduleWindow) # Gotowe

        if self.role in ["admin", "vet"]:  # Dostęp dla admina i weterynarza
            self.add_button("Historia Leczenia", "images/icons/history.png", HistoryWindow) # gotowe
            self.add_button("Baza Zwierząt", "images/icons/animals.png", AnimalsWindow) # Gotowe

        if self.role == "admin":  # Tylko dla admina
            self.add_button("Statystyki i Raporty", "images/icons/reports.png", ReportsWindow) # gotowe
            self.add_button("Lokalizacje", "images/icons/location.png", LocationsWindow) # gotowe
            self.add_button("Finanse", "images/icons/finance.png", FinancialSummaryWindow) # gotowe
            self.add_button("Zarządzaj użytkownikami", "images/icons/users.png", UsersWindow)

    def add_button(self, label, icon_path, window_class):
        """Dodaje przycisk z ikoną do lewej sekcji."""
        button = QPushButton(label)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(40, 40))  # Rozmiar ikony
        button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #cccccc;
                font-size: 18px;
                padding: 10px;
                text-align: left;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        button.clicked.connect(lambda: self.open_window(window_class))
        self.buttons_layout.addWidget(button)

    def open_window(self, window_class):
        """Otwiera określone okno."""
        window = window_class(parent=self, username=self.username)  # Przekazujemy username do okien
        window.show()