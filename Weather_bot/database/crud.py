from database import models

async def save_user_location(user_id: int, latitude: float, longitude: float):
    pool = await models.create_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
        INSERT INTO users (user_id, lat, lon)
        VALUES ($1, $2, $3)
    ''', user_id, latitude, longitude)
    await conn.close()