"""主菜单键盘。"""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📲 取号"), KeyboardButton(text="📩 收码")],
        [KeyboardButton(text="🧾 订单"), KeyboardButton(text="💳 余额")],
        [KeyboardButton(text="🧩 项目"), KeyboardButton(text="🌍 国家")],
        [KeyboardButton(text="🛒 充值"), KeyboardButton(text="🆘 帮助")],
    ],
    resize_keyboard=True,
    input_field_placeholder="请选择操作",
)

__all__ = ["MAIN_MENU"]
