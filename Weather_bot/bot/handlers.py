from aiogram import Router, F
from aiogram.types import Message
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand,
    BufferedInputFile,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from services.weather_api import get_wether
from aiogram import Bot
from database.crud import save_user_location,get_user_locations,get_record
import json
from bot.utils import generate_card

router = Router()

# @router.message(F.text)
# async def handle_text(message:Message):
#     await message.answer(message.text)

@router.message(Command("weather"))
@router.message(F.text == "Узнать погоду")
async def weather(message: types.Message):
    choose_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новая локация")],
            [KeyboardButton(text="История")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        '''Если вы уже пользовались ботом, то можете выбрать из истории.
        \nЕсли не пользовались, то выберите "Новая локация"''',
        reply_markup=choose_keyboard
    )
    
    
@router.message(F.text == "Новая локация")
async def handle_new_location(message: types.Message):
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


@router.message(F.text == "История")
async def handle_history(message: types.Message):
    records = await get_user_locations(message.from_user.id)
    
    if not records:
        await message.answer("У вас пока нет истории локаций.")
        return
    
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    # Добавляем кнопки построчно
    buttons = []
    
    for record in records:
        city_name = record.get('cityname') or "Неизвестный город"
        buttons.append(
            InlineKeyboardButton(
                text=city_name,
                callback_data=f"loc_info {record['id']}"
            )
        )
    
    # Добавляем все кнопки в клавиатуру
    keyboard.inline_keyboard.append(buttons)
    
    # Добавляем кнопку "Закрыть" на новой строке
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Закрыть", callback_data="close")])
    
    await message.answer("Выберите локацию", reply_markup=keyboard)

            
            

@router.callback_query(lambda c: c.data.startswith('loc_info '))      
async def handle_product(callback: types.CallbackQuery):
    product_id = callback.data.split(" ")[1]
    records = await get_record(int(product_id))
    record=records[0]
    lat=record["lat"]
    lon=record["lon"]
    user_id=record["user_id"]
    responsed = await response(lat=lat,lon=lon,user_id=user_id)
    await callback.message.answer_photo(responsed[0],caption=responsed[1])
   
@router.message(F.location)
async def handle_location(message: Message):
    lat = message.location.latitude
    lon = message.location.longitude
    us_id=message.from_user.id
    
    responsed = await response(lat=lat,lon=lon,user_id=us_id)
    
    await message.answer_photo(responsed[0],caption=responsed[1])
   
   
   
   
async def response(lat,lon,user_id):
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
    await save_user_location(user_id=user_id,latitude=lat,longitude=lon,CityName=answer["name"])
    city = answer["name"]
    temperature = answer["main"]["temp"]
    feels_like=answer["main"]["feels_like"]
    humidity=answer["main"]["humidity"]
    wind=answer["wind"]["speed"]
    caption = ( f"Погода в {city}\n🌡 Температура: {temperature}°C\n🤔 Ощущается как: {feels_like}°C\n💧 Влажность: {humidity}% \n💨 Ветер: {wind} м/с\n" )
    
    # await message.answer_photo(photo,caption=caption)
    # await message.answer_photo(photo='bot/temp/output.png')
    return (photo,caption)
    
    
    
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