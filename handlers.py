# handlers.py

import time

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import (
    add_user,
    get_balance,
    get_last_bonus,
    set_last_bonus,
    update_balance
)

from config import BONUS_AMOUNT, BONUS_COOLDOWN
from keyboards import (
    start_kb,
    payment_kb,
    offer_kb
)

router = Router()


# ==========================================
# FSM STATES
# ==========================================

class DepositState(StatesGroup):
    waiting_sender_info = State()
    waiting_trx_id = State()


class BuyState(StatesGroup):
    waiting_game_name = State()
    waiting_uid = State()
    waiting_level = State()


class PriceState(StatesGroup):
    waiting_new_price = State()
    waiting_new_number = State()


class RejectState(StatesGroup):
    waiting_reason = State()


class BroadcastState(StatesGroup):
    waiting_message = State()


# ==========================================
# /START COMMAND
# ==========================================

@router.message(Command("start"))
async def start_cmd(message: Message):

    add_user(message.from_user.id)

    text = f"""
👋 Welcome {message.from_user.first_name}

🔥 Welcome To Topup Bot

নিচের মেনু থেকে একটি অপশন নির্বাচন করুন।
"""

    await message.answer(
        text,
        reply_markup=start_kb
    )


# ==========================================
# BALANCE COMMAND
# ==========================================

@router.message(Command("balance"))
@router.message(F.text == "💰 Balance")
async def balance_cmd(message: Message):

    balance = get_balance(message.from_user.id)

    await message.answer(
        f"💰 Your Current Balance:\n\n{balance} Tk"
    )


# ==========================================
# BONUS COMMAND
# ==========================================

@router.message(Command("bonus"))
@router.message(F.text == "🎉 Bonus")
async def bonus_cmd(message: Message):

    user_id = message.from_user.id

    last_bonus = get_last_bonus(user_id)
    current_time = int(time.time())

    remaining = BONUS_COOLDOWN - (current_time - last_bonus)

    if remaining > 0:

        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        await message.answer(
            f"❌ আপনি ইতিমধ্যে Bonus নিয়েছেন.\n\n"
            f"আবার Bonus নিতে অপেক্ষা করুন:\n"
            f"{hours} ঘণ্টা {minutes} মিনিট"
        )
        return

    update_balance(user_id, BONUS_AMOUNT)
    set_last_bonus(user_id, current_time)

    await message.answer(
        f"🎉 Bonus Claimed Successfully!\n\n"
        f"💰 {BONUS_AMOUNT} Tk আপনার Balance এ যোগ করা হয়েছে।"
    )


# ==========================================
# ADD BALANCE BUTTON
# ==========================================

@router.message(F.text == "➕ Add Balance")
async def add_balance_menu(message: Message):

    await message.answer(
        "💳 Payment Method নির্বাচন করুন:",
        reply_markup=payment_kb
    )


# ==========================================
# OFFER BUTTON
# ==========================================

@router.message(F.text == "🎁 Offer")
async def offer_menu(message: Message):

    await message.answer(
        "🛒 নিচের Offer থেকে একটি নির্বাচন করুন:",
        reply_markup=offer_kb
    )
  # ==========================================
# PAYMENT METHOD CALLBACK
# ==========================================

from aiogram.types import CallbackQuery
from config import ADMIN_ID
from database import get_setting, add_deposit

@router.callback_query(F.data.startswith("pay_"))
async def payment_method(callback: CallbackQuery, state: FSMContext):

    method = callback.data.split("_")[1]

    if method == "bkash":
        number = get_setting("bkash")

    elif method == "nagad":
        number = get_setting("nagad")

    else:
        number = get_setting("binance")

    await state.update_data(method=method)

    await callback.message.edit_text(
        f"""
💳 Payment Method: {method.upper()}

নাম্বার / ID:
{number}

পেমেন্ট সম্পন্ন করার পর যেই নাম্বার থেকে টাকা পাঠিয়েছেন,
সেই নাম্বারের শেষ ৩ সংখ্যা লিখুন।
"""
    )

    await state.set_state(
        DepositState.waiting_sender_info
    )

    await callback.answer()


# ==========================================
# RECEIVE SENDER INFO
# ==========================================

@router.message(
    DepositState.waiting_sender_info
)
async def sender_info_handler(
        message: Message,
        state: FSMContext):

    await state.update_data(
        sender_info=message.text
    )

    await message.answer(
        "🧾 এখন Transaction ID পাঠান:"
    )

    await state.set_state(
        DepositState.waiting_trx_id
    )


# ==========================================
# RECEIVE TRX ID
# ==========================================

