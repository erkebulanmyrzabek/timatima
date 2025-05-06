#!/bin/bash

# Создание директории для логов, если ее нет
mkdir -p logs

# Запуск тестов для всех приложений
echo "Запуск тестов для всех приложений..."
python manage.py test apps

# Запуск тестов для конкретных приложений
# echo "Запуск тестов для приложения accounts..."
# python manage.py test apps.accounts

# echo "Запуск тестов для приложения news..."
# python manage.py test apps.news

# Запуск с покрытием кода (требуется coverage)
# echo "Запуск тестов с покрытием кода..."
# coverage run --source='apps' manage.py test apps
# coverage report

echo "Тестирование завершено!" 