import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
# Импортируем наши модули из папки handlers
from handlers import menu, calculator

async def main():
    # Инициализация бота с HTML-разметкой
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # 🛡 ФИЛЬТР: Бот работает ТОЛЬКО в личке
    # (чтобы он не реагировал на команды в рабочем чате админов)
    dp.message.filter(F.chat.type == "private")
    
    # 🔌 ПОДКЛЮЧЕНИЕ ЛОГИКИ (РОУТЕРОВ)
    # Порядок важен: сначала админка, потом меню (кнопки), потом калькулятор
    dp.include_router(menu.router)
    dp.include_router(calculator.router)
    
    # Очистка очереди сообщений перед запуском (чтобы не отвечал на старое)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Логирование в консоль
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Старт
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass