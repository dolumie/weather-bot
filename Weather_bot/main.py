import asyncio
from aiogram import Bot, Dispatcher
from decouple import config
from bot.handlers import router, setup_bot_commands
from database import models


async def main() -> None:
    """
    Основная функция для запуска Telegram бота.
    
    Инициализирует бота, диспетчер и запускает обработку входящих сообщений.
    Обрабатывает KeyboardInterrupt для корректного завершения работы.
    
    Raises:
        Exception: При возникновении ошибок в работе бота
    """
    try:
        # Инициализация бота
        bot: Bot = Bot(token=config('TELEGRAM_BOT_TOKEN'))
        dp: Dispatcher = Dispatcher()
        
        # Подключение роутера
        dp.include_router(router)
        
        # Инициализация базы данных
        await models.on_startup(dp)
        
        # Настройка команд бота
        await setup_bot_commands(bot)
        
        # Запуск бота
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        print("\nБот остановлен вручную")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if 'bot' in locals():
            await bot.session.close()


if __name__ == "__main__":
    """Точка входа для запуска бота."""
    asyncio.run(main())