@router.message(
    DepositState.waiting_trx_id
)
async def trx_handler(
        message: Message,
        state: FSMContext):

    data = await state.get_data()

    method = data["method"]
    sender = data["sender_info"]
    trx_id = message.text

    deposit_id = add_deposit(
        message.from_user.id,
        method,
        sender,
        trx_id
    )

    await message.answer(
        """
✅ আপনার রিকোয়েস্ট এডমিনের কাছে পৌঁছে গেছে।

⏳ দয়া করে ১ থেকে ৫ মিনিট অপেক্ষা করুন।

এডমিন আপনার Balance Add করে দিবে।
"""
    )

    await message.bot.send_message(
        ADMIN_ID,
        f"""
💰 New Deposit Request

Deposit ID: {deposit_id}

👤 User: {message.from_user.full_name}
🆔 User ID: {message.from_user.id}

💳 Method: {method.upper()}
📱 Sender Last 3 Digit: {sender}
🧾 TRX ID: {trx_id}
"""
    )

    await state.clear()
          # ======================
# ORDER FUNCTIONS
# ======================

def add_order(user_id, offer_name, price, game_name, uid, level):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO orders
    (user_id, offer_name, price, game_name, uid, level)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, offer_name, price, game_name, uid, level))

    order_id = cur.lastrowid

    conn.commit()
    conn.close()

    return order_id


def deduct_balance(user_id, amount):
    conn = connect()
    cur = conn.cursor()
  from database import (
    get_price,
    add_order,
    deduct_balance
)

from keyboards import (
    buy_offer_kb,
    order_admin_kb
)

# ==========================================
# SHOW OFFER PRICE
# ==========================================

@router.callback_query(F.data.startswith("offer_"))
async def show_offer(callback: CallbackQuery):

    offer = callback.data.replace("offer_", "")
    price = get_price(offer)

    await callback.message.edit_text(
        f"""
🛒 Offer: {offer}

💰 Price: {price} Tk

নিচের বাটনে ক্লিক করে অর্ডার করুন।
""",
        reply_markup=buy_offer_kb(offer)
    )

    await callback.answer()


# ==========================================
# BUY OFFER
# ==========================================

@router.callback_query(F.data.startswith("buy_"))
async def buy_offer(
        callback: CallbackQuery,
        state: FSMContext):

    offer = callback.data.replace("buy_", "")

    price = get_price(offer)

    balance = get_balance(
        callback.from_user.id
    )

    if balance < price:

        await callback.answer(
            "❌ আপনার Balance যথেষ্ট নেই।",
            show_alert=True
        )
        return

    await state.update_data(
        offer=offer,
        price=price
    )

    await callback.message.edit_text(
        "🎮 Please আপনার Game Name লিখুন:"
    )

    await state.set_state(
        BuyState.waiting_game_name
    )

    await callback.answer()


# ==========================================
# GAME NAME
# ==========================================

@router.message(
    BuyState.waiting_game_name
)
async def game_name_handler(
        message: Message,
        state: FSMContext):

    await state.update_data(
        game_name=message.text
    )

    await message.answer(
        "🆔 আপনার UID লিখুন:"
    )

    await state.set_state(
        BuyState.waiting_uid
    )


# ==========================================
# UID
# ==========================================

@router.message(
    BuyState.waiting_uid
)
async def uid_handler(
        message: Message,
        state: FSMContext):

    await state.update_data(
        uid=message.text
    )

    await message.answer(
        "⭐ আপনার Level কত লিখুন:"
    )

    await state.set_state(
        BuyState.waiting_level
    )


# ==========================================
# LEVEL + SEND ADMIN
# ==========================================

@router.message(
    BuyState.waiting_level
)
async def level_handler(
        message: Message,
        state: FSMContext):

    data = await state.get_data()

    offer = data["offer"]
    price = data["price"]
    game_name = data["game_name"]
    uid = data["uid"]
    level = message.text

    deduct_balance(
        message.from_user.id,
        price
    )

    order_id = add_order(
        message.from_user.id,
        offer,
        price,
        game_name,
        uid,
        level
    )

    await message.answer(
        f"""
✅ Order Submitted Successfully

🛒 Offer: {offer}
💰 Price: {price} Tk

দয়া করে অপেক্ষা করুন।
"""
    )

    await message.bot.send_message(
        ADMIN_ID,
        f"""
🛒 New Order

Order ID: {order_id}

👤 User: {message.from_user.full_name}
🆔 User ID: {message.from_user.id}

🎁 Offer: {offer}
💰 Price: {price} Tk

🎮 Game: {game_name}
🆔 UID: {uid}
⭐ Level: {level}
""",
        reply_markup=order_admin_kb(
            order_id
        )
    )

    await state.clear()

    cur.execute(
        "UPDATE users SET balance = balance - ? WHERE user_id=?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()
          
