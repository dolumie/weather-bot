# 🌦️ Weather Telegram Bot

Бот для получения текущей погоды с генерацией графических карточек и сохранением истории запросов.

## 📋 Содержание
- [Функционал](#-функционал)
- [Установка](#-установка)
- [Конфигурация](#-конфигурация)
- [Запуск](#-запуск)
- [Использование](#-использование)
- [Структура проекта](#-структура-проекта)
- [FAQ](#-faq)

## 🌟 Функционал
- Получение текущей погоды по локации
- Автоматическое определение местоположения
- Ручной выбор точки на карте
- История последних запросов
- Генерация графических карточек
- Хранение данных в PostgreSQL

## 🛠️ Установка

### Требования
- Python 3.11+
- Docker (для контейнеризованного запуска)
- API ключ OpenWeatherMap

### 1. Клонирование репозитория
git clone https://github.com/ваш-репозиторий/weather-bot.git
cd weather-bot
2. Настройка окружения
Создайте файл .env в корне проекта:

TELEGRAM_BOT_TOKEN=ваш_токен_бота
WEATHER_API_KEY=ваш_ключ_openweathermap
# Настройки БД (для Docker)
DB_HOST=db
DB_PORT=5432
DB_USER=bot_user
DB_PASSWORD=bot_password_123
DB_NAME=weather_bot


🚀 Запуск
Вариант 1: Docker (рекомендуется)
docker-compose up -d --build
Вариант 2: Локальный запуск
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
🖥️ Использование
Доступные команды бота:

/start - Главное меню

/weather - Запрос погоды

📍 Новая локация - Указать новое местоположение

🕒 История - Просмотр истории запросов

📂 Структура проекта
weather-bot/
├── bot/                    # Основной код бота
│   ├── handlers.py         # Обработчики сообщений
│   ├── utils.py            # Вспомогательные функции
├── database/               # Работа с базой данных
│   ├── models.py           # Модели SQLAlchemy
│   ├── crud.py             # Операции с БД
├── Graphic_data/           # Генерация графики
│   ├── assets/             # Ресурсы для карточек
│   ├── picture_generation.py # Генератор изображений
├── services/               # Внешние сервисы
│   ├── weather_api.py      # API OpenWeatherMap
├── docker-compose.yml      # Конфигурация Docker
├── Dockerfile              # Сборка образа бота
├── init.sql                # Инициализация БД
└── requirements.txt        # Зависимости Python
🔧 Настройка PostgreSQL
При первом запуске автоматически создается:

Пользователь: bot_user

База данных: weather_bot

Таблица users для хранения истории

Доступ к pgAdmin:

URL: http://localhost:5050

Логин: admin@example.com

Пароль: admin123

❓ FAQ
Q: Как добавить новые иконки погоды?
A: Поместите PNG-файлы в Graphic_data/assets/weather_icons/ и обновите словарь WEATHER_MAP в коде.

Q: Где хранятся временные файлы?
A: В папке bot/temp/ (очищается при перезапуске)

Q: Как изменить стиль карточек?
A: Редактируйте файлы в Graphic_data/assets/:

background.png - фон карточки

Шрифт в font/PixelizerBold.ttf

Цвета текста в picture_generation.py