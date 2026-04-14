import json
from memory.db import get_connection


def save_skill(name, steps):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        steps TEXT
    )
    """)

    try:
        cursor.execute(
            "INSERT INTO skills (name, steps) VALUES (?, ?)",
            (name, json.dumps(steps))
        )
        print(f"[SKILL SAVED] {name}")
    except:
        pass

    conn.commit()
    cursor.close()
    conn.close()


def get_all_skills():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, steps FROM skills")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [(r[0], json.loads(r[1])) for r in rows]