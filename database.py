# database.py

import sqlite3


# ==========================================
# DATABASE CONNECTION
# ==========================================

def connect():

    conn = sqlite3.connect(
        "bot.db"
    )

    return conn


# ==========================================
# CREATE TABLES
# ==========================================

def init_db():

    conn = connect()

    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (

        user_id INTEGER PRIMARY KEY,

        balance REAL DEFAULT 0,

        last_bonus INTEGER DEFAULT 0

    )
    """)

    # DEPOSITS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS deposits (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        method TEXT,

        sender_info TEXT,

        trx_id TEXT

    )
    """)

    # ORDERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        offer_name TEXT,

        price REAL,

        game_name TEXT,

        uid TEXT,

        level TEXT

    )
    """)

    # SETTINGS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (

        key TEXT PRIMARY KEY,

        value TEXT

    )
    """)

    # PRICES TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prices (

        offer TEXT PRIMARY KEY,

        price REAL

    )
    """)

    conn.commit()

    conn.close()
    # ==========================================
# USER FUNCTIONS
# ==========================================

def add_user(user_id):

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id)
        VALUES (?)
        """,
        (user_id,)
    )

    conn.commit()

    conn.close()


# ==========================================
# GET BALANCE
# ==========================================

def get_balance(user_id):

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT balance
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    data = cur.fetchone()

    conn.close()

    if data:
        return data[0]

    return 0


# ==========================================
# ADD BALANCE
# ==========================================

def update_balance(user_id, amount):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET balance = balance + ?
        WHERE user_id = ?
        """,
        (amount, user_id)
    )

    conn.commit()
    conn.close()


# ==========================================
# DEDUCT BALANCE
# ==========================================

def deduct_balance(
        user_id,
        amount):

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET balance = balance - ?
        WHERE user_id=?
        """,
        (amount, user_id)
    )

    conn.commit()

    conn.close()
# ==========================================
# BONUS FUNCTIONS
# ==========================================

def get_last_bonus(user_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT last_bonus FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    conn.close()

    if row:
        return row[0] or 0

    return 00

# ==========================================
# SET LAST BONUS TIME
# ==========================================

def set_last_bonus(user_id, timestamp):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET last_bonus = ?
        WHERE user_id = ?
        """,
        (timestamp, user_id)
    )

    conn.commit()
    conn.close()


# ==========================================
# ADD DEPOSIT
# ==========================================

def add_deposit(
        user_id,
        method,
        sender_info,
        trx_id):

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO deposits
        (user_id, method, sender_info, trx_id)

        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            method,
            sender_info,
            trx_id
        )
    )

    deposit_id = cur.lastrowid

    conn.commit()

    conn.close()

    return deposit_id


# ==========================================
# GET DEPOSIT
# ==========================================

def get_deposit(deposit_id):

    conn = connect()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM deposits
        WHERE id=?
        """,
        (deposit_id,)
    )

    data = cur.fetchone()

    conn.close()

    return data
# ==========================================
# ORDER FUNCTIONS
# ==========================================

def add_order(
        user_id,
        offer_name,
        price,
        game_name,
        uid,
        level):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO orders
        (user_id, offer_name, price, game_name, uid, level)

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            offer_name,
            price,
            game_name,
            uid,
            level
        )
    )

    order_id = cur.lastrowid

    conn.commit()
    conn.close()

    return order_id


def get_order(order_id):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM orders
        WHERE id=?
        """,
        (order_id,)
    )

    data = cur.fetchone()

    conn.close()

    return data


# ==========================================
# PRICE FUNCTIONS
# ==========================================

def get_price(offer):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT price
        FROM prices
        WHERE offer=?
        """,
        (offer,)
    )

    data = cur.fetchone()

    conn.close()

    if data:
        return data[0]

    # Default Price List
    default_prices = {
        "25 Diamond": 27,
        "50 Diamond": 42,
        "115 Diamond": 86,
        "240 Diamond": 168,
        "355 Diamond": 250,
        "480 Diamond": 325,
        "610 Diamond": 410,
        "850 Diamond": 560,
        "1240 Diamond": 820,
        "2530 Diamond": 1650,
        "5060 Diamond": 3250,
        "10120 Diamond": 6500,
        "Weekly": 170,
        "Monthly": 910
    }

    return default_prices.get(offer, 0)


def set_price(
        offer,
        price):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO prices
        (offer, price)

        VALUES (?, ?)
        """,
        (offer, price)
    )

    conn.commit()
    conn.close()


# ==========================================
# PAYMENT SETTINGS
# ==========================================

def get_setting(key):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT value
        FROM settings
        WHERE key=?
        """,
        (key,)
    )

    data = cur.fetchone()

    conn.close()

    if data:
        return data[0]

    defaults = {
        "bkash": "0189052****6",
        "nagad": "017XXXXXXXX",
        "binance": "example_binance_id"
    }

    return defaults.get(key, "Not Set")


def set_setting(
        key,
        value):

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO settings
        (key, value)

        VALUES (?, ?)
        """,
        (key, value)
    )

    conn.commit()
    conn.close()


# ==========================================
# GET ALL USERS
# ==========================================

def get_all_users():

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id FROM users"
    )

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]
