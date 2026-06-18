# M4AleZharAIPOST — AI-генератор постов для Telegram

Учебный проект модуля 4. Сервис собирает новости с сайтов и Telegram-каналов, через AI генерирует посты и публикует их в Telegram-канал. Управление — через REST API с Swagger.

Проект делается **по блокам**. В репозитории сейчас лежит **полный скелет** с mock-реализациями для блоков 3–5, чтобы проект всегда был запускаемым.

---

## Текущий статус

| Блок | Что | Состояние |
|------|-----|-----------|
| 1 | FastAPI + SQLite + CRUD для sources / keywords / posts | ✅ готово |
| 2 | Парсинг новостей: RSS-сайты + Telegram (mock) | ✅ готово |
| 3 | Celery + Redis + фоновые задачи | 🟡 скелет (mock) |
| 4 | AI-генерация постов (OpenAI) | 🟡 скелет (mock) |
| 5 | Публикация в Telegram (Telethon) | 🟡 скелет (mock) |
| 6 | README, docker-compose, финализация | 🟡 базовый README готов |

«Mock» = функция возвращает фиксированный ответ и пишет в лог. Реальная интеграция подключается заменой тела одной-двух функций — комментарии в коде показывают, что именно поменять.

---

## Стек

- **FastAPI** + Uvicorn — REST API + Swagger
- **SQLAlchemy** + SQLite — хранилище
- **feedparser** + requests — парсинг RSS
- **Celery + Redis** — фоновые задачи и расписание (подключим в Блоке 3)
- **OpenAI** — генерация постов (подключим в Блоке 4)
- **Telethon** — Telegram (подключим в Блоке 5)

---

## Структура проекта

```
M4AleZharAIPOST/
├── app/
│   ├── main.py                 # точка входа FastAPI
│   ├── config.py               # настройки из .env
│   ├── database.py             # подключение к БД, сессии
│   ├── models.py               # SQLAlchemy-модели: Source, Keyword, NewsItem, Post
│   ├── utils.py                # общий логгер
│   ├── tasks.py                # Celery-таски (Блок 3, пока mock)
│   ├── api/
│   │   ├── endpoints.py        # все REST-эндпоинты
│   │   └── schemas.py          # Pydantic-схемы
│   ├── news_parser/
│   │   ├── sites.py            # RSS-парсер
│   │   ├── telegram.py         # парсер TG-каналов (Блок 5, пока mock)
│   │   └── service.py          # общая логика + дедупликация
│   ├── ai/
│   │   ├── openai_client.py    # клиент OpenAI (Блок 4, пока mock)
│   │   └── generator.py        # промпт + сборка поста
│   └── telegram/
│       ├── bot.py              # Telethon-клиент (Блок 5, пока mock)
│       └── publisher.py        # публикация поста в канал
├── celery_worker.py            # точка входа Celery (Блок 3, заглушка)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/AleZhar79/M4AleZharAIPOST.git
cd M4AleZharAIPOST
```

### 2. Создать виртуальное окружение и поставить зависимости

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / Mac:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Создать `.env`

```powershell
copy .env.example .env
```
(на Linux/Mac — `cp .env.example .env`)

Для скелета **трогать ничего не нужно** — все ключи пустые, моки сами это поймут.

### 4. Запустить сервер

```bash
uvicorn app.main:app --reload
```

### 5. Открыть Swagger

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Что можно потыкать прямо сейчас (без Redis/OpenAI/Telegram)

### Полный сценарий «end-to-end» на моках

1. **Добавить источник** — `POST /api/sources/`:
   ```json
   {"type":"site","name":"Habr","url":"https://habr.com/ru/rss/articles/","enabled":true}
   ```

2. **Запустить парсинг** — `POST /api/parse/run`.
   Ответ: `{"sources_processed":1,"items_found":20,"items_saved":20,...}`.

3. **Посмотреть собранные новости** — `GET /api/news/?limit=5`.

4. **Сгенерировать пост** (mock OpenAI) — `POST /api/generate/1`
   (1 = `news_id`). В ответе `generated_text` будет mock-постом.

5. **Опубликовать пост** (mock Telegram) — `POST /api/publish/1`
   (1 = `post_id`). Текст «отправится» в консоль uvicorn, статус поста станет `published`.

