import asyncpg
from decouple import config 
from typing import Optional, AsyncGenerator
from aiogram import Dispatcher
async def create_pool() -> Optional[asyncpg.pool.Pool]:
    """
    Создает и возвращает пул подключений к PostgreSQL.
    
    Returns:
        asyncpg.pool.Pool: Пул подключений к базе данных.
        None: Если подключение не удалось.
        
    Raises:
        asyncpg.PostgresError: В случае ошибки подключения к БД.
    """
    try:
        pool = await asyncpg.create_pool(
           user=config('USER', default='bot_user'),  # Добавлены fallback значения
            password=config('PASSWORD', default='bot_password_123'),
            database=config('DATABASE', default='weather_bot'),
            host=config('HOST', default='db'),  # Для Docker используем 'db'
            port=config('PORT', default=5432, cast=int),
            ssl=False,  # Для локальной БД не требуется
            min_size=1,  # Минимальное количество подключений
            max_size=5,  # Максимальное количество подключений
            command_timeout=30,  # Таймаут запросов
            max_inactive_connection_lifetime=300
        )
        return pool
    except (asyncpg.PostgresError, Exception) as e:
        print(f"Ошибка при создании пула подключений: {e}")
        return None


async def create_table() -> None:
    """
    Создает таблицу 'users' в базе данных, если она не существует.
    
    Raises:
        asyncpg.PostgresError: В случае ошибки выполнения SQL-запроса.
    """
    try:
        pool = await create_pool()
        if pool is None:
            raise ConnectionError("Не удалось установить соединение с БД")
            
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    lat FLOAT,
                    lon FLOAT,
                    req_time TIMESTAMP DEFAULT NOW(),
                    cityname TEXT
                )
            ''')
    except (asyncpg.PostgresError, ConnectionError, Exception) as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        if 'pool' in locals() and pool is not None:
            await pool.close()


async def on_startup(dp: Dispatcher) -> None:
    """
    Функция инициализации при запуске бота.
    Создает необходимые таблицы в БД и выводит сообщение о готовности.
    
    Args:
        dp: Объект диспетчера aiogram.
    """
    try:
        await create_table()
        print("Бот запущен и БД готова!")
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")