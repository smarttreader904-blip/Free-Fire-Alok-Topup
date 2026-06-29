# config.py

import os

# =========================
# BOT CONFIGURATION
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin Telegram ID
ADMIN_ID = 8385436442

# =========================
# DEFAULT PAYMENT METHODS
# =========================

BKASH_NUMBER = "0189052****6"
NAGAD_NUMBER = "017XXXXXXXX"
BINANCE_ID = "123456789"

# =========================
# BONUS SYSTEM
# =========================

BONUS_AMOUNT = 1
BONUS_COOLDOWN = 86400
REFERRAL_BONUS = 5

# =========================
# DEFAULT DIAMOND PRICES
# =========================

DEFAULT_PRICES = {
    "25 Diamond": 27,
    "50 Diamond": 42,
    "115 Diamond": 86,
    "240 Diamond": 168,
    "355 Diamond": 250,
    "480 Diamond": 325,
    "610 Diamond": 410,
    "850 Diamond": 560,
    "1240 Diamond": 800,
    "2530 Diamond": 1600,
    "5060 Diamond": 3200,
    "10120 Diamond": 6400,
    "Weekly": 170,
    "Monthly": 910
}
