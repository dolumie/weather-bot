import asyncpg
from decouple import config 
async def create_pool():
    return await asyncpg.create_pool(
      user=config('USER'),
      password=config('PASSWORD'),
      database= config('DATABASE'),
      host= config('HOST'),
      port= config('PORT'),
      max_inactive_connection_lifetime=300,  # закрывать неиспользуемые соединения через 5 мин
      timeout=30  # таймаут ожидания соединения
    )

async def create_table():
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY ,
                user_id BIGINT,
                lat FLOAT,
                lon FLOAT,
                req_time TIMESTAMP DEFAULT NOW(),
                cityname Text
            )
        ''')
        await conn.close()
        
async def on_startup(dp):
    await create_table()
    print("Бот запущен и БД готова!")