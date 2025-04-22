from aiogram import Bot, Dispatcher
from decouple import config
from bot.handlers import router,bot_commands
import asyncio
from database import models
async def on_startup(dp):
    await models.create_tables()
    print("Бот запущен и БД готова!")

async def main():
    bot = Bot(token=config('TELEGRAM_BOT_TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)
    await bot_commands(bot)
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())