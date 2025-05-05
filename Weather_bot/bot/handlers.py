from aiogram import Router, types, F, Bot
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand,
    BufferedInputFile,
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    WebAppInfo,
    Message
)
from services.weather_api import get_wether
from database.crud import save_user_location,get_user_locations,get_record
from bot.utils import generate_card
from typing import Tuple
import json

router = Router()

# Клавиатуры
choose_keyboard_new_his = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍Новая локация")],
        [KeyboardButton(text="🕒История")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

choose_keyboard_auto_man = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚙️Автоматически")],
        [KeyboardButton(text="✍️Вручную")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="☁️Узнать погоду")],
    ],
    resize_keyboard=True,
)


@router.message(Command("weather"))
@router.message(F.text == "☁️Узнать погоду")
async def weather(message: Message) -> None:
    """
    Обработчик команды /weather и кнопки "Узнать погоду".
    Предлагает пользователю выбрать между новой локацией и историей.
    """
    await message.answer(
        '✨ Если вы уже использовали бота, вы можете выбрать локацию из истории запросов.\n'
        '🌍 Если вы обращаетесь к нему впервые, выберите опцию «Новая локация».',
        reply_markup=choose_keyboard_new_his
    )


@router.message(F.text == "📍Новая локация")
async def handle_new_location(message: Message) -> None:
    """
    Обработчик выбора новой локации. Предлагает выбрать способ определения местоположения.
    """
    await message.answer(
        '📍Если вы хотите использовать геолокацию, выберите «Автоматически».\n'
        '🗺 Если предпочитаете указать местоположение вручную, нажмите «Вручную».',
        reply_markup=choose_keyboard_auto_man
    )


@router.message(F.text == "⚙️Автоматически")
async def handle_new_location_auto(message: Message) -> None:
    """
    Обработчик выбора автоматического определения местоположения.
    Предлагает отправить геолокацию.
    """
    location_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍Отправить местоположение", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "📲 Пожалуйста, нажмите кнопку ниже, чтобы отправить ваше местоположение:",
        reply_markup=location_keyboard
    )


@router.message(F.text == "✍️Вручную")
async def handle_new_location_manual(message: Message) -> None:
    """
    Обработчик выбора ручного ввода местоположения.
    Предлагает использовать веб-приложение с картой.
    """
    web_app_button = KeyboardButton(
        text="Выбрать точку на карте 🗺️",
        web_app=WebAppInfo(url="https://dolumie.github.io/weather-bot/") 
    )
    markup = ReplyKeyboardMarkup(
        keyboard=[[web_app_button]],  
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "Нажмите кнопку, чтобы выбрать точку:",
        reply_markup=markup
    )


@router.message(F.content_type == 'web_app_data')
async def handle_web_app_data(message: Message) -> None:
    """
    Обработчик данных из веб-приложения с картой.
    Получает координаты и показывает погоду для выбранной точки.
    """
    try:
        data = json.loads(message.web_app_data.data)
        lat = data['lat']
        lon = data['lon']
        us_id = message.from_user.id
        responsed = await get_weather_response(lat=lat, lon=lon, user_id=us_id)
        await message.answer_photo(responsed[0], caption=responsed[1])
    except (KeyError, json.JSONDecodeError) as e:
        await message.answer("Ошибка обработки данных с карты. Попробуйте еще раз.")
    except Exception as e:
        await message.answer("Произошла ошибка при получении погоды.")


@router.message(F.text == "🕒История")
async def handle_history(message: Message) -> None:
    """
    Обработчик просмотра истории локаций.
    Показывает список ранее запрошенных мест.
    """
    try:
        records = await get_user_locations(message.from_user.id)
        
        if not records:
            await message.answer("У вас пока нет истории локаций.")
            return
            
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for record in records:
            city_name = record.get('cityname', "Неизвестный город")
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"{city_name} 🏙",
                    callback_data=f"loc_info {record['id']}"
                )
            ])
        
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="◀️Назад", callback_data="back")
        ])
        
        await message.answer("Выберите локацию", reply_markup=keyboard)
    except Exception as e:
        await message.answer("Произошла ошибка при получении истории.")


