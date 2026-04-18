# =====================================================
# memory/manager.py
# FINAL Optimized AYZN Memory System
# No LLM calls during retrieval
# Exact -> Intent Cache -> Fuzzy
# =====================================================

import sqlite3
import json
from rapidfuzz import process, fuzz


DB_PATH = "memory/brain.db"


# =====================================================
# DB
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def init_memory():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_command TEXT UNIQUE,
        intent TEXT,
        category TEXT,
        steps TEXT,
        uses INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# NORMALIZE
# =====================================================

def normalize(text):
    text = text.lower().strip()
    text = " ".join(text.split())

    fillers = [
        "lets", "let's", "please",
        "can you", "could you",
        "yo", "hey", "ayzn"
    ]

    for x in fillers:
        text = text.replace(x, "")

    return " ".join(text.split()).strip()


# =====================================================
# SAVE MEMORY
# =====================================================

def save_memory(command, steps, intent="general_task", category="general"):
    print("\n[MEMORY SAVE]")

    command = normalize(command)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, uses FROM memories
    WHERE raw_command=?
    """, (command,))

    row = cur.fetchone()

    if row:
        cur.execute("""
        UPDATE memories
        SET steps=?, uses=?, intent=?, category=?
        WHERE id=?
        """, (
            json.dumps(steps),
            row[1] + 1,
            intent,
            category,
            row[0]
        ))

        print("[MEMORY UPDATED]")

    else:
        cur.execute("""
        INSERT INTO memories
        (raw_command, intent, category, steps)
        VALUES (?, ?, ?, ?)
        """, (
            command,
            intent,
            category,
            json.dumps(steps)
        ))

        print("[MEMORY NEW]")

    conn.commit()
    conn.close()


# =====================================================
# EXACT
# =====================================================

def exact_match(command):
    command = normalize(command)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT steps
    FROM memories
    WHERE raw_command=?
    """, (command,))

    row = cur.fetchone()
    conn.close()

    if row:
        print("[L1 EXACT HIT ⚡]")
        return json.loads(row[0])

    return None


# =====================================================
# INTENT CACHE (NO LLM)
# =====================================================

def intent_match(command):
    command = normalize(command)

    words = command.split()

    if len(words) >= 2:
        guess = "_".join(words[:2])
    else:
        guess = command.replace(" ", "_")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT steps
    FROM memories
    WHERE intent=?
    ORDER BY uses DESC
    LIMIT 1
    """, (guess,))

    row = cur.fetchone()
    conn.close()

    if row:
        print("[L2 INTENT HIT ⚡]")
        return json.loads(row[0])

    return None


# =====================================================
# FUZZY
# =====================================================

def fuzzy_match(command):
    command = normalize(command)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT raw_command, steps
    FROM memories
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("[MEMORY] EMPTY")
        return None

    choices = [r[0] for r in rows]

    result = process.extractOne(
        command,
        choices,
        scorer=fuzz.ratio
    )

    if not result:
        return None

    best, score, idx = result

    print(f"[L3 SCORE] {score}")

    if score >= 60:
        print("[L3 FUZZY HIT ⚡]")
        return json.loads(rows[idx][1])

    return None


# =====================================================
# MAIN GET
# =====================================================

def get_memory(command):
    print("\n[MEMORY] START")

    result = exact_match(command)
    if result:
        return result

    result = intent_match(command)
    if result:
        return result

    result = fuzzy_match(command)
    if result:
        return result

    print("[MEMORY] MISS")
    return None


# =====================================================
# SHOW
# =====================================================

def show_memory():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, raw_command, intent, category, uses
    FROM memories
    ORDER BY uses DESC
    """)

    rows = cur.fetchall()
    conn.close()

    print("\n====== MEMORY ======")

    for row in rows:
        print(row)

    print("====================")


# =====================================================
# DELETE
# =====================================================

def delete_memory(command):
    command = normalize(command)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM memories
    WHERE raw_command=?
    """, (command,))

    conn.commit()
    conn.close()

    print("[MEMORY DELETED]")


def clear_memory():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM memories")

    conn.commit()
    conn.close()

    print("[MEMORY CLEARED]")


# =====================================================
# INIT
# =====================================================

init_memory()