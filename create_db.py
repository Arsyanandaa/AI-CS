import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    # Ubah "password_kamu" di bawah ini sesuai password postgres laptopmu!
    conn = psycopg2.connect(user="postgres", password="GGgaming123#$#$", host="127.0.0.1", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE DATABASE gamepay_db;")
        print("Database 'gamepay_db' berhasil dibuat, bro!")
    except psycopg2.errors.DuplicateDatabase:
        print("Database 'gamepay_db' ternyata sudah ada.")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_database()