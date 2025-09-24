"""国家选择键盘。"""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_country_keyboard(
    countries: list[tuple[str, str]],
    *,
    page: int = 1,
    page_size: int = 6,
    project_id: int | None = None,
) -> InlineKeyboardMarkup:
    start = (page - 1) * page_size
    end = start + page_size
    slice_ = countries[start:end]
    buttons: list[list[InlineKeyboardButton]] = []
    for code, name in slice_:
        callback = f"order:new:{project_id}:{code}" if project_id is not None else f"country:{code}"
        buttons.append([InlineKeyboardButton(text=f"{name} ({code})", callback_data=callback)])
    nav_row = []
    if page > 1:
        prefix = f"country_page:{project_id}:" if project_id is not None else "country_page:"
        nav_row.append(InlineKeyboardButton(text="⬅️ 上一页", callback_data=f"{prefix}{page-1}"))
    if end < len(countries):
        prefix = f"country_page:{project_id}:" if project_id is not None else "country_page:"
        nav_row.append(InlineKeyboardButton(text="下一页 ➡️", callback_data=f"{prefix}{page+1}"))
    if nav_row:
        buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="🔍 搜索", switch_inline_query_current_chat="国家 ")])
    buttons.append([InlineKeyboardButton(text="⬅️ 返回", callback_data="menu:root")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


__all__ = ["build_country_keyboard"]
