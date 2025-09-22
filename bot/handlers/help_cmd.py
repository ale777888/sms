"""帮助命令。"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="help")


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "<b>使用指引(预览版)</b>\n"
        "1. 通过主菜单选择取号或收码。\n"
        "2. 充值与余额功能将在下一阶段开放。\n"
        "3. 遇到问题可联系管理员。"
    )
