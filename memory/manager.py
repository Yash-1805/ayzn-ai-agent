import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from memory.db import get_connection


# ---------------- VECTOR MODEL ----------------

vectorizer = TfidfVectorizer()
memory_texts = []  # stores all phrases for fitting


# ---------------- NORMALIZATION ----------------

def normalize_text(text):
    return text.lower().strip()


# ---------------- ENCODING ----------------

def encode_all_texts(texts):
    global vectorizer
    return vectorizer.fit_transform(texts).toarray()


def encode_query(query):
    global vectorizer, memory_texts

    if not memory_texts:
        return None

    return vectorizer.transform([query]).toarray()[0]


# ---------------- SIMILARITY ----------------

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


# ---------------- LOAD MEMORY TEXTS ----------------

def load_memory_texts():
    global memory_texts

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT phrases FROM memory")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    memory_texts = []

    for row in rows:
        phrases = json.loads(row[0])
        memory_texts.extend(phrases)


# ---------------- GET MEMORY ----------------

def get_memory(task, threshold=0.3):
    print("\n[MEMORY] START")

    task = normalize_text(task)

    # -------- LOAD TEXTS --------
    load_memory_texts()

    if not memory_texts:
        print("[MEMORY] EMPTY")
        return None

    print("[DEBUG] fitting vectorizer")
    embeddings = encode_all_texts(memory_texts)

    query_vec = encode_query(task)

    print("[DEBUG] DB fetch start")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT phrases, steps FROM memory")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    print("[DEBUG] DB fetch done")

    best_score = 0
    best_steps = None
    idx = 0

    for row in rows:
        phrases, steps_str = row
        phrases = json.loads(phrases)

        for _ in phrases:
            emb = embeddings[idx]

            score = cosine(query_vec, emb)

            if score > best_score:
                best_score = score
                best_steps = steps_str

            idx += 1

    print(f"[MEMORY] best score = {best_score}")

    if best_score > threshold:
        print("[MEMORY] HIT ⚡")
        return json.loads(best_steps)

    print("[MEMORY] MISS")
    return None


# ---------------- SAVE / MERGE ----------------

def save_memory(task, steps, merge_threshold=0.4):
    print("\n[MEMORY SAVE]")

    task = normalize_text(task)

    load_memory_texts()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, phrases FROM memory")
    rows = cursor.fetchall()

    best_id = None
    best_score = 0

    if memory_texts:
        embeddings = encode_all_texts(memory_texts)
        query_vec = encode_query(task)

        idx = 0

        for row in rows:
            _id, phrases = row
            phrases = json.loads(phrases)

            for _ in phrases:
                emb = embeddings[idx]

                score = cosine(query_vec, emb)

                if score > best_score:
                    best_score = score
                    best_id = _id

                idx += 1

    # -------- MERGE --------
    if best_score > merge_threshold:
        print(f"[MEMORY MERGE] score={best_score:.2f}")

        cursor.execute("SELECT phrases FROM memory WHERE id=?", (best_id,))
        old_phrases = json.loads(cursor.fetchone()[0])

        if task not in old_phrases:
            old_phrases.append(task)

        cursor.execute(
            "UPDATE memory SET phrases=? WHERE id=?",
            (json.dumps(old_phrases), best_id)
        )

    # -------- NEW --------
    else:
        print("[MEMORY NEW]")

        cursor.execute(
            "INSERT INTO memory (phrases, embedding, steps) VALUES (?, ?, ?)",
            (
                json.dumps([task]),
                json.dumps([]),  # not used anymore
                json.dumps(steps)
            )
        )

    conn.commit()
    cursor.close()
    conn.close()