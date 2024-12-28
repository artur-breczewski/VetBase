from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QDialog, QLineEdit, QMessageBox, QMainWindow, QHeaderView
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QGuiApplication
from database.connection import get_connection


class AnimalsWindow(QMainWindow):
    def __init__(self, parent=None, username=None):
        super().__init__(parent)
        self.setWindowTitle("Baza Zwierząt")
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

        # Górna sekcja: przyciski
        self.nav_layout = QHBoxLayout()
        self.main_layout.addLayout(self.nav_layout)

        self.add_animal_button = QPushButton("Dodaj Zwierzę")
        self.add_animal_button.clicked.connect(self.open_add_animal_dialog)
        self.nav_layout.addWidget(self.add_animal_button)

        self.edit_animal_button = QPushButton("Edytuj Zwierzę")
        self.edit_animal_button.setEnabled(False)
        self.edit_animal_button.clicked.connect(self.edit_animal)
        self.nav_layout.addWidget(self.edit_animal_button)

        self.delete_animal_button = QPushButton("Usuń Zwierzę")
        self.delete_animal_button.setEnabled(False)
        self.delete_animal_button.clicked.connect(self.delete_animal)
        self.nav_layout.addWidget(self.delete_animal_button)

        # Środkowa sekcja: tabela + zdjęcie
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # Tabela
        self.animals_table = QTableWidget()
        self.animals_table.setColumnCount(9)
        self.animals_table.setHorizontalHeaderLabels(["ID", "Imię", "Gatunek", "Rasa", "Wiek", "Właściciel", "Kontakt", "Mail", "Uwagi"])
        self.style_table()
        self.animals_table.cellClicked.connect(self.toggle_action_buttons)
        self.content_layout.addWidget(self.animals_table)

        # Pole na zdjęcie
        self.image_label = QLabel("Zdjęcie zaznaczonego zwierzęcia z listy")
        self.image_label.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 14px;
            color: #555555;
        """)
        self.image_label.setFixedSize(300, 300)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.image_label)

        # Sygnały reagujące na zmianę zaznaczenia w tabeli
        self.animals_table.selectionModel().selectionChanged.connect(self.toggle_action_buttons)
        self.animals_table.selectionModel().selectionChanged.connect(self.update_image_from_selection)

        # Wczytaj dane zwierząt
        self.load_animals()

    def style_table(self):
        """Stylizuje tabelę i dodaje funkcjonalność zaznaczania całych wierszy."""
        # Rozciąganie kolumn na całą szerokość tabeli
        header = self.animals_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Włączenie siatki
        self.animals_table.setShowGrid(True)

        # Styl nagłówków
        self.animals_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #dcdcdc;
            }
        """)

        # Naprzemienne kolory wierszy
        self.animals_table.setAlternatingRowColors(True)
        self.animals_table.setStyleSheet("""
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
        self.animals_table.verticalHeader().setVisible(True)
        self.animals_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 3px;
                font-size: 12px;
                border: 1px solid #dcdcdc;
            }
        """)
        self.animals_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Zaznaczenie całych wierszy
        self.animals_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Ukrycie pionowych linii nagłówków
        self.animals_table.verticalHeader().setVisible(False)

    def center_window(self):
        """Wyśrodkowuje okno na ekranie."""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_animals(self):
        """Ładuje dane z tabeli animals do widżetu tabeli"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
            return

        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, name, species, breed, age, owner_name, owner_contact, owner_email, info
            FROM animals
        """)
        results = cursor.fetchall()

        self.animals_table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.animals_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.animals_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        cursor.close()
        connection.close()

    def toggle_action_buttons(self):
        """Aktywuje przyciski akcji po zaznaczeniu wiersza"""
        selected_rows = self.animals_table.selectionModel().selectedRows()
        if selected_rows:
            self.edit_animal_button.setEnabled(True)
            self.delete_animal_button.setEnabled(True)
        else:
            self.edit_animal_button.setEnabled(False)
            self.delete_animal_button.setEnabled(False)

    def open_add_animal_dialog(self):
        """Otwiera okno dialogowe do dodania zwierzęcia"""
        dialog = AddAnimalDialog(self)
        dialog.exec()
        self.load_animals()

    def edit_animal(self):
        """Edytuje zaznaczone zwierzę"""
        selected_rows = self.animals_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz zwierzę do edycji!")
            return

        selected_row = selected_rows[0]
        animal_id = self.animals_table.item(selected_row.row(), 0).text()

        # Otwieramy dialog edycji
        dialog = EditAnimalDialog(self, animal_id)
        dialog.exec()
        self.load_animals()

    def delete_animal(self):
        """Usuwa zaznaczone zwierzę"""
        selected_rows = self.animals_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Brak wyboru", "Wybierz zwierzę do usunięcia!")
            return

        selected_row = selected_rows[0]
        animal_name = self.animals_table.item(selected_row.row(), 1).text()

        confirm = QMessageBox.question(
            self,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć zwierzę o imieniu {animal_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                connection = get_connection()
                if not connection:
                    QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
                    return

                cursor = connection.cursor()
                cursor.execute("DELETE FROM animals WHERE id = %s", (animal_id,))
                connection.commit()
                cursor.close()
                connection.close()

                QMessageBox.information(self, "Sukces", "Zwierzę zostało usunięte!")
                self.load_animals()
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas usuwania: {e}")

    def update_image_from_selection(self):
        """Aktualizuje zdjęcie na podstawie zaznaczenia w tabeli"""
        selected_rows = self.animals_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.display_image(row, 0)
        else:
            self.image_label.setText("Brak zdjęcia")
            self.image_label.setStyleSheet("""
                background-color: #f0f0f0;
                font-size: 14px;
                color: #555555;
            """)

    def display_image(self, row, column):
        """Wyświetla zdjęcie dla zaznaczonego wiersza"""
        selected_id = self.animals_table.item(row, 0).text()  # Pobieramy ID zwierzęcia
        image_path = f"images/{selected_id}.jpg"  # Ścieżka do zdjęcia
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            self.image_label.setText("Brak zdjęcia")            
            self.image_label.setStyleSheet("""
                background-color: #f0f0f0;
                font-size: 14px;
                color: #555555;
            """)
        else:
            self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
            self.image_label.setStyleSheet("""
                background-color: #f0f0f0;
                font-size: 14px;
                color: #555555;
            """)

class AddAnimalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj Zwierzę")
        self.setFixedSize(400, 450)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Imię:"))
        layout.addWidget(self.name_input)

        self.species_input = QLineEdit()
        layout.addWidget(QLabel("Gatunek:"))
        layout.addWidget(self.species_input)

        self.breed_input = QLineEdit()
        layout.addWidget(QLabel("Rasa:"))
        layout.addWidget(self.breed_input)

        self.age_input = QLineEdit()
        layout.addWidget(QLabel("Wiek:"))
        layout.addWidget(self.age_input)

        self.owner_name_input = QLineEdit()
        layout.addWidget(QLabel("Właściciel:"))
        layout.addWidget(self.owner_name_input)

        self.owner_contact_input = QLineEdit()
        layout.addWidget(QLabel("Kontakt:"))
        layout.addWidget(self.owner_contact_input)

        self.owner_email_input = QLineEdit()
        layout.addWidget(QLabel("Adres e-mail:"))
        layout.addWidget(self.owner_email_input)

        self.info_input = QLineEdit()
        layout.addWidget(QLabel("Uwagi:"))
        layout.addWidget(self.info_input)

        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_animal)
        layout.addWidget(self.add_button)

    def add_animal(self):
        """Dodaje nowe zwierzę do bazy danych"""
        name = self.name_input.text()
        species = self.species_input.text()
        breed = self.breed_input.text()
        age = self.age_input.text()
        owner_name = self.owner_name_input.text()
        owner_contact = self.owner_contact_input.text()
        owner_email = self.owner_email_input.text()
        info = self.info_input.text()

        if not name or not species or not owner_name:
            QMessageBox.warning(self, "Błąd", "Imię, gatunek i właściciel są wymagane!")
            return

        try:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Błąd", "Brak połączenia z bazą danych.")
                return

            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO animals (name, species, breed, age, owner_name, owner_contact, owner_email, info)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, species, breed, age, owner_name, owner_contact, owner_email, info))
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Sukces", "Zwierzę zostało dodane!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas dodawania zwierzęcia: {e}")


