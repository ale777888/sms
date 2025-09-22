"""/start 处理。"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from ..keyboards.main_menu import MAIN_MENU

router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "欢迎使用 <b>tg-sms-bot</b>，请选择需要的操作。",
        reply_markup=MAIN_MENU,
    )
