"""Telegram 机器人入口。"""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from shared import settings
from shared.db import init_db
from shared.sms_client import get_sms_client
from .handlers import register_handlers
from .services.state import ActiveOrder, bot_state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


async def main() -> None:
    await init_db()
    bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    sms_client = get_sms_client(base_url=settings.base_url, token=settings.sms_token)
    dp.workflow_data.update({"bot_state": bot_state, "sms_client": sms_client})
    register_handlers(dp)

    async def _on_startup() -> None:
        logging.info("Bot startup complete")

    async def _on_shutdown() -> None:
        logging.info("Bot shutdown: releasing pending orders")
        pending: list[ActiveOrder] = []
        with suppress(Exception):
            pending = await bot_state.shutdown()
        for order in pending:
            with suppress(Exception):
                await sms_client.release(pkey=order.pkey)
        with suppress(Exception):
            await sms_client.close()
        await bot.session.close()

    dp.startup.register(_on_startup)
    dp.shutdown.register(_on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
