# database.py

import sqlite3
from config import DEFAULT_PRICES

DB_NAME = "bot.db"


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cur = conn.cursor()

    # Users Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0,
        last_bonus INTEGER DEFAULT 0
    )
    """)

    # Prices Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        offer_name TEXT PRIMARY KEY,
        price REAL
    )
    """)

    # Settings Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Deposits Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS deposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        method TEXT,
        sender_info TEXT,
        trx_id TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    # Orders Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        offer_name TEXT,
        price REAL,
        game_name TEXT,
        uid TEXT,
        level TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    conn.commit()

    # Default Prices Insert
    for offer, price in DEFAULT_PRICES.items():
        cur.execute(
            "INSERT OR IGNORE INTO prices (offer_name, price) VALUES (?, ?)",
            (offer, price)
        )

    # Default Payment Methods
    cur.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)",
                ("bkash", "0189052****6"))

    cur.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)",
                ("nagad", "017XXXXXXXX"))

    cur.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)",
                ("binance", "123456789"))

    conn.commit()
    conn.close()


# ======================
# USER FUNCTIONS
# ======================

def add_user(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

    conn.commit()
    conn.close()


def get_balance(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cur.fetchone()
    conn.close()

    if data:
        return data[0]
    return 0


def update_balance(user_id, amount):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id=?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()


# ======================
# BONUS FUNCTIONS
# ======================

def get_last_bonus(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT last_bonus FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cur.fetchone()
    conn.close()

    if data:
        return data[0]
    return 0


def set_last_bonus(user_id, timestamp):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET last_bonus=? WHERE user_id=?",
        (timestamp, user_id)
    )

    conn.commit()
    conn.close()


# ======================
# PRICE FUNCTIONS
# ======================

def get_price(offer):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT price FROM prices WHERE offer_name=?",
        (offer,)
    )

    data = cur.fetchone()
    conn.close()

    if data:
        return data[0]
    return None


def set_price(offer, new_price):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE prices SET price=? WHERE offer_name=?",
        (new_price, offer)
    )

    conn.commit()
    conn.close()


def get_all_prices():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT offer_name, price FROM prices")

    data = cur.fetchall()
    conn.close()

    return data


# ======================
# PAYMENT METHODS
# ======================

def get_setting(key):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT value FROM settings WHERE key=?",
        (key,)
    )

    data = cur.fetchone()
    conn.close()

    if data:
        return data[0]
    return None


def set_setting(key, value):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO settings (key, value)
    VALUES (?, ?)
    """, (key, value))

    conn.commit()
    conn.close()
