"""帮助命令。"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="help")


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "<b>使用指引</b>\n"
        "1. 点击“📲 取号”选择项目与国家完成取号。\n"
        "2. 在订单消息中使用“📩 开始收码”获取验证码；如长时间未返回，可重试或释放。\n"
        "3. “💳 余额”可查询短信平台余额，充值请联系管理员。\n"
        "4. 如需人工协助，请备注订单编号联系运维。"
    )
