import asyncpg
from decouple import config 
async def create_pool():
    return await asyncpg.create_pool(
      user=config('USER'),
      password=config('PASSWORD'),
      database= config('DATABASE'),
      host= config('HOST'),
      port= config('PORT')
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
                req_time TIMESTAMP DEFAULT NOW()
            )
        ''')
        await conn.close()
        
async def on_startup(dp):
    await create_table()
    print("Бот запущен и БД готова!")