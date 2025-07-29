import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        strength INTEGER DEFAULT 5,
        agility INTEGER DEFAULT 5,
        endurance INTEGER DEFAULT 5,
        perception INTEGER DEFAULT 5,
        intelligence INTEGER DEFAULT 5,
        charisma INTEGER DEFAULT 5,
        willpower INTEGER DEFAULT 5,
        skills TEXT DEFAULT '',
        free_points INTEGER DEFAULT 100
    )
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("""
        INSERT INTO users (user_id, username)
        VALUES (?, ?)
        """, (user_id, username))
    conn.commit()
    conn.close()

def get_user_profile(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user
