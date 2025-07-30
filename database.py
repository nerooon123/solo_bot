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
        free_points INTEGER DEFAULT 100,
        title TEXT DEFAULT 'Без титула',
        profession TEXT DEFAULT 'Без профессии',
        level INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        hp INTEGER DEFAULT 100,
        mp INTEGER DEFAULT 100
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        difficulty TEXT,
        goal TEXT,
        reward TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_quests (
        user_id INTEGER,
        quest_id INTEGER,
        completed INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, quest_id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        name TEXT PRIMARY KEY,
        description TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        quality TEXT,
        description TEXT
    )
    """)
    try:
        cursor.execute("""
        ALTER TABLE users ADD COLUMN inventory TEXT DEFAULT ''
        """)
    except sqlite3.OperationalError:
        # Колонка уже существует — игнорируем ошибку
        pass
    # Если поле inventory уже есть — игнорируйте ошибку, или используйте try/except
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("""
        INSERT INTO users (user_id, username, inventory)
        VALUES (?, ?, ?)
        """, (user_id, username, '[]'))
    conn.commit()
    conn.close()

def get_user_profile(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_quest(title, description, difficulty, goal, reward):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quests (title, description, difficulty, goal, reward)
        VALUES (?, ?, ?, ?, ?)
    """, (title, description, difficulty, goal, reward))
    conn.commit()
    conn.close()

def get_quests_page(page: int, page_size: int = 5):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM quests")
    total = cursor.fetchone()[0]
    cursor.execute(
        "SELECT id, title, description, difficulty, goal, reward FROM quests LIMIT ? OFFSET ?",
        (page_size, page * page_size)
    )
    quests = cursor.fetchall()
    conn.close()
    return quests, total

def is_quest_completed(user_id: int, quest_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT completed FROM user_quests WHERE user_id = ? AND quest_id = ?",
        (user_id, quest_id)
    )
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == 1

def complete_quest(user_id: int, quest_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO user_quests (user_id, quest_id, completed) VALUES (?, ?, 1)",
        (user_id, quest_id)
    )
    conn.commit()
    conn.close()

def add_xp_and_level(user_id: int, xp_to_add: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT level, xp FROM users WHERE user_id = ?", (user_id,))
    level, xp = cursor.fetchone()
    xp += xp_to_add
    leveled_up = False
    while True:
        next_level_xp = 100 + level * 10
        if xp >= next_level_xp:
            xp -= next_level_xp
            level += 1
            leveled_up = True
        else:
            break
    cursor.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (xp, level, user_id))
    conn.commit()
    conn.close()
    return leveled_up, level

def add_skill(name: str, description: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO skills (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    conn.close()

def add_item(name, quality, description):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, quality, description) VALUES (?, ?, ?)", (name, quality, description))
    conn.commit()
    conn.close()
