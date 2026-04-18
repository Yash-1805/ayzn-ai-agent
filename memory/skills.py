# =====================================================
# memory/skills.py
# Step Skill Library for AYZN
# Reusable Atomic Skills Memory
# =====================================================

import sqlite3
import json
from rapidfuzz import process, fuzz


DB_PATH = "memory/brain.db"


# =====================================================
# INIT TABLE
# =====================================================

def init_skills():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        category TEXT,
        steps TEXT,
        uses INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# SAVE SKILL
# =====================================================

def save_skill(name, steps, category="general"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT id, uses FROM skills
    WHERE name=?
    """, (name,))

    row = cur.fetchone()

    if row:
        cur.execute("""
        UPDATE skills
        SET uses=?, steps=?
        WHERE id=?
        """, (
            row[1] + 1,
            json.dumps(steps),
            row[0]
        ))

        print(f"[SKILL UPDATED] {name}")

    else:
        cur.execute("""
        INSERT INTO skills
        (name, category, steps)
        VALUES (?, ?, ?)
        """, (
            name,
            category,
            json.dumps(steps)
        ))

        print(f"[SKILL SAVED] {name}")

    conn.commit()
    conn.close()


# =====================================================
# GET EXACT SKILL
# =====================================================

def get_skill(name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT steps
    FROM skills
    WHERE name=?
    """, (name,))

    row = cur.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])

    return None


# =====================================================
# FUZZY FIND SKILL
# =====================================================

def find_skill(query):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT name, steps
    FROM skills
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    names = [r[0] for r in rows]

    result = process.extractOne(
        query,
        names,
        scorer=fuzz.ratio
    )

    if not result:
        return None

    best_name, score, idx = result

    if score >= 75:
        print(f"[SKILL HIT ⚡] {best_name}")
        return json.loads(rows[idx][1])

    return None


# =====================================================
# LIST ALL SKILLS
# =====================================================

def list_skills():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT name, category, uses
    FROM skills
    ORDER BY uses DESC
    """)

    rows = cur.fetchall()
    conn.close()

    print("\n====== SKILLS ======")

    for row in rows:
        print(row)

    print("====================")


# =====================================================
# DELETE SKILL
# =====================================================

def delete_skill(name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM skills
    WHERE name=?
    """, (name,))

    conn.commit()
    conn.close()

    print(f"[SKILL DELETED] {name}")


# =====================================================
# CLEAR ALL
# =====================================================

def clear_skills():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM skills")

    conn.commit()
    conn.close()

    print("[ALL SKILLS CLEARED]")


# =====================================================
# AUTO EXTRACT COMMON SKILLS
# =====================================================

def auto_learn_from_steps(steps):
    for step in steps:
        action = step.get("action")
        value = step.get("value", "").lower()

        if action == "open_app":
            save_skill(
                f"open_{value}",
                [step],
                "app"
            )

        elif action == "hotkey" and value == "command+t":
            save_skill(
                "new_tab",
                [step],
                "browser"
            )

        elif action == "press_key" and value == "space":
            save_skill(
                "play_pause",
                [step],
                "media"
            )


# =====================================================
# GET ALL SKILL NAMES
# =====================================================

def get_skill_names():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT name
    FROM skills
    ORDER BY uses DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]


# =====================================================
# INIT
# =====================================================

init_skills()