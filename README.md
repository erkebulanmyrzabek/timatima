# Дом Адвокатов - Юридический портал

Бэкенд для юридического веб-сайта с функционалом управления контентом, аутентификацией, авторизацией, мультиязычностью и кастомной админ-панелью.

## Технологии

- **Фреймворк**: Django + Django REST Framework (DRF)
- **База данных**: SQLite
- **Кэширование**: Redis
- **Аутентификация**: JWT
- **Шифрование**: bcrypt для паролей
- **Безопасность**: Защита от XSS, SQL-инъекций, CSRF, ограничение попыток входа
- **Логирование**: Логи действий пользователей

## Требования

- Python 3.9+
- Redis
- Зависимости из requirements.txt

## Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/your-username/lawyers-house.git
cd lawyers-house
```

2. Создать и активировать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Настроить переменные окружения:
```bash
# Скопировать пример .env файла
cp .env.example .env

# Отредактировать .env файл и установить собственные значения
nano .env
```

5. Применить миграции:
```bash
python manage.py migrate
```

6. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустить сервер:
```bash
python manage.py runserver
```

## Структура проекта

```
dom_advokatov/
├── core/               # Настройки проекта
└── apps/               # Приложения
    ├── accounts/       # Пользователи, регистрация, профили
    ├── news/           # Новости (CRUD)
    ├── podcasts/       # Подкасты (CRUD)
    ├── telegram_posts/ # Посты из Telegram (CRUD)
    ├── lawyers/        # Адвокаты (CRUD, фильтрация)
    ├── localization/   # Локализация (переводы интерфейса)
    ├── mainpage/       # Контент главной страницы
    └── admin_custom/   # API для кастомной админ-панели
```

## API Endpoints

Доступны два варианта API endpoints - с версионированием и без (для обратной совместимости).

### Версионированные endpoints
- `POST /api/v1/auth/login/` - Вход
- `POST /api/v1/auth/register/` - Регистрация
- `POST /api/v1/auth/refresh/` - Обновление токена

### Обратная совместимость
- `POST /api/auth/login/` - Вход
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/refresh/` - Обновление токена

### Пользователи
- `POST /api/users/profile/` - Обновление данных профиля
- `POST /api/users/update-2fa/` - Обновление номера для 2FA
- `DELETE /api/users/delete/` - Удаление аккаунта

### Новости
- `GET /api/news/` - Список новостей
- `POST /api/news/` - Создание новости (только для staff)
- `PUT /api/news/{id}/` - Обновление новости (только для staff)
- `DELETE /api/news/{id}/` - Удаление новости (только для staff)

### Подкасты
- `GET /api/podcasts/` - Список подкастов
- `POST /api/podcasts/` - Создание подкаста (только для staff)
- `PUT /api/podcasts/{id}/` - Обновление подкаста (только для staff)
- `DELETE /api/podcasts/{id}/` - Удаление подкаста (только для staff)

### Telegram Посты
- `GET /api/telegram-posts/` - Список постов
- `POST /api/telegram-posts/` - Создание поста (только для staff)
- `PUT /api/telegram-posts/{id}/` - Обновление поста (только для staff)
- `DELETE /api/telegram-posts/{id}/` - Удаление поста (только для staff)

### Адвокаты
- `GET /api/lawyers/` - Список адвокатов
- `POST /api/lawyers/` - Создание адвоката (только для staff)
- `PUT /api/lawyers/{id}/` - Обновление адвоката (только для staff)
- `DELETE /api/lawyers/{id}/` - Удаление адвоката (только для staff)

### Локализация
- `GET /api/localization/` - Список переводов (только для staff)
- `POST /api/localization/` - Создание перевода (только для staff)
- `PUT /api/localization/{id}/` - Обновление перевода (только для staff)
- `DELETE /api/localization/{id}/` - Удаление перевода (только для staff)
- `GET /api/localization/by-lang/?lang=ru` - Переводы по языку (публичный доступ)

### Главная страница
- `GET /api/mainpage/news/` - Новости для главной страницы
- `GET /api/mainpage/podcasts/` - Подкасты для главной страницы
- `GET /api/mainpage/telegram-posts/` - Telegram посты для главной страницы
- `GET /api/mainpage/lawyers/` - Адвокаты для главной страницы

### Админ-панель
- `GET /api/admin/users/` - Список админов (только superuser)
- `POST /api/admin/users/` - Создание админа (только superuser)
- `PUT /api/admin/users/{id}/` - Обновление админа (только superuser)
- `DELETE /api/admin/users/{id}/` - Удаление админа (только superuser)

## Документация API

Документация API доступна после запуска проекта:
- Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- ReDoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

## Тестирование

Для запуска тестов используйте:
```bash
# Запуск всех тестов
./run_tests.sh

# Запуск тестов для конкретного приложения
python manage.py test apps.accounts
```

## Производительность

- Поддержка до 100 одновременных пользователей
- Максимальное время ответа сервера: 200 мс
- Кэширование GET-запросов через Redis для оптимизации производительности

## Безопасность

- Пароли хэшируются с использованием bcrypt
- Защита от XSS через санитизацию входных данных
- Защита от SQL-инъекций через ORM Django
- Защита от CSRF через middleware Django
- Ограничение попыток входа (Django Axes)

## Лицензия

[MIT](LICENSE) 