# Kaspi Parser - Python Backend Test Task

Проект для сбора информации о товарах с Kaspi.kz.  

## 📦 Файлы

- `seed.json` - URL выбранного товара
- `export/product.json` - экспорт основных данных товара
- `export/offers.jsonl` - экспорт офферов продавцов (по желанию, выполнено)


## ⚙️ Технологии

- Python 3.10
- PostgreSQL + SQLAlchemy (async)
- Pydantic для типизации
- Alembic для миграций
- Docker для контейнеризации
- JSON логирование

## Скриншоты
<img width="1920" height="1080" alt="Screenshot 2025-10-04 194039" src="https://github.com/user-attachments/assets/fd9b0a1f-4831-4aa4-89d7-c6dbb4af565e" />
<img width="1920" height="1080" alt="Screenshot 2025-10-04 193933" src="https://github.com/user-attachments/assets/87bb3cce-1e6d-457a-a0e4-4f0db5ca5843" />
<img width="1920" height="1080" alt="Screenshot 2025-10-04 194005" src="https://github.com/user-attachments/assets/b5f41a45-9d1d-4e31-8d3d-d1fe25d41016" />


## 🚀 Установка и запуск

### Локально через Docker

1. Собрать и поднять контейнеры:

```bash
docker-compose up --build
```

2. Контейнер с приложением подключается к PostgreSQL.
Данные из seed.json автоматически собираются и сохраняются в базу и JSON.

### Через локальное окружение Python

Создать виртуальное окружение:
```bash
python -m venv venv
```

Активировать окружение:

- Windows:

```bash
venv\Scripts\activate
```

- Linux/macOS:

```bash
source venv/bin/activate
```


Установить зависимости:
```bash
pip install -r requirements.txt
```

Запустить приложение:
```bash
python -m app.main

```
Приложение выполнит сбор данных по seed.json и сохранит их в PostgreSQL и JSON.

## 📋 Использование
Основной функционал

- Сбор данных о товаре:

    - Название

    - Категория

    - Минимальная и максимальная цена

    - Рейтинг

    - Количество отзывов

    - Характеристики товара (key–value)

    - Ссылки на изображения

    - Офферы продавцов

    - Количество продавцов

- Сохранение данных:

    - В PostgreSQL (таблица products)

    - В export/product.json и export/offers.json

    - История цен и офферов хранится в базе и в json.

    - Логирование выполняется в формате JSON.
- ⏱ Автообновление:
    - Программа запускается каждые 15 минут, обновляя только изменившиеся поля.

## 📌 Примечания
- Все данные корректно сериализуются в JSON и PostgreSQL (используются типы JSONB для полей details, offers, image_links).
- Поддерживаются асинхронные запросы для высокой производительности.
- Типизация строго соблюдается через Pydantic.
