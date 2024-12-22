import asyncio
import logging
from http import HTTPStatus

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Response, request
from telegram import Update

from admin import app
from bot.bot import application, setup_handlers
from db.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_URL = "/telegram"


async def set_webhook():
    """Устанавливает вебхук."""
    if settings.SERVER_URL:
        logger.info("Устанавливаем вебхук...")
        await application.bot.set_webhook(
            url=f"{settings.SERVER_URL}/{TELEGRAM_URL}",
        )


@app.post(f"{TELEGRAM_URL}")
async def telegram() -> Response:
    """Управляет очередью входящих сообщений Telegram."""
    await application.update_queue.put(
        Update.de_json(data=request.json, bot=application.bot)
    )
    return Response(status=HTTPStatus.OK)


async def main():
    """Выполняет одновременный запуск Flask и Telegram."""
    await setup_handlers()
    await set_webhook()
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(app),
            port=int(settings.UVICORN_PORT),
            use_colors=False,
            host=settings.UVICORN_SERVER,
        )
    )
    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
