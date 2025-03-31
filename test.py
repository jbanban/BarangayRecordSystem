import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="barangayrecordsystem"
    )
    print("Connected successfully!")
    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
