import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import logging

# Конфигурационные константы
BACKGROUND_PATH = 'Graphic_data/assets/background.png'
ICONS_DIR = 'Graphic_data/assets/weather_icons'
FONT_PATH = 'Graphic_data/assets/font/PixelizerBold.ttf'

# Настройки внешнего вида
TEXT_COLOR = (96, 41, 131)
ICON_TARGET_SIZE = (200, 200)
TEXT_FONT_SIZE = 54
TEXT_POSITION_RATIO = 2.0

DEFAULT_ADVICE = {
    'day': "Хорошего дня!",
    'night': "Спокойной ночи!"
}

WEATHER_MAP = {
    # ... (существующий словарь WEATHER_MAP остается без изменений)
}

def generate_card(json_path: str, output_path: str) -> None:
    """
    Генерирует графическую карточку с информацией о погоде на основе JSON данных.
    
    Args:
        json_path: Путь к JSON файлу с данными о погоде
        output_path: Путь для сохранения сгенерированной карточки
        
    Raises:
        FileNotFoundError: Если отсутствуют необходимые файлы
        KeyError: Если в данных отсутствуют обязательные поля
        ValueError: Если возникает ошибка при обработке изображения
        Exception: Для других неожиданных ошибок
        
    Examples:
        >>> generate_card('weather.json', 'output.png')
    """
    try:
        # Проверка наличия файлов
        _validate_files(json_path)
        
        # Загрузка и проверка данных
        data = _load_weather_data(json_path)
        weather = data['weather'][0]
        main_condition = weather['main']
        description = weather['description'].lower()

        # Определение времени суток
        time_key = _determine_time_of_day(data)
        
        # Обработка частичной облачности
        main_condition = _handle_partly_cloudy(main_condition, description)
        
        # Получение совета и пути к иконке
        advice, icon_path = _get_weather_content(main_condition, time_key)
        
        # Создание и сохранение изображения
        _create_and_save_image(advice, icon_path, output_path)
        
    except Exception as e:
        logging.error(f"Ошибка при генерации карточки: {str(e)}")
        raise

def _validate_files(json_path: str) -> None:
    """Проверяет наличие всех необходимых файлов."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Файл с данными о погоде не найден: {json_path}")
    if not os.path.exists(BACKGROUND_PATH):
        raise FileNotFoundError(f"Фоновое изображение не найдено: {BACKGROUND_PATH}")
    if not os.path.exists(ICONS_DIR):
        raise FileNotFoundError(f"Папка с иконками не найдена: {ICONS_DIR}")

def _load_weather_data(json_path: str) -> Dict[str, Any]:
    """Загружает и проверяет данные о погоде из JSON файла."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'weather' not in data or not data['weather']:
        raise KeyError("Отсутствуют данные о погоде в JSON файле")
    if 'sys' not in data or 'sunrise' not in data['sys'] or 'sunset' not in data['sys']:
        raise KeyError("Отсутствуют данные о времени восхода/заката")
    
    return data

def _determine_time_of_day(data: Dict[str, Any]) -> str:
    """Определяет текущее время суток (день/ночь)."""
    sunrise = datetime.fromtimestamp(data['sys']['sunrise'])
    sunset = datetime.fromtimestamp(data['sys']['sunset'])
    current_time = datetime.now()
    return 'day' if sunrise <= current_time <= sunset else 'night'

def _handle_partly_cloudy(main_condition: str, description: str) -> str:
    """Обрабатывает особый случай частичной облачности."""
    partly_cloudy_keywords = ['небольшая', 'переменная', 'расссеянные', 'слегка', 'с прояснениями']
    if main_condition == 'Clouds' and any(keyword in description for keyword in partly_cloudy_keywords):
        return 'Partly Cloudy'
    return main_condition

def _get_weather_content(main_condition: str, time_key: str) -> tuple[str, Optional[str]]:
    """Возвращает совет и путь к иконке для заданных погодных условий."""
    advice = DEFAULT_ADVICE[time_key]
    icon_path = None
    
    if main_condition in WEATHER_MAP:
        condition_info = WEATHER_MAP[main_condition]
        
        # Получение совета
        advice_key = f"advice_{time_key}"
        advice = condition_info.get('advice', condition_info.get(advice_key, DEFAULT_ADVICE[time_key]))
        
        # Получение пути к иконке
        icon_file = condition_info.get('icon', condition_info.get(f"{time_key}_icon"))
        if icon_file:
            icon_path = os.path.join(ICONS_DIR, icon_file)
            if not os.path.exists(icon_path):
                icon_path = None
    
    return advice, icon_path

def _create_and_save_image(advice: str, icon_path: Optional[str], output_path: str) -> None:
    """Создает и сохраняет итоговое изображение."""
    try:
        background = Image.open(BACKGROUND_PATH).convert('RGBA')
        
        # Добавление иконки если она существует
        if icon_path and os.path.exists(icon_path):
            background = _add_icon_to_background(background, icon_path)
        
        # Добавление текста
        background = _add_text_to_background(background, advice)
        
        # Сохранение результата
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        background.save(output_path)
        logging.info(f"Карточка успешно сохранена: {output_path}")
        
    except Exception as e:
        raise ValueError(f"Ошибка при обработке изображения: {str(e)}")

def _add_icon_to_background(background: Image.Image, icon_path: str) -> Image.Image:
    """Добавляет иконку погоды на фоновое изображение."""
    icon = Image.open(icon_path).convert('RGBA')
    icon.thumbnail(ICON_TARGET_SIZE, Image.Resampling.LANCZOS)
    
    icon_layer = Image.new('RGBA', background.size, (0, 0, 0, 0))
    icon_position = (
        (background.width - icon.width) // 5,
        (background.height - icon.height) // 3
    )
    icon_layer.paste(icon, icon_position, icon)
    
    return Image.alpha_composite(background, icon_layer)

def _add_text_to_background(background: Image.Image, text: str) -> Image.Image:
    """Добавляет текст на фоновое изображение."""
    draw = ImageDraw.Draw(background)
    
    try:
        font = ImageFont.truetype(FONT_PATH, size=TEXT_FONT_SIZE)
    except IOError:
        logging.warning("Не удалось загрузить шрифт, используется стандартный")
        font = ImageFont.load_default()
    
    # Совместимость с разными версиями Pillow
    try:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)
    
    text_x = (background.width - text_width) // 2
    text_y = (background.height - text_height) // TEXT_POSITION_RATIO
    
    draw.text(
        (text_x, text_y),
        text,
        font=font,
        fill=TEXT_COLOR,
    )
    
    return background