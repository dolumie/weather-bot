from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime

with open('weather.json', 'r', encoding='utf-8') as file:
    weather_data = json.load(file)

city = weather_data['name']
weather_condition = weather_data['weather'][0]['main']
description = weather_data['weather'][0]['description']
temp = weather_data['main']['temp']
humidity = weather_data['main']['humidity']
wind_speed = weather_data['wind']['speed']
sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
current_time = datetime.now()

is_daytime = sunrise <= current_time <= sunset

frames = []
duration = 200

if is_daytime:
    background_path = 'assets/background/sky_day.png'
    animation_frames = [f'icons/sun/sun_{i}.png' for i in range(3)]
    element_size = (120, 120)
    element_pos = (50, 50)
    text_color = "black"
else:
    background_path = 'assets/background/sky_night.png'
    animation_frames = [f'icons/stars/star_{i}.png' for i in range(7)]
    element_size = (150, 150)
    element_pos = (100, 30)
    text_color = "white"

for frame_path in animation_frames:
    frame = Image.open(background_path)

    element = Image.open(frame_path).resize(element_size)
    frame.paste(element, element_pos, element)

    draw = ImageDraw.Draw(frame)
    pixel_font = ImageFont.truetype('assets/font/PixelizerBold.ttf', size=24)

    draw.text((200, 50), f"Город: {city}", font=pixel_font, fill=text_color)
    draw.text((200, 80), f"Погода: {description}", font=pixel_font, fill=text_color)
    draw.text((200, 110), f"Температура: {temp}°C", font=pixel_font, fill=text_color)
    draw.text((200, 140), f"Влажность: {humidity}%", font=pixel_font, fill=text_color)
    draw.text((200, 170), f"Ветер: {wind_speed} м/с", font=pixel_font, fill=text_color)

    time_indicator = "День" if is_daytime else "Ночь"
    draw.text((200, 200), f"Время: {time_indicator}", font=pixel_font, fill=text_color)

    frames.append(frame)

output_filename = 'output/weather_day.gif' if is_daytime else 'output/weather_night.gif'
frames[0].save(
    output_filename,
    save_all=True,
    append_images=frames[1:],
    duration=duration,
    loop=0,
    optimize=True
)

print(f"Анимация сохранена как '{output_filename}'")

static_output = 'output/weather_static.png'
frames[0].save(static_output)
print(f"Статичное изображение сохранено как '{static_output}'")