#!/bin/bash

# Создание директории для логов, если ее нет
mkdir -p logs

# Создание директорий для изображений, если их нет
mkdir -p media/news/images
mkdir -p media/lawyers/photos
mkdir -p media/users/photos
mkdir -p media/podcasts/images

# Загрузка фикстур
echo "Загрузка начальных данных для пользователей..."
python manage.py loaddata apps/accounts/fixtures/initial_data.json

echo "Загрузка начальных данных для адвокатов..."
python manage.py loaddata apps/lawyers/fixtures/initial_data.json

echo "Загрузка начальных данных для новостей..."
python manage.py loaddata apps/news/fixtures/initial_data.json

echo "Загрузка фикстур завершена."
echo ""
echo "Учетные данные для входа:"
echo "========================="
echo "Администратор:"
echo "Email: admin@example.com"
echo "Пароль: password"
echo ""
echo "Обычный пользователь:"
echo "Email: user@example.com"
echo "Пароль: password"
echo ""
echo "Адвокат:"
echo "Email: lawyer@example.com"
echo "Пароль: password"
echo "=========================" 