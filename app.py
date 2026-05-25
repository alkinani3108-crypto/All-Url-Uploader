from __future__ import annotations

import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Settings
from utils.logging_config import setup_logging
from routers.callbacks import router as callbacks_router
from routers.commands import router as commands_router
from routers.intake import router as intake_router
from routers.thumbnails import router as thumbnails_router
from services.cooldown import CooldownManager
from services.request_store import RequestStore
from services.thumbnail_store import ThumbnailStore


async def health(request):
    return web.Response(text="OK")


async def start_web():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


def create_dispatcher(settings: Settings) -> Dispatcher:
    dispatcher = Dispatcher()
    # include your routers exactly as before
    dispatcher.include_router(callbacks_router)
    dispatcher.include_router(commands_router)
    dispatcher.include_router(intake_router)
    dispatcher.include_router(thumbnails_router)
    return dispatcher


async def run():
    setup_logging()
    settings = Settings()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = create_dispatcher(settings)

    # Start fake HTTP server so Render detects an open port
    await start_web()

    # Start bot polling normally
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
