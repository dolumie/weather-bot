import httpx
from decouple import config
from typing import Dict, Any
import logging

async def get_wether(coord: Dict[str, float]) -> Dict[str, Any]:
    """
    Получает данные о погоде с OpenWeatherMap API по заданным координатам.

    Args:
        coord: Словарь с координатами, должен содержать ключи 'lat' и 'lon'

    Returns:
        Словарь с данными о погоде в формате JSON

    Raises:
        httpx.HTTPStatusError: Если API возвращает код состояния HTTP >= 400
        httpx.RequestError: Если возникла ошибка при выполнении запроса
        ValueError: Если координаты неверны или отсутствует API ключ
        Exception: Для всех других неожиданных ошибок

    Examples:
        >>> await get_wether({"lat": 55.7558, "lon": 37.6176})
        {'weather': [...], 'main': {...}, ...}
    """
    try:
        TOKEN = config('WEATHER_API_KEY')
        if not TOKEN:
            raise ValueError("API ключ для погоды не найден в конфигурации")

        if 'lat' not in coord or 'lon' not in coord:
            raise ValueError("Координаты должны содержать 'lat' и 'lon'")

        params = {
            **coord,
            "appid": TOKEN,
            "units": "metric",
            "lang": "ru"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params=params
            )
            response.raise_for_status()  # Вызывает исключение для 4XX/5XX ответов
            return response.json()

    except httpx.HTTPStatusError as e:
        logging.error(f"Ошибка API погоды: {e.response.status_code} {e.response.text}")
        raise
    except httpx.RequestError as e:
        logging.error(f"Ошибка соединения с API погоды: {str(e)}")
        raise
    except ValueError as e:
        logging.error(f"Ошибка в параметрах запроса: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Неожиданная ошибка при получении погоды: {str(e)}")
        raise
       