import asyncio
import logging
import sys
import threading
import os
import uvicorn

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import config
from handlers import menu, calculator

# --- НАСТРОЙКА WEB SERVER (FastAPI) ---
app = FastAPI()

# Важно: путь должен совпадать с тем, что указан в volumes в docker-compose.yml
# Там написано: - ./images:/opt/GREENHILL/images
IMAGES_DIR = "/opt/GREENHILL/images"

# Проверяем, существует ли папка, чтобы бот не падал при старте
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR, exist_ok=True)

# Подключаем раздачу статики
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

async def main():
    # Инициализация бота
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    # Фильтр на личные сообщения
    dp.message.filter(F.chat.type == "private")
    
    # Подключение роутеров
    dp.include_router(menu.router)
    dp.include_router(calculator.router)
    
    # Удаляем старые апдейты и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    await dp.start_polling(bot)

def run_fastapi():
    """Запуск FastAPI в отдельном потоке"""
    # Запускаем на порту 8001, как указано в Caddyfile
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

if __name__ == "__main__":
    try:
        # Запускаем веб-сервер для картинок в фоновом потоке
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Запускаем бота в основном потоке
        asyncio.run(main())
    except KeyboardInterrupt:
        pass