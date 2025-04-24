from aiogram import Router, F
from aiogram.types import Message
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand,
    BufferedInputFile
)
from services.weather_api import get_wether
from aiogram import Bot
from database.crud import save_user_location
import json
from bot.utils import generate_card

router = Router()

# @router.message(F.text)
# async def handle_text(message:Message):
#     await message.answer(message.text)
@router.message(Command("weather"))
@router.message(F.text == "Узнать погоду")
async def weather(message: types.Message):
        location_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить местоположение", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
        )
        await message.answer(
            "Пожалуйста, нажмите кнопку ниже, чтобы отправить ваше местоположение:",
            reply_markup=location_keyboard
        )
              
@router.message(F.location)
async def handle_location(message: Message):
    lat = message.location.latitude
    lon = message.location.longitude
    us_id=message.from_user.id
    await save_user_location(user_id=us_id,latitude=lat,longitude=lon)
    answer = await get_wether({"lat":lat,"lon":lon})
    #обработка
    data = answer
    with open("bot/temp/weather.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    generate_card(json_path='bot/temp/weather.json',
                  output_path='bot/temp/output.png')
    print(answer)
    with open("bot/temp/output.png", "rb") as file:
        photo_data = file.read()
    # Создаем BufferedInputFile
    photo = BufferedInputFile(photo_data, filename="output.png")
    # Отправляем фото
    
    city = answer["name"]
    temperature = answer["main"]["temp"]
    feels_like=answer["main"]["feels_like"]
    humidity=answer["main"]["humidity"]
    wind=answer["wind"]["speed"]
    
    caption = ( f"Погода в {city}\n🌡 Температура: {temperature}°C\n🤔 Ощущается как: {feels_like}°C\n💧 Влажность: {humidity}% \n💨 Ветер: {wind} м/с\n" )
    await message.answer_photo(photo,caption=caption)
    # await message.answer_photo(photo='bot/temp/output.png')
    
    
    
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Узнать погоду")],
        # [KeyboardButton(text="Отправить местоположение", request_location=True)]
    ],
    resize_keyboard=True,
)
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот погоды. Выберите действие:",
        reply_markup=start_keyboard
    )

async def bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="weather", description="Узнать погоду"),
    ]
    await bot.set_my_commands(commands)