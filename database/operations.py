from database.connection import get_connection

def add_animal(name, species, breed, age, owner_name, owner_contact):
    try:
        conn = get_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO animals (name, species, breed, age, owner_name, owner_contact)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, species, breed, age, owner_name, owner_contact))
        conn.commit()

        cursor.close()
        conn.close()
        print("Animal added successfully!")
        return True
    except Exception as e:
        print("Error adding animal:", e)
        return False
    
def create_user(username, password_hash, role):
    connection = get_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
        """, (username, password_hash, role))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def delete_user(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def get_all_users():
    connection = get_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, role, created_at FROM users")
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
    
def get_visits_for_date(date):
    """Pobierz wizyty zaplanowane na daną datę."""
    connection = get_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT v.id, a.name, v.visit_date::time, v.description
            FROM visits v
            JOIN animals a ON v.animal_id = a.id
            WHERE v.visit_date::date = %s
        """, (date,))
        visits = cursor.fetchall()
        cursor.close()
        connection.close()
        return visits
    except Exception as e:
        print(f"Error fetching visits for date {date}: {e}")
        return []

def add_history_record(animal_id, visit_date, registered_by, description_reason, medication, indications, location_id=None, attachments=None):
    """
    Dodaje rekord historii leczenia do bazy danych.
    :param animal_id: ID zwierzęcia.
    :param visit_date: Data wizyty.
    :param registered_by: Osoba rejestrująca.
    :param description_reason: Opis przyczyny wizyty.
    :param medication: Podane leki.
    :param indications: Opis zabiegów.
    :param location_id: ID lokalizacji wizyty.
    :param attachments: Lista ścieżek do załączników (opcjonalnie).
    :return: True, jeśli zapis zakończono sukcesem, False w przypadku błędu.
    """
    try:
        connection = get_connection()
        if not connection:
            return False

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO history (animal_id, visit_date, registered_by, description_reason, medication, indications, location_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (animal_id, visit_date, registered_by, description_reason, medication, indications, location_id))
        history_id = cursor.fetchone()[0]  # Pobierz ID nowo dodanego rekordu

        # Obsługa załączników
        if attachments:
            for attachment in attachments:
                cursor.execute("""
                    INSERT INTO history_attachments (history_id, file_path)
                    VALUES (%s, %s)
                """, (history_id, attachment))

        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Błąd podczas dodawania historii leczenia: {e}")
        return False

def get_filtered_history(filters=None):
    """Pobierz historię leczenia z zastosowaniem filtrów."""
    connection = get_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        query = """
            SELECT h.id, a.name, h.visit_date, h.registered_by, h.description_reason, h.medication, h.payment
            FROM history h
            JOIN animals a ON h.animal_id = a.id
            WHERE TRUE
        """
        params = []
        if filters:
            if filters.get("date"):
                query += " AND h.visit_date::date = %s"
                params.append(filters["date"])
            if filters.get("doctor"):
                query += " AND h.registered_by ILIKE %s"
                params.append(f"%{filters['doctor']}%")
            if filters.get("medication"):
                query += " AND h.medication ILIKE %s"
                params.append(f"%{filters['medication']}%")
        cursor.execute(query, tuple(params))
        history = cursor.fetchall()
        cursor.close()
        connection.close()
        return history
    except Exception as e:
        print(f"Error fetching filtered history: {e}")
        return []