# keyboards.py

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# =========================
# START MENU
# =========================

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ ব্যালেন্স যোগ করুন"),
            KeyboardButton(text="🎁 ডায়মন্ড")
        ],
        [
            KeyboardButton(text="👥 রেফার")
        ],
        [
            KeyboardButton(text="🎉 বোনাস"),
            KeyboardButton(text="💰 ব্যালেন্স")
        ]
    ],
    resize_keyboard=True
)
# =========================
# PAYMENT METHODS
# =========================

payment_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💳 BKash",
                callback_data="pay_bkash"
            ),
            InlineKeyboardButton(
                text="💳 Nagad",
                callback_data="pay_nagad"
            )
        ],
        [
            InlineKeyboardButton(
                text="🪙 Binance",
                callback_data="pay_binance"
            )
        ]
    ]
)

# =========================
# OFFER MENU
# =========================

offer_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📅 WEEKLY",
                callback_data="offer_Weekly"
            ),
            InlineKeyboardButton(
                text="🗓 MONTHLY",
                callback_data="offer_Monthly"
            )
        ],

        # ১ম লাইন
        [
            InlineKeyboardButton(
                text="25 Diamond",
                callback_data="offer_25 Diamond"
            ),
            InlineKeyboardButton(
                text="50 Diamond",
                callback_data="offer_50 Diamond"
            ),
            InlineKeyboardButton(
                text="115 Diamond",
                callback_data="offer_115 Diamond"
            )
        ],

        # ২য় লাইন
        [
            InlineKeyboardButton(
                text="240 Diamond",
                callback_data="offer_240 Diamond"
            ),
            InlineKeyboardButton(
                text="355 Diamond",
                callback_data="offer_355 Diamond"
            ),
            InlineKeyboardButton(
                text="480 Diamond",
                callback_data="offer_480 Diamond"
            )
        ],

        # ৩য় লাইন
        [
            InlineKeyboardButton(
                text="610 Diamond",
                callback_data="offer_610 Diamond"
            ),
            InlineKeyboardButton(
                text="850 Diamond",
                callback_data="offer_850 Diamond"
            ),
            InlineKeyboardButton(
                text="1240 Diamond",
                callback_data="offer_1240 Diamond"
            )
        ],

        # ৪র্থ লাইন
        [
            InlineKeyboardButton(
                text="2530 Diamond",
                callback_data="offer_2530 Diamond"
            ),
            InlineKeyboardButton(
                text="5060 Diamond",
                callback_data="offer_5060 Diamond"
            ),
            InlineKeyboardButton(
                text="10120 Diamond",
                callback_data="offer_10120 Diamond"
            )
        ]
    ]
)

# =========================
# BUY BUTTON
# =========================

def buy_offer_kb(offer_name):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Buy Offer",
                    callback_data=f"buy_{offer_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back",
                    callback_data="back_offer_menu"
                ),
                InlineKeyboardButton(
                    text="🏠 Menu",
                    callback_data="main_menu"
                )
            ]
        ]
    )

# =========================
# ADMIN DEPOSIT BUTTONS
# =========================

def deposit_admin_kb(deposit_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"dep_approve_{deposit_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"dep_reject_{deposit_id}"
                )
            ]
        ]
    )


# =========================
# ADMIN ORDER BUTTONS
# =========================

def order_admin_kb(order_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"order_approve_{order_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"order_reject_{order_id}"
                )
            ]
        ]
    )


# =========================
# ADMIN PRICE MENU
# =========================

price_admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📱 Change BKash",
                callback_data="change_bkash"
            )
        ],
        [
            InlineKeyboardButton(
                text="📱 Change Nagad",
                callback_data="change_nagad"
            )
        ],
        [
            InlineKeyboardButton(
                text="🪙 Change Binance",
                callback_data="change_binance"
            )
        ]
    ]
)


# =========================
# PRICE CHANGE BUTTONS
# =========================

price_change_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="25 Diamond",
                callback_data="price_25 Diamond"
            ),
            InlineKeyboardButton(
                text="50 Diamond",
                callback_data="price_50 Diamond"
            ),
            InlineKeyboardButton(
                text="115 Diamond",
                callback_data="price_115 Diamond"
            )
        ],

        [
            InlineKeyboardButton(
                text="240 Diamond",
                callback_data="price_240 Diamond"
            ),
            InlineKeyboardButton(
                text="355 Diamond",
                callback_data="price_355 Diamond"
            ),
            InlineKeyboardButton(
                text="480 Diamond",
                callback_data="price_480 Diamond"
            )
        ],

        [
            InlineKeyboardButton(
                text="610 Diamond",
                callback_data="price_610 Diamond"
            ),
            InlineKeyboardButton(
                text="850 Diamond",
                callback_data="price_850 Diamond"
            ),
            InlineKeyboardButton(
                text="1240 Diamond",
                callback_data="price_1240 Diamond"
            )
        ],

        [
            InlineKeyboardButton(
                text="2530 Diamond",
                callback_data="price_2530 Diamond"
            ),
            InlineKeyboardButton(
                text="5060 Diamond",
                callback_data="price_5060 Diamond"
            ),
            InlineKeyboardButton(
                text="10120 Diamond",
                callback_data="price_10120 Diamond"
            )
        ],

        [
            InlineKeyboardButton(
                text="📅 Weekly",
                callback_data="price_Weekly"
            ),
            InlineKeyboardButton(
                text="🗓 Monthly",
                callback_data="price_Monthly"
            )
        ]
    ]
)
