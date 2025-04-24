from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime

# Пути
BACKGROUND_PATH = 'Graphic_data/assets/background.png'
ICONS_DIR = 'Graphic_data/assets/weather_icons'
FONT_PATH = 'Graphic_data/assets/font/PixelizerBold.ttf'

# Внешний вид
TEXT_COLOR = (96,41,131)
ICON_TARGET_SIZE = (200, 200)
TEXT_FONT_SIZE = 54
TEXT_POSITION_RATIO = 2.0

# На случай, если нет данных в словаре погодных условий
DEFAULT_ADVICE = {
    'day': "Хорошего дня!",
    'night': "Спокойной ночи!"
}

# Словарь погодных условий
WEATHER_MAP = {
    "Clear": {
        "day_icon": "sunny.png",
        "night_icon": "clear_moon.png",
        "advice_night": "Загляните в небо." + "\n" + "Там красиво.",
        "advice_day": "Не забудьте" + "\n" + "солнечные очки!"
    },
    "Clouds": {
        "icon": "cloudy.png",
        "advice": "Возьмите с собой" + "\n" + "хорошее настроение."
    },
    "Partly Cloudy": {
        "day_icon": "partly_cloudy.png",
        "night_icon": "partly_cloudy_night.png",
        "advice_day": "На всякий случай" + "\n" + "захватите кофту.",
        "advice_night": "Уютной ночи" + "\n" + "и тёплых мыслей."
    },
    "Fog": {
        "icon": "fog.png",
        "advice": "Будьте внимательны" + "\n"+ "на дорогах."
    },
    "Rain": {
        "icon": "rain.png",
        "advice": "Не забудьте зонтик!"
    },
    "Snow": {
        "icon": "snow.png",
        "advice": "Одевайтесь тепло!"
    },
    "Thunderstorm": {
        "icon": "thunderstorm.png",
        "advice": "Оставайтесь дома," +"\n" +"берегите себя."
    },
    "Wind": {
        "icon": "windy.png",
        "advice": "Не переохладитесь."
    },
}

def generate_card(json_path: str, output_path: str) -> None:
# Проверка наличия файлов
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Файл с данными о погоде не найден: {json_path}")
    if not os.path.exists(BACKGROUND_PATH):
        raise FileNotFoundError(f"Фоновое изображение не найдено: {BACKGROUND_PATH}")
    if not os.path.exists(ICONS_DIR):
        raise FileNotFoundError(f"Папка с иконками не найдена: {ICONS_DIR}")
# Загрузка и проверка данных
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'weather' not in data or not data['weather']:
        raise KeyError("Отутствуют данные о погоде в JSON файле")

    weather = data['weather'][0]
    main_condition = weather['main']
    description = weather['description'].lower()

# Определение времени суток
    if 'sys' not in data or 'sunrise' not in data['sys'] or 'sunset' not in data['sys']:
        raise KeyError("Отсутствуют данные о времени восхода/заката")

    sunrise = datetime.fromtimestamp(data['sys']['sunrise'])
    sunset = datetime.fromtimestamp(data['sys']['sunset'])
    current_time = datetime.now()
    is_daytime = sunrise <= current_time <= sunset
    time_key = 'day' if is_daytime else 'night'

# Обработка частичной облачности. Это особый случай
    if main_condition == 'Clouds' and 'few' or 'scattered' in description:
        main_condition = 'Partly Cloudy'

# Выбор контента для карточки
    advice = DEFAULT_ADVICE[time_key]
    icon_path = None

    if main_condition in WEATHER_MAP:
        condition_info = WEATHER_MAP[main_condition]
        
# Выбор текста совета
        if 'advice' in condition_info:
            advice = condition_info['advice']
        else:
            advice_key = f"advice_{time_key}"
            advice = condition_info.get(advice_key, DEFAULT_ADVICE[time_key])
        
# Выбор иконки
        if 'icon' in condition_info:
            icon_file = condition_info['icon']
        else:
            icon_key = f"{time_key}_icon"
            icon_file = condition_info.get(icon_key)
        
        if icon_file:
            icon_path = os.path.join(ICONS_DIR, icon_file)
            if not os.path.exists(icon_path):
                icon_path = None

# Создание изображения
    try:
# Загрузка фона
        background = Image.open(BACKGROUND_PATH).convert('RGBA')
        
# Добавление иконки
        if icon_path and os.path.exists(icon_path):
            icon = Image.open(icon_path).convert('RGBA')
            
# Машстабирование
            icon.thumbnail(ICON_TARGET_SIZE, Image.Resampling.LANCZOS)
            
# Создание слоя для иконки
            icon_layer = Image.new('RGBA', background.size, (0, 0, 0, 0))
            icon_position = (
                (background.width - icon.width) // 5,
                (background.height - icon.height) // 3
            )
            icon_layer.paste(icon, icon_position, icon)
            
# Объединение с фоном
            background = Image.alpha_composite(background, icon_layer)

# Добавление текста
        draw = ImageDraw.Draw(background)
        
# Загрузка шрифта
        try:
            font = ImageFont.truetype(FONT_PATH, size=TEXT_FONT_SIZE)
        except IOError:
            print("Не удалось загрузить шрифт")
            font = ImageFont.load_default()

# Расчет размеров текста
        try:
            text_bbox = draw.textbbox((0, 0), advice, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(advice, font=font)

# Позиционирование текста
        text_x = (background.width - text_width) // 2
        text_y = (background.height - text_height) // TEXT_POSITION_RATIO

# Текст 
        draw.text(
            (text_x, text_y),
            advice,
            font=font,
            fill=TEXT_COLOR,
)

# Сохранение
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        background.save(output_path)
        print(f"Карточка успешно сохранена: {output_path}")

    except Exception as e:
        raise ValueError(f"Ошибка при обработке изображения: {e}")


# if __name__ == '__main__':
#     try:
#         generate_card(
#             json_path='weather.json',
#             output_path='output/weather_card.png'
#         )
#     except Exception as e:
#         print(f"Ошибка при создании карточки: {str(e)}")
#         exit(1)