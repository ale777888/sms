"""项目选择键盘。"""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_project_keyboard(entries: list[tuple[int, str, float]], *, page: int = 1, currency: str = "CNY", page_size: int = 6) -> InlineKeyboardMarkup:
    start = (page - 1) * page_size
    end = start + page_size
    slice_ = entries[start:end]
    buttons: list[list[InlineKeyboardButton]] = []
    for project_id, name, price in slice_:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{name} · {price:g}{currency}",
                    callback_data=f"project:{project_id}",
                )
            ]
        )
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ 上一页", callback_data=f"project_page:{page-1}"))
    if end < len(entries):
        nav_row.append(InlineKeyboardButton(text="下一页 ➡️", callback_data=f"project_page:{page+1}"))
    if nav_row:
        buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="⭐ 收藏", callback_data="project:fav")])
    buttons.append([InlineKeyboardButton(text="⬅️ 返回", callback_data="menu:root")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


__all__ = ["build_project_keyboard"]
