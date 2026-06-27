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
    BONUS_COOLDOWN,
    REFERRAL_BONUS
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
    deduct_balance,
    get_order,
    get_deposit,
    get_all_users,
    set_price,
has_referred,
save_referral,
    set_setting
)

from keyboards import (
    start_kb,
    payment_kb,
    offer_kb,
    buy_offer_kb,
    order_admin_kb,
    price_admin_kb,
    price_change_kb,
    deposit_admin_kb
)

router = Router()


# ==========================================
# STATES
# ==========================================

class DepositState(StatesGroup):
    waiting_sender_info = State()
    waiting_amount = State()
    waiting_trx_id = State()

class BuyState(StatesGroup):
    waiting_game_name = State()
    waiting_uid = State()
    waiting_level = State()


class PriceState(StatesGroup):
    waiting_new_price = State()


class PaymentState(StatesGroup):
    waiting_new_payment = State()
    
class SetMoneyState(StatesGroup):
    waiting_user_id = State()
    waiting_amount = State()

class RejectOrderState(StatesGroup):
    waiting_reason = State()


class RejectDepositState(StatesGroup):
    waiting_reason = State()


class ApproveDepositState(StatesGroup):
    waiting_amount = State()


# ==========================================
# /START
# ==========================================

@router.message(Command("start"))
async def start_cmd(message: Message):

    args = message.text.split()

    add_user(message.from_user.id)

    if len(args) > 1:

        referrer_id = int(args[1])

        if (
            referrer_id != message.from_user.id
            and not has_referred(message.from_user.id)
        ):

            update_balance(
                referrer_id,
                REFERRAL_BONUS
            )

            save_referral(
                message.from_user.id,
                referrer_id
            )

            try:
                await message.bot.send_message(
                    referrer_id,
                    f"🎉 আপনি {REFERRAL_BONUS} Tk Referral Bonus পেয়েছেন।"
                )
            except:
                pass

    await message.answer(
        f"""
👋 Welcome {message.from_user.first_name}

🔥 Welcome To Topup Bot

নিচের অপশন থেকে একটি সিলেক্ট করুন।
""",
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
💰 Your Balance

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
❌ আপনি Bonus নিয়েছেন।

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
🎉 Bonus Claimed

💰 {BONUS_AMOUNT} Tk Balance এ যোগ করা হয়েছে।
"""
    )


# ==========================================
# MAIN MENU BUTTONS
# ==========================================

@router.message(F.text == "➕ Add Balance")
async def add_balance_menu(
        message: Message):

    await message.answer(
        "💳 Payment Method নির্বাচন করুন:",
        reply_markup=payment_kb
    )


@router.message(F.text == "🎁 Offer")
async def offer_menu(
        message: Message):

    await message.answer(
        "🛒 নিচের Offer থেকে একটি নির্বাচন করুন:",
        reply_markup=offer_kb
)
# ==========================================
# PAYMENT METHOD CALLBACK
# ==========================================

@router.callback_query(F.data.startswith("pay_"))
async def payment_method(
        callback: CallbackQuery,
        state: FSMContext):

    method = callback.data.split("_")[1]

    if method == "bkash":
        number = get_setting("bkash")

    elif method == "nagad":
        number = get_setting("nagad")

    else:
        number = get_setting("binance")

    await state.update_data(
        method=method
    )

    await callback.message.edit_text(
        f"""
💳 Payment Method: {method.upper()}

📱 Number / ID:
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
# RECEIVE LAST 3 DIGIT
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
        "💰 আপনি কত টাকা Deposit করেছেন লিখুন:"
    )

    await state.set_state(
        DepositState.waiting_amount
    )


# ==========================================
# RECEIVE DEPOSIT AMOUNT
# ==========================================

