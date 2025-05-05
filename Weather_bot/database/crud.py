from typing import List, Optional, Dict, Any
import asyncpg
from database import models

async def save_user_location(
    user_id: int, 
    latitude: float, 
    longitude: float,
    CityName: str
) -> None:
    """
    Сохраняет местоположение пользователя в базу данных.
    
    Args:
        user_id: ID пользователя
        latitude: Широта
        longitude: Долгота
        CityName: Название города
        
    Raises:
        asyncpg.PostgresError: В случае ошибки при работе с БД
    """
    try:
        pool = await models.create_pool()
        if pool is None:
            raise ConnectionError("Не удалось подключиться к базе данных")
            
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, lat, lon, cityname)
                VALUES ($1, $2, $3, $4)
            ''', user_id, latitude, longitude, CityName)
            
    except (asyncpg.PostgresError, ConnectionError) as e:
        print(f"Ошибка при сохранении местоположения: {e}")
        raise
    finally:
        if 'pool' in locals() and pool is not None:
            await pool.close()


async def get_user_locations(user_id: int) -> List[asyncpg.Record]:
    """
    Получает последние 4 уникальных местоположения пользователя.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Список записей из базы данных
        
    Raises:
        asyncpg.PostgresError: В случае ошибки при работе с БД
    """
    try:
        pool = await models.create_pool()
        if pool is None:
            raise ConnectionError("Не удалось подключиться к базе данных")
            
        async with pool.acquire() as con:
            records = await con.fetch('''
            WITH last_requests AS (
            SELECT *, 
            ROW_NUMBER() OVER (PARTITION BY cityname ORDER BY req_time DESC) as rn
            FROM users
            WHERE user_id = $1 )
            SELECT * 
            FROM last_requests
            WHERE rn = 1
            ORDER BY req_time DESC
            LIMIT 4
            ''', user_id)
        return records
        
    except (asyncpg.PostgresError, ConnectionError) as e:
        print(f"Ошибка при получении местоположений: {e}")
        raise
    finally:
        if 'pool' in locals() and pool is not None:
            await pool.close()


async def get_record(id_record: int) -> Optional[asyncpg.Record]:
    """
    Получает запись из базы данных по ID.
    
    Args:
        id_record: ID записи в базе данных
        
    Returns:
        Запись из базы данных или None, если запись не найдена
        
    Raises:
        asyncpg.PostgresError: В случае ошибки при работе с БД
    """
    try:
        pool = await models.create_pool()
        if pool is None:
            raise ConnectionError("Не удалось подключиться к базе данных")
            
        async with pool.acquire() as con:
            record = await con.fetchrow('''
                SELECT * 
                FROM users 
                WHERE id = $1
            ''', id_record)
        return record
        
    except (asyncpg.PostgresError, ConnectionError) as e:
        print(f"Ошибка при получении записи: {e}")
        raise
    finally:
        if 'pool' in locals() and pool is not None:
            await pool.close()