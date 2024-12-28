from database.connection import get_connection

if __name__ == "__main__":
    connection = get_connection()
    if connection:
        print("Connection test successful!")
        connection.close()
    else:
        print("Connection test failed.")