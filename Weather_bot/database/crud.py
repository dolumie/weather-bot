from database import models

async def save_user_location(user_id: int, latitude: float, longitude: float,CityName:str):
    pool = await models.create_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
        INSERT INTO users (user_id, lat, lon, cityname)
        VALUES ($1, $2, $3,$4)
    ''', user_id, latitude, longitude,CityName)
        
        
async def get_user_locations(user_id:int):
    pool = await models.create_pool()
    async with pool.acquire() as con:
        records = await con.fetch('''
        SELECT DISTINCT ON(users.cityname) * FROM users WHERE user_id = $1
    ''', user_id)
    return records

async def get_record(id_record):
    pool = await models.create_pool()
    async with pool.acquire() as con:
        record = await con.fetch('''
        SELECT * FROM users WHERE id = $1
    ''', id_record)
    return record