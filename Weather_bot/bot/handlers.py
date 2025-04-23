from aiogram import Router, F
from aiogram.types import Message
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand
)
import math
from services.weather_api import get_wether
from aiogram import Bot
from database.crud import save_user_location

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
    print(answer)
    await message.answer(f"Температура: {math.ceil(answer['main']['temp'])}°C")
    
    
    
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