import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.exceptions import TelegramNetworkError
from config import PROXY_URL, BOT_TOKEN
from database import create_table
from handlers import router

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Создаем сервер API для обхода блокировки
api_server = TelegramAPIServer.from_base(PROXY_URL)
session = AiohttpSession(api=api_server)
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

# Подключаем роутер с хендлерами
dp.include_router(router)


# Запуск процесса поллинга новых апдейтов
async def main():
    # Запускаем создание таблицы базы данных
    await create_table()

    # Запускаем поллинг с автоматическим перезапуском при ошибках сети
    while True:
        try:
            await dp.start_polling(bot)
        except (TelegramNetworkError, asyncio.CancelledError) as e:
            logging.warning(f"Ошибка соединения: {e}. Перезапуск через 3 секунды...")
            await asyncio.sleep(3)
            continue
        break


if __name__ == "__main__":
    asyncio.run(main())