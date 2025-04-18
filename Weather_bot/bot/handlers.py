from aiogram import Router, F
from aiogram.types import Message
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from services.weather_api import get_wether


router = Router()

# @router.message(F.text)
# async def handle_text(message:Message):
#     await message.answer(message.text)
    
@router.message(Command('weather'))
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
    answer = await get_wether({"lat":lat,"lon":lon})
    #обработка
    print(answer)
    await message.answer(f"Температура: {answer['main']['temp']}°C")
    
    