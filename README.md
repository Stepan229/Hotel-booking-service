
# 🏨 Hotel Booking Service

Django REST API сервис для бронирования номеров в отелях.

## 🚀 Установка и запуск

### Предварительные требования
- Python 3.10+
- Poetry
- Docker & Docker Compose

### Запуск приложения

```bash
# Клонирование репозитория
git clone <repository-url>
cd booking-service

# Создание файла .env 
cp .env.example .env
# Отредактируйте .env файл, указав ваши настройки

# Запуск приложения
docker-compose up --build

# Приложение будет доступно по http://localhost:8000
```

## 🧪 Тестирование

```bash

# Запуск тестов 
python manage.py test

# Запуск с покрытием кода
poetry run coverage run manage.py test

```

## 🛠️ Разработка

### Установка 
```bash
poetry install 
```

### Миграции
```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Проверка миграций
python manage.py makemigrations
```

## ⚙️ Конфигурация

Основные настройки в файлах:
- `.env` - переменные окружения 
- `booking_service/settings.py` - настройки Django
- `docker-compose.yml` - конфигурация Docker
- `pyproject.toml` - зависимости и инструменты

## 📦 Основные технологии

- **Backend**: Django + Django REST Framework
- **База данных**: PostgreSQL
- **Контейнеризация**: Docker
- **Зависимости**: Poetry
- **Тестирование**: Factory Boy
- **Линтинг**: Ruff

---

**Приложение запущено!** 🎉 Доступно по адресу: http://localhost:8000