@router.callback_query(lambda c: c.data.startswith('back'))     
async def handle_back(callback: types.CallbackQuery) -> None:
    """
    Обработчик кнопки "Назад" в истории локаций.
    Возвращает пользователя в главное меню.
    """
    await callback.message.edit_text(
        '✨ Если вы уже использовали бота, вы можете выбрать локацию из истории запросов.\n'
        '🌍 Если вы обращаетесь к нему впервые, выберите опцию «Новая локация».',
        reply_markup=None  
    )
    await callback.message.answer(
        "↩️Вы вернулись в меню выбора.",
        reply_markup=choose_keyboard_new_his
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith('loc_info '))      
async def handle_location(callback: types.CallbackQuery) -> None:
    """
    Обработчик выбора локации из истории.
    Показывает погоду для выбранной локации.
    """
    try:
        product_id = callback.data.split(" ")[1]
        record = await get_record(int(product_id))
        if not record:
            await callback.answer("Локация не найдена")
            return
    
        responsed = await get_weather_response(
            lat=record["lat"],
            lon=record["lon"],
            user_id=record["user_id"]
        )
        await callback.message.answer_photo(responsed[0], caption=responsed[1])
        await callback.answer()
    except Exception as e:
        await callback.answer("Произошла ошибка при получении данных.")


@router.message(F.location)
async def handle_location_message(message: Message) -> None:
    """
    Обработчик получения геолокации от пользователя.
    Показывает погоду для текущего местоположения.
    """
    try:
        lat = message.location.latitude
        lon = message.location.longitude
        us_id = message.from_user.id
        responsed = await get_weather_response(lat=lat, lon=lon, user_id=us_id)
        await message.answer_photo(responsed[0], caption=responsed[1])
    except Exception as e:
        await message.answer("Произошла ошибка при получении погоды для вашего местоположения.")


async def get_weather_response(lat: float, lon: float, user_id: int) -> Tuple[BufferedInputFile, str]:
    """
    Получает данные о погоде и создает графическую карточку.
    
    Args:
        lat: Широта
        lon: Долгота
        user_id: ID пользователя
        
    Returns:
        Кортеж из (фото карточки, подпись с данными о погоде)
        
    Raises:
        Exception: Если произошла ошибка при получении или обработке данных
    """
    try:
        answer = await get_wether({"lat": lat, "lon": lon})
        
        # Сохраняем данные о погоде в файл
        with open("bot/temp/weather.json", "w", encoding="utf-8") as file:
            json.dump(answer, file, ensure_ascii=False, indent=4)
        
        # Генерируем карточку
        generate_card(
            json_path='bot/temp/weather.json',
            output_path='bot/temp/output.png'
        )
        
        # Читаем сгенерированное изображение
        with open("bot/temp/output.png", "rb") as file:
            photo_data = file.read()
        
        photo = BufferedInputFile(photo_data, filename="output.png")
        
        # Сохраняем локацию пользователя
        await save_user_location(
            user_id=user_id,
            latitude=lat,
            longitude=lon,
            CityName=answer["name"]
        )
        
        # Формируем подпись
        city = answer["name"]
        temperature = answer["main"]["temp"]
        feels_like = answer["main"]["feels_like"]
        humidity = answer["main"]["humidity"]
        wind = answer["wind"]["speed"]
        
        caption = (
            f"🏙 {city}\n"
            f"🌡 Температура: {temperature}°C\n"
            f"🤔 Ощущается как: {feels_like}°C\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Ветер: {wind} м/с\n"
        )
        
        return (photo, caption)
        
    except Exception as e:
        raise Exception(f"Ошибка при формировании ответа: {str(e)}")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start.
    Показывает приветственное сообщение и основную клавиатуру.
    """
    await message.answer(
        "🌤 Привет! Я бот погоды. Выберите действие:",
        reply_markup=start_keyboard
    )


async def setup_bot_commands(bot: Bot) -> None:
    """
    Устанавливает команды бота для меню.
    
    Args:
        bot: Экземпляр бота
    """
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="weather", description="Узнать погоду"),
    ]
    await bot.set_my_commands(commands)