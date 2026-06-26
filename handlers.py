# handlers.py

import time

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import (
    ADMIN_ID,
    BONUS_AMOUNT,
    BONUS_COOLDOWN
)

from database import (
    add_user,
    get_balance,
    update_balance,
    get_last_bonus,
    set_last_bonus,
    get_setting,
    add_deposit,
    get_price,
    add_order,
    deduct_balance
)

from keyboards import (
    start_kb,
    payment_kb,
    offer_kb,
    buy_offer_kb,
    order_admin_kb
)

router = Router()

# ==========================================
# STATES
# ==========================================

class DepositState(StatesGroup):
    waiting_sender_info = State()
    waiting_trx_id = State()


class BuyState(StatesGroup):
    waiting_game_name = State()
    waiting_uid = State()
    waiting_level = State()


# ==========================================
# /START
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
# BALANCE
# ==========================================

@router.message(Command("balance"))
@router.message(F.text == "💰 Balance")
async def balance_cmd(message: Message):

    balance = get_balance(
        message.from_user.id
    )

    await message.answer(
        f"""
💰 Your Current Balance

Balance: {balance} Tk
"""
    )


# ==========================================
# BONUS
# ==========================================

@router.message(Command("bonus"))
@router.message(F.text == "🎉 Bonus")
async def bonus_cmd(message: Message):

    user_id = message.from_user.id

    last_bonus = get_last_bonus(user_id)
    current_time = int(time.time())

    remaining = BONUS_COOLDOWN - (
            current_time - last_bonus
    )

    if remaining > 0:

        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        await message.answer(
            f"""
❌ আপনি ইতিমধ্যে Bonus নিয়েছেন।

আবার Bonus নিতে অপেক্ষা করুন:

{hours} ঘণ্টা {minutes} মিনিট
"""
        )
        return

    update_balance(
        user_id,
        BONUS_AMOUNT
    )

    set_last_bonus(
        user_id,
        current_time
    )

    await message.answer(
        f"""
🎉 Bonus Claimed Successfully

💰 {BONUS_AMOUNT} Tk Balance এ যোগ করা হয়েছে।
"""
    )


# ==========================================
# ADD BALANCE BUTTON
# ==========================================

@router.message(F.text == "➕ Add Balance")
async def add_balance_menu(
        message: Message):

    await message.answer(
        "💳 Payment Method নির্বাচন করুন:",
        reply_markup=payment_kb
    )


# ==========================================
# OFFER BUTTON
# ==========================================

@router.message(F.text == "🎁 Offer")
async def offer_menu(
        message: Message):

    await message.answer(
        "🛒 নিচের Offer থেকে একটি নির্বাচন করুন:",
        reply_markup=offer_kb
)