@router.message(
    DepositState.waiting_amount
)
async def deposit_amount_handler(
        message: Message,
        state: FSMContext):

    await state.update_data(
        deposit_amount=message.text
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
    amount = data["deposit_amount"]
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
💰 Deposit Amount: {amount} Tk
🧾 TRX ID: {trx_id}
""",
        reply_markup=deposit_admin_kb(deposit_id)
    )

    await state.clear()
# ==========================================
# SHOW OFFER DETAILS
# ==========================================

@router.callback_query(F.data.startswith("offer_"))
async def show_offer(
        callback: CallbackQuery):

    offer = callback.data.replace(
        "offer_", ""
    )

    price = get_price(offer)

    await callback.message.edit_text(
        f"""
🛒 Offer Details

🎁 Offer: {offer}

💰 Price: {price} Tk

নিচের বাটনে ক্লিক করে Buy করুন।
""",
        reply_markup=buy_offer_kb(
            offer
        )
    )

    await callback.answer()


# ==========================================
# BUY OFFER
# ==========================================

@router.callback_query(F.data.startswith("buy_"))
async def buy_offer(
        callback: CallbackQuery,
        state: FSMContext):

    offer = callback.data.replace(
        "buy_", ""
    )

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
        "🎮 আপনার Game Name লিখুন:"
    )

    await state.set_state(
        BuyState.waiting_game_name
    )

    await callback.answer()


# ==========================================
# RECEIVE GAME NAME
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
        "🆔 এখন আপনার UID লিখুন:"
    )

    await state.set_state(
        BuyState.waiting_uid
    )


# ==========================================
# RECEIVE UID
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
# RECEIVE LEVEL + SEND ORDER
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

    # Balance কাটবে
    deduct_balance(
        message.from_user.id,
        price
    )

    # Order Save হবে
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

🎁 Offer: {offer}
💰 Price: {price} Tk

⏳ দয়া করে অপেক্ষা করুন।
এডমিন খুব দ্রুত আপনার Order Complete করবে।
"""
    )

    # Admin Notification
    await message.bot.send_message(
        ADMIN_ID,
        f"""
🛒 New Order

🆔 Order ID: {order_id}

👤 User: {message.from_user.full_name}
🆔 User ID: {message.from_user.id}

🎁 Offer: {offer}
💰 Price: {price} Tk

🎮 Game Name: {game_name}
🆔 UID: {uid}
⭐ Level: {level}
""",
        reply_markup=order_admin_kb(
            order_id
        )
    )

    await state.clear()
# ==========================================
# REJECT STATES
# ==========================================

class RejectOrderReasonState(StatesGroup):
    waiting_reason = State()


class RejectDepositReasonState(StatesGroup):
    waiting_reason = State()


class DepositApproveState(StatesGroup):
    waiting_amount = State()


# ==========================================
# ORDER APPROVE
# ==========================================

@router.callback_query(
    F.data.startswith("order_approve_")
)
async def order_approve(
        callback: CallbackQuery):

    order_id = int(
        callback.data.replace(
            "order_approve_", ""
        )
    )

    order = get_order(order_id)

    if not order:
        await callback.answer(
            "❌ Order পাওয়া যায়নি"
        )
        return

    user_id = order[1]

    await callback.bot.send_message(
        user_id,
        """
✅ আপনার Diamond দেওয়া হয়েছে।

🎮 দয়া করে গেমে প্রবেশ করে চেক করুন।
"""
    )

    await callback.message.edit_text(
        f"✅ Order #{order_id} Approved"
    )

    await callback.answer(
        "Approved Successfully"
    )


# ==========================================
# ORDER REJECT
# ==========================================

@router.callback_query(
    F.data.startswith("order_reject_")
)
async def order_reject(
        callback: CallbackQuery,
        state: FSMContext):

    order_id = int(
        callback.data.replace(
            "order_reject_", ""
        )
    )

    await state.update_data(
        reject_order_id=order_id
    )

    await callback.message.answer(
        "❌ কেন Order Reject করবেন?\n\nকারণ লিখুন:"
    )

    await state.set_state(
        RejectOrderReasonState.waiting_reason
    )

    await callback.answer()


