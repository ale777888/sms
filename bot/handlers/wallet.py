"""余额与充值回调。"""
from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery

router = Router(name="wallet")


@router.callback_query(Text(startswith="wallet:"))
async def wallet_placeholder(query: CallbackQuery) -> None:
    await query.answer("钱包操作将在下一阶段提供。", show_alert=True)
