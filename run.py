import logging
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

from app.handlers import router
from database.models import async_main

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands)

async def main():
    await async_main()
    load_dotenv()
    bot = Bot(os.getenv('TG_TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        print("EXIT")