@router.message(
    RejectOrderReasonState.waiting_reason
)
async def save_order_reject_reason(
        message: Message,
        state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    data = await state.get_data()

    order_id = data["reject_order_id"]

    order = get_order(order_id)

    if not order:
        await message.answer(
            "❌ Order পাওয়া যায়নি"
        )
        return

    user_id = order[1]
    price = order[3]

    # টাকা ফেরত
    update_balance(
        user_id,
        price
    )

    reason = message.text

    await message.bot.send_message(
        user_id,
        f"""
❌ আপনার Order Reject করা হয়েছে।

কারণ:
{reason}

💰 আপনার {price} Tk ফেরত দেওয়া হয়েছে।

/balance দিয়ে Balance চেক করুন।
"""
    )

    await message.answer(
        "✅ Order Reject করা হয়েছে এবং টাকা ফেরত দেওয়া হয়েছে।"
    )

    await state.clear()


# ==========================================
# DEPOSIT APPROVE
# ==========================================

@router.callback_query(
    F.data.startswith("dep_approve_")
)
async def deposit_approve(
        callback: CallbackQuery,
        state: FSMContext):

    deposit_id = int(
        callback.data.replace(
            "dep_approve_", ""
        )
    )

    await state.update_data(
        approve_deposit_id=deposit_id
    )

    await callback.message.answer(
        """
💰 কত টাকা Balance এ Add করবেন?

Example:
100
500
1000
"""
    )

    await state.set_state(
        DepositApproveState.waiting_amount
    )

    await callback.answer()


@router.message(
    DepositApproveState.waiting_amount
)
async def save_deposit_amount(
        message: Message,
        state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        amount = float(message.text)

    except:
        await message.answer(
            "❌ শুধু সংখ্যা লিখুন।"
        )
        return

    data = await state.get_data()

    deposit_id = data["approve_deposit_id"]

    deposit = get_deposit(deposit_id)

    if not deposit:
        await message.answer(
            "❌ Deposit পাওয়া যায়নি।"
        )
        return

    user_id = deposit[1]

    update_balance(
        user_id,
        amount
    )

    await message.bot.send_message(
        user_id,
        f"""
✅ আপনার Deposit Approved হয়েছে।

💰 {amount} Tk আপনার Balance এ যোগ করা হয়েছে।

/balance দিয়ে Balance চেক করুন।
"""
    )

    await message.answer(
        "✅ Deposit Approved Successfully"
    )

    await state.clear()


# ==========================================
# DEPOSIT REJECT
# ==========================================

@router.callback_query(
    F.data.startswith("dep_reject_")
)
async def deposit_reject(
        callback: CallbackQuery,
        state: FSMContext):

    deposit_id = int(
        callback.data.replace(
            "dep_reject_", ""
        )
    )

    await state.update_data(
        reject_deposit_id=deposit_id
    )

    await callback.message.answer(
        "❌ কেন Deposit Reject করবেন?\n\nকারণ লিখুন:"
    )

    await state.set_state(
        RejectDepositReasonState.waiting_reason
    )

    await callback.answer()


@router.message(
    RejectDepositReasonState.waiting_reason
)
async def save_deposit_reject_reason(
        message: Message,
        state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    data = await state.get_data()

    deposit_id = data["reject_deposit_id"]

    deposit = get_deposit(deposit_id)

    if not deposit:
        await message.answer(
            "❌ Deposit পাওয়া যায়নি"
        )
        return

    user_id = deposit[1]

    await message.bot.send_message(
        user_id,
        f"""
❌ আপনার Deposit Request Reject করা হয়েছে।

কারণ:
{message.text}

দয়া করে সঠিক তথ্য দিয়ে পুনরায় চেষ্টা করুন।
"""
    )

    await message.answer(
        "✅ Deposit Reject Successfully"
    )

    await state.clear() 
# ==========================================
# PRICE COMMAND
# ==========================================

@router.message(Command("price"))
async def price_panel(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "⚙️ Admin Price Panel",
        reply_markup=price_admin_kb
    )

    await message.answer(
        "💰 কোন অফারের দাম পরিবর্তন করবেন?",
        reply_markup=price_change_kb
    )


# ==========================================
# PRICE CHANGE CALLBACK
# ==========================================

@router.callback_query(
    F.data.startswith("price_")
)
async def price_change_callback(
        callback: CallbackQuery,
        state: FSMContext):

    offer = callback.data.replace(
        "price_", ""
    )

    current_price = get_price(offer)

    await state.update_data(
        offer=offer
    )

    await callback.message.answer(
        f"""
🎁 Offer: {offer}

💰 Current Price: {current_price} Tk

নতুন Price পাঠান:
"""
    )

    await state.set_state(
        PriceState.waiting_new_price
    )

    await callback.answer()


# ==========================================
# SAVE NEW PRICE
# ==========================================

@router.message(
    PriceState.waiting_new_price
)
async def save_new_price(
        message: Message,
        state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        new_price = float(message.text)

    except:
        await message.answer(
            "❌ শুধু সংখ্যা লিখুন।"
        )
        return

    data = await state.get_data()

    offer = data["offer"]

    set_price(
        offer,
        new_price
    )

    await message.answer(
        f"""
✅ Price Updated Successfully

🎁 Offer: {offer}
💰 New Price: {new_price} Tk
"""
    )

    await state.clear()


# ==========================================
# CHANGE PAYMENT NUMBER
# ==========================================

@router.callback_query(
    F.data.in_([
        "change_bkash",
        "change_nagad",
        "change_binance"
    ])
)
async def change_payment_number(
        callback: CallbackQuery,
        state: FSMContext):

    payment_type = callback.data.replace(
        "change_", ""
    )

    await state.update_data(
        payment_type=payment_type
    )

    await callback.message.answer(
        f"📱 নতুন {payment_type.upper()} Number/ID পাঠান:"
    )

    await state.set_state(
        PaymentState.waiting_new_payment
    )

    await callback.answer()


# ==========================================
# SAVE NEW PAYMENT NUMBER
# ==========================================

@router.message(
    PaymentState.waiting_new_payment
)
async def save_payment_number(
        message: Message,
        state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    data = await state.get_data()

    payment_type = data["payment_type"]

    set_setting(
        payment_type,
        message.text
    )

    await message.answer(
        f"✅ {payment_type.upper()} আপডেট করা হয়েছে।"
    )

    await state.clear()


# ==========================================
# BROADCAST
# ==========================================

@router.message(Command("boardchat"))
async def broadcast_message(
        message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace(
        "/boardchat ", ""
    )

    users = get_all_users()

    success = 0

    for user_id in users:

        try:
            await message.bot.send_message(
                user_id,
                text
            )

            success += 1

        except:
            pass

    await message.answer(
        f"✅ Message Sent To {success} Users"
    )# ==========================================
# ADMIN NOTIFICATION FUNCTIONS
# ==========================================

async def send_order_complete_notification(
        bot,
        user_id,
        offer):

    await bot.send_message(
        user_id,
        f"""
🎉 আপনার অর্ডার সম্পন্ন করা হয়েছে।

🎁 Offer: {offer}

✅ Diamond Successfully Delivered

🎮 দয়া করে গেমে প্রবেশ করে চেক করুন।
"""
    )


async def send_order_reject_notification(
        bot,
        user_id,
        offer,
        amount,
        reason):

    await bot.send_message(
        user_id,
        f"""
❌ আপনার Order Reject করা হয়েছে।

🎁 Offer: {offer}

📝 কারণ:
{reason}

💰 {amount} Tk আপনার Balance এ ফেরত দেওয়া হয়েছে।

/balance কমান্ড দিয়ে Balance চেক করুন।
"""
    )


async def send_deposit_approve_notification(
        bot,
        user_id,
        amount):

    await bot.send_message(
        user_id,
        f"""
✅ আপনার Deposit Approved হয়েছে।

💰 {amount} Tk Balance এ যোগ করা হয়েছে।

/balance কমান্ড দিয়ে Balance চেক করুন।
"""
    )


async def send_deposit_reject_notification(
        bot,
        user_id,
        reason):

    await bot.send_message(
        user_id,
        f"""
❌ আপনার Deposit Request Reject করা হয়েছে।

📝 কারণ:
{reason}

দয়া করে পুনরায় সঠিক তথ্য দিয়ে চেষ্টা করুন।
"""
    )


# ==========================================
# ADMIN ONLY CHECK
# ==========================================

def is_admin(user_id):

    if user_id == ADMIN_ID:
        return True

    return False


# ==========================================
# ADMIN HELP COMMAND
# ==========================================

@router.message(Command("admin"))
async def admin_help(message: Message):

    if not is_admin(message.from_user.id):
        return

    await message.answer(
        """
👑 Admin Commands

/price - Offer Price Change

/boardchat message
- সকল User কে Message পাঠাতে

/balance - নিজের Balance দেখতে

/bonus - Bonus নিতে

/start - Main Menu
"""
            )
# ==========================================
# CANCEL COMMAND
# ==========================================

@router.message(Command("cancel"))
async def cancel_process(
        message: Message,
        state: FSMContext):

    await state.clear()

    await message.answer(
        """
❌ বর্তমান Process Cancel করা হয়েছে।

আবার শুরু করতে /start ব্যবহার করুন।
""",
        reply_markup=start_kb
    )

# ==========================================
# REFER SYSTEM
# ==========================================

@router.message(F.text == "👥 Refer")
async def refer_cmd(message: Message):

    bot_info = await message.bot.get_me()

    link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"

    await message.answer(
        f"""
👥 Refer & Earn

🔗 আপনার Referral Link:

{link}

🎁 প্রতি Refer এ {REFERRAL_BONUS} Tk পাবেন।
"""
    )
# ==========================================
# HELP COMMAND
# ==========================================

@router.message(Command("help"))
async def help_command(
        message: Message):

    await message.answer(
        """
📖 Bot Commands

/start - Bot Start

/balance - Balance Check

/bonus - Daily Bonus

/cancel - Current Process Cancel

/help - Help Menu
"""
    )


# ==========================================
# BACK TO OFFER MENU
# ==========================================

@router.callback_query(F.data == "back_offer_menu")
async def back_offer_menu(callback: CallbackQuery):

    await callback.message.edit_text(
        "🛒 নিচের Offer থেকে একটি নির্বাচন করুন:",
        reply_markup=offer_kb
    )

    await callback.answer()


# ==========================================
# MAIN MENU CALLBACK
# ==========================================

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):

    await callback.message.delete()

    await callback.message.answer(
        """
👋 Welcome

🔥 Welcome To Topup Bot

নিচের অপশন থেকে একটি সিলেক্ট করুন।
""",
        reply_markup=start_kb
    )

    await callback.answer()

# ==========================================
# SET MONEY COMMAND
# ==========================================

@router.message(Command("setmoney"))
async def set_money_cmd(
        message: Message,
        state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "🆔 User ID পাঠান:"
    )

    await state.set_state(
        SetMoneyState.waiting_user_id
    )


@router.message(
    SetMoneyState.waiting_user_id
)
async def get_user_id(
        message: Message,
        state: FSMContext):

    await state.update_data(
        target_user_id=int(message.text)
    )

    await message.answer(
        "💰 কত টাকা Add করবেন?"
    )

    await state.set_state(
        SetMoneyState.waiting_amount
    )


@router.message(
    SetMoneyState.waiting_amount
)
async def add_money_to_user(
        message: Message,
        state: FSMContext):

    data = await state.get_data()

    user_id = data["target_user_id"]
    amount = float(message.text)

    update_balance(
        user_id,
        amount
    )

    await message.answer(
        f"✅ {amount} Tk যোগ করা হয়েছে।"
    )

    try:
        await message.bot.send_message(
            user_id,
            f"🎉 Admin আপনার Balance এ {amount} Tk যোগ করেছেন।"
        )
    except:
        pass

    await state.clear()
# ==========================================
# UNKNOWN TEXT HANDLER
# ==========================================

@router.message()
async def unknown_message(
        message: Message):

    await message.answer(
        """
❌ এই অপশনটি সঠিক নয়।

দয়া করে /start চাপুন অথবা মেনু থেকে একটি অপশন নির্বাচন করুন।
""",
        reply_markup=start_kb
            )
