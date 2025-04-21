from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime

BACKGROUND_PATH = 'assets/background.png'
ICONS_DIR = 'assets/weather_icons'
FONT_PATH = 'assets/font/PixelizerBold.ttf'

WEATHER_MAP = {
    "Clear": {
        "day_icon": "sunny.png",
        "night_icon": "clear_moon.png",
        "advice": "Загляните в небо. Там красиво.",
        "advice_day": "Не забудьте солнечные очки!"
    },
    "Clouds": {
        "icon": "cloudy.png",
        "advice": "Возьмите с собой хорошее настроение."
    },
    "Partly Cloudy": {
        "day_icon": "partly_cloudy.png",
        "night_icon": "partly_cloudy_night.png",
        "advice_day": "На всякий случай захватите кофту.",
        "advice_night": "Уютной ночи и тёплых мыслей."
    },
    "Fog": {
        "icon": "fog.png",
        "advice": "Будьте внимательны на дорогах."
    },
    "Rain": {
        "icon": "rain.png",
        "advice": "Не забудьте зонтик."
    },
    "Snow": {
        "icon": "snow.png",
        "advice": "Одевайтесь тепло."
    },
    "Thunderstorm": {
        "icon": "thunderstorm.png",
        "advice": "Оставайтесь дома, берегите себя."
    },
    "Wind": {
        "icon": "windy.png",
        "advice": "Не переохладитесь."
    },
}


def generate_card(json_path: str, output_path: str):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Файл с данными о погоде не найден: {json_path}")

    if not os.path.exists(BACKGROUND_PATH):
        raise FileNotFoundError(f"Фоновое изображение не найдено: {BACKGROUND_PATH}")

    if not os.path.exists(ICONS_DIR):
        raise FileNotFoundError(f"Директория с иконками не найдена: {ICONS_DIR}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'weather' not in data or not data['weather']:
        raise KeyError("Отсутствуют данные о погоде в JSON файле")

    w = data['weather'][0]
    main = w['main']
    desc = w['description'].lower()

    if main == 'Clouds' and 'partly' in desc:
        main = 'Partly Cloudy'

    if main not in WEATHER_MAP:
        raise KeyError(f"Нет данных для состояния: {main}")

    info = WEATHER_MAP[main]

    if 'sys' not in data or 'sunrise' not in data['sys'] or 'sunset' not in data['sys']:
        raise KeyError("Отсутствуют данные о времени восхода/заката")

    sunrise = datetime.fromtimestamp(data['sys']['sunrise'])
    sunset = datetime.fromtimestamp(data['sys']['sunset'])
    now = datetime.now()
    is_day = sunrise <= now <= sunset

    if 'icon' in info:
        icon_file = info['icon']
        advice = info['advice']
    else:
        time_key = 'day' if is_day else 'night'
        icon_key = f"{time_key}_icon"
        advice_key = f"advice_{time_key}"

        if icon_key not in info:
            raise KeyError(f"Отсутствует иконка для состояния {main} ({time_key})")
        if advice_key not in info:
            raise KeyError(f"Отсутствует совет для состояния {main} ({time_key})")

        icon_file = info[icon_key]
        advice = info[advice_key]

    icon_path = os.path.join(ICONS_DIR, icon_file)
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"Иконка погоды не найдена: {icon_path}")

    try:
        bg = Image.open(BACKGROUND_PATH).convert('RGBA')
        icon = Image.open(icon_path).convert('RGBA')
        icon = icon.resize((120, 120))
    except Exception as e:
        raise ValueError(f"Ошибка при загрузке изображений: {e}")

    icon_pos = (30, 30)
    bg.paste(icon, icon_pos, icon)

    draw = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype(FONT_PATH, size=28)
    except IOError:
        print("Предупреждение: шрифт не найден, используется стандартный")
        font = ImageFont.load_default()

    try:
        w_text, h_text = draw.textsize(advice, font=font)
    except AttributeError:
        left, top, right, bottom = draw.textbbox((0, 0), advice, font=font)
        w_text = right - left
        h_text = bottom - top

    x_text = (bg.width - w_text) // 2
    y_text = bg.height - h_text - 40

    draw.text((x_text, y_text), advice, font=font, fill='black')

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    bg.save(output_path)
    print(f"Карточка сохранена в: {output_path}")


if __name__ == '__main__':
    try:
        generate_card('weather.json', 'output/weather_card.png')
    except Exception as e:
        print(f"Ошибка при создании карточки: {e}")