class EditAnimalDialog(QDialog):
    def __init__(self, parent=None, animal_id=None):
        super().__init__(parent)
        self.animal_id = animal_id
        self.setWindowTitle("Edytuj Zwierzę")
        self.setFixedSize(400, 450)
        self.setWindowIcon(QIcon("images/background/icon.png"))  # Ustawienie ikony

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Imię:"))
        layout.addWidget(self.name_input)

        self.species_input = QLineEdit()
        layout.addWidget(QLabel("Gatunek:"))
        layout.addWidget(self.species_input)

        self.breed_input = QLineEdit()
        layout.addWidget(QLabel("Rasa:"))
        layout.addWidget(self.breed_input)

        self.age_input = QLineEdit()
        layout.addWidget(QLabel("Wiek:"))
        layout.addWidget(self.age_input)

        self.owner_name_input = QLineEdit()
        layout.addWidget(QLabel("Właściciel:"))
        layout.addWidget(self.owner_name_input)

        self.owner_contact_input = QLineEdit()
        layout.addWidget(QLabel("Kontakt:"))
        layout.addWidget(self.owner_contact_input)

        self.owner_email_input = QLineEdit()
        layout.addWidget(QLabel("Adres e-mail:"))
        layout.addWidget(self.owner_email_input)

        self.info_input = QLineEdit()
        layout.addWidget(QLabel("Uwagi:"))
        layout.addWidget(self.info_input)

        self.save_button = QPushButton("Zapisz Zmiany")
        self.save_button.clicked.connect(self.save_changes)
        layout.addWidget(self.save_button)

        self.load_animal_data()

    def load_animal_data(self):
        """Ładuje dane zwierzęcia do pól formularza"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT name, species, breed, age, owner_name, owner_contact, owner_email, info
                FROM animals WHERE id = %s
            """, (self.animal_id,))
            result = cursor.fetchone()
            if result:  # Sprawdź, czy zapytanie zwróciło wynik
                self.name_input.setText(result[0])
                self.species_input.setText(result[1])
                self.breed_input.setText(result[2])
                self.age_input.setText(str(result[3]))
                self.owner_name_input.setText(result[4])
                self.owner_contact_input.setText(result[5])
                self.owner_email_input.setText(result[6])
                self.info_input.setText(result[7])
            else:
                QMessageBox.warning(self, "Błąd", "Nie znaleziono danych dla wybranego zwierzęcia!")
            cursor.close()
            connection.close()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas ładowania danych: {e}")

    def save_changes(self):
        """Zapisuje zmiany w zwierzęciu"""
        name = self.name_input.text()
        species = self.species_input.text()
        breed = self.breed_input.text()
        age = self.age_input.text()
        owner_name = self.owner_name_input.text()
        owner_contact = self.owner_contact_input.text()
        owner_email = self.owner_email_input.text()
        info = self.info_input.text()

        if not name or not species or not owner_name:
            QMessageBox.warning(self, "Błąd", "Imię, gatunek i właściciel są wymagane!")
            return

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE animals
                SET name = %s, species = %s, breed = %s, age = %s, owner_name = %s, owner_contact = %s, owner_email = %s,  info = %s
                WHERE id = %s
            """, (name, species, breed, age, owner_name, owner_contact, owner_email, info, self.animal_id))
            connection.commit()
            cursor.close()
            connection.close()
            QMessageBox.information(self, "Sukces", "Zmiany zostały zapisane!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas zapisywania: {e}")