import psycopg2

def get_connection():
    try:
        print("Attempting to connect to the database...")
        connection = psycopg2.connect(
            dbname="vetbase",                # Nazwa bazy danych
            user="vetbase_user",            # Użytkownik bazy danych
            password="vetbase_password",    # Hasło użytkownika
            host="host.docker.internal",               # Host (dla lokalnej bazy)
            port="5432",                    # Port PostgreSQL
            connect_timeout=5               # Timeout połączenia (5 sekund)
        )
        print("Connection established successfully!")
        return connection
    except psycopg2.OperationalError as e:
        print("OperationalError: Could not connect to the database. Details:", e)
        return None
    except Exception as e:
        print("Unexpected error occurred:", e)
        return None