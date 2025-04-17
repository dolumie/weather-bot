from aiogram import Router, F
from aiogram.types import Message
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


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
        #await message.answer("weather")
    