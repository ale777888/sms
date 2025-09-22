"""Telegram 机器人入口。"""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from shared import settings
from .handlers import register_handlers
from .services.state import BotState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


async def main() -> None:
    bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    state = BotState()
    dp.workflow_data.update({"bot_state": state})
    register_handlers(dp)

    async def _on_startup() -> None:
        logging.info("Bot startup complete")

    async def _on_shutdown() -> None:
        logging.info("Bot shutdown: releasing pending orders")
        with suppress(Exception):
            await state.shutdown()
        await bot.session.close()

    dp.startup.register(_on_startup)
    dp.shutdown.register(_on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
