import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import auth_handlers, game_handlers
from database import create_db_and_tables
from middleware.database import DatabaseMiddleware
from src.utils.logger import logger


async def launch():
    # Инициализация бота и диспетчера
    bot = Bot(token="7929207204:AAHWRYap92rrbKV9eB038_6p80FbGN2i8to")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Создание таблиц в базе данных
    await create_db_and_tables()

    # Регистрация middleware
    dp.update.middleware.register(DatabaseMiddleware())

    # Регистрация роутеров
    dp.include_router(auth_handlers.router)
    dp.include_router(game_handlers.router)

    # Запуск бота
    logger.info("Бот запущен")
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(launch())