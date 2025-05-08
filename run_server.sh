#!/bin/bash

# Создание директории для логов, если ее нет
mkdir -p logs

# Проверка Redis сервера (для macOS/Linux)
which redis-server > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Redis-сервер не найден. Установите Redis."
    exit 1
fi

# Проверка, запущен ли Redis
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Redis-сервер не запущен. Запустите его перед запуском сервера."
    echo "Например, 'redis-server' или 'brew services start redis' (на macOS)."
    exit 1
fi

# Применение миграций
echo "Применение миграций..."
python manage.py migrate

# Запуск сервера разработки
echo "Запуск сервера Django..."
python manage.py runserver

# Если вы хотите запустить с конкретным IP и портом:
# python manage.py runserver 0.0.0.0:8000 