Весь конвейер ТЗ — парсинг → генерация → публикация — работает на моках.

---

## Переменные окружения

| Переменная | Когда нужна | Что делает |
|------------|-------------|------------|
| `DATABASE_URL` | всегда | путь к базе. По умолчанию SQLite (`sqlite:///./aibot.db`) |
| `OPENAI_API_KEY` | Блок 4 | ключ OpenAI. Без него работает mock |
| `TELEGRAM_API_ID` | Блок 5 | API_ID с [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_API_HASH` | Блок 5 | API_HASH оттуда же |
| `TELEGRAM_BOT_TOKEN` | Блок 5 (опц.) | если будем публиковать через бота, а не как пользователь |
| `TELEGRAM_CHANNEL` | Блок 5 | `@username` канала для публикации |
| `REDIS_URL` | Блок 3 | адрес Redis. По умолчанию `redis://localhost:6379/0` |

---

## Дорожная карта: как заменять mock-и на реальные реализации

### Блок 3 — Celery + Redis

1. Поставить Redis (на Windows — Memurai).
2. В `requirements.txt` добавить:
   ```
   celery==5.4.0
   redis==5.0.8
   ```
3. В `celery_worker.py` раскомментировать блок с `celery_app`.
4. В `app/tasks.py` навесить `@celery_app.task` на функции, импортировав `celery_app` из `celery_worker`.
5. Запустить воркер и beat:
   ```powershell
   celery -A celery_worker.celery_app worker --loglevel=info --pool=solo
   celery -A celery_worker.celery_app beat --loglevel=info
   ```
6. В `app/news_parser/service.py` и эндпоинте `/api/parse/run` ничего не меняем — Celery будет вызывать тот же `run_parsing()`.

### Блок 4 — OpenAI

1. В `requirements.txt` добавить:
   ```
   openai==1.51.0
   ```
2. В `.env` положить `OPENAI_API_KEY=sk-...`.
3. В `app/ai/openai_client.py` заменить тело `call_openai()` на реальный вызов (шаблон в комментариях файла).
4. Добавить обработку `RateLimitError` и `APIError`.
5. Промпт и логика в `app/ai/generator.py` менять не нужно.

### Блок 5 — Telethon

1. В `requirements.txt` добавить:
   ```
   telethon==1.36.0
   ```
2. Получить `API_ID` и `API_HASH` на [my.telegram.org](https://my.telegram.org), положить в `.env`.
3. Создать сессию (первый запуск попросит код из Telegram).
4. В `app/telegram/bot.py` заменить `send_message_mock` и `fetch_messages_mock` на реальные вызовы Telethon (шаблон в комментариях файла).
5. В `app/news_parser/telegram.py` дёргать `fetch_messages` вместо встроенного mock.
6. В `app/telegram/publisher.py` поменять `send_message_mock` на `send_message`.

### Блок 6 — финализация

- Допилить этот README (примеры curl-запросов, скриншоты).
- Опционально — `docker-compose.yml` с сервисами: app, redis, celery_worker, celery_beat.
- Финальный чек-лист готовности.

---

## Примеры запросов

### Создать источник
```bash
curl -X POST http://127.0.0.1:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{"type":"site","name":"Habr","url":"https://habr.com/ru/rss/articles/","enabled":true}'
```

### Запустить парсинг
```bash
curl -X POST http://127.0.0.1:8000/api/parse/run
```

### Сгенерировать пост из новости
```bash
curl -X POST http://127.0.0.1:8000/api/generate/1
```

### Опубликовать пост
```bash
curl -X POST http://127.0.0.1:8000/api/publish/1
```

---

## Чек-лист сдачи проекта

- [x] FastAPI + Swagger
- [x] CRUD для sources / keywords / posts
- [x] Парсинг RSS-сайтов
- [ ] Парсинг Telegram (Блок 5)
- [ ] Celery + Redis + расписание (Блок 3)
- [ ] AI-генерация через OpenAI (Блок 4)
- [ ] Публикация в Telegram (Блок 5)
- [ ] Защита от дублей (частично — для новостей готово)
- [ ] README с инструкцией и примерами
- [ ] docker-compose.yml (опционально)
