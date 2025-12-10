import pathlib
import sys
import os
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))
from dotenv import load_dotenv
from config.config import settings
import mysql.connector

load_dotenv()

conn = mysql.connector.connect(
    host=settings.HOST,
    user=settings.USERNAME,
    password=settings.PASSWORD,
    database=settings.DATABASE_NAME,
    port=settings.PORT
)

print("Database connection established", conn.is_connected())
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())


def get_connection():
    return mysql.connector.connect(
        host=settings.HOST,
        user=settings.USERNAME,
        password=settings.PASSWORD,
        database=settings.DATABASE_NAME,
        port=settings.PORT
    )



if __name__ == "__main__":
    get_connection()
    print("Connection successful")
