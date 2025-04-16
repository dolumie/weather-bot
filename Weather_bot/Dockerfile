# Используем официальный образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /bot

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt --prefer-binary

# Копируем остальные файлы
COPY . .

# Запускаем бота
CMD ["python","main.py"]