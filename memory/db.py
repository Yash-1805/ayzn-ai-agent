import sqlite3

def get_connection():
    conn = sqlite3.connect(
        "memory.db",
        check_same_thread=False,
        timeout=5
    )

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    return conn


# create table once
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrases TEXT,
    embedding TEXT,
    steps TEXT
)
""")

conn.commit()
cursor.close()
conn.close()