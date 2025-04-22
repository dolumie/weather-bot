import asyncpg

async def create_pool():
    return await asyncpg.create_pool(
        user="your_user",
        password="your_password",
        database="your_db",
        host="localhost",
        port=5432
    )
    
async def create_tables():
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                user_id TEXT,
                lat FLOAT,
                lom FLOAT,
                req_time TIMESTAMP DEFAULT NOW()
            )
        ''')