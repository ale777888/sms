"""订单操作键盘。"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_order_actions(order_id: int, status: str) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    if status in {"created", "polling"}:
        buttons.append([InlineKeyboardButton(text="📩 开始收码", callback_data=f"order:poll:{order_id}")])
        buttons.append([InlineKeyboardButton(text="♻️ 释放", callback_data=f"order:release:{order_id}")])
    if status == "received":
        buttons.append([InlineKeyboardButton(text="📄 复制短信", callback_data=f"order:copy:{order_id}")])
        buttons.append([InlineKeyboardButton(text="♻️ 释放", callback_data=f"order:release:{order_id}")])
    if status not in {"blacklisted", "released"}:
        buttons.append([InlineKeyboardButton(text="🚫 加黑", callback_data=f"order:black:{order_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ 返回", callback_data="menu:orders")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


__all__ = ["build_order_actions"]
