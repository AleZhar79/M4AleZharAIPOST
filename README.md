# M4AleZharAIPOST

Учебный проект 4-го модуля: **бот, который сам пишет посты в Telegram-канал**.

Сервис тянет новости из RSS, переписывает их через AI в формате telegram-поста и публикует в твой канал. Всё работает по расписанию: парсинг — каждые 30 минут, генерация и публикация — по триггеру (API или Celery-таск).

---

## Что внутри (стек)

| Слой | Технология | Зачем |
|---|---|---|
| API | FastAPI + Uvicorn | Принимать запросы, отдавать Swagger |
| БД | SQLite + SQLAlchemy | Хранить источники, новости, готовые посты |
| Очередь задач | Celery + Redis | Парсить и публиковать в фоне, по расписанию |
| Парсинг новостей | feedparser, requests | Тянуть RSS |
| AI | OpenAI SDK через OpenRouter | Переписывать новость в пост |
| Telegram | Telethon (user-account) | Публиковать пост в канал |

---

## Архитектура коротко

```
              ┌──────────────┐
              │ Celery Beat  │  раз в 30 мин кидает таск
              └──────┬───────┘
                     ▼
   RSS ──► parse_all_sources_task ──► news_items (БД)
                                          │
                                          ▼
                              generate_post_task / pipeline_task
                                          │
                                          ▼
                                   posts (БД, draft)
                                          │
                              publish_post_task / POST /api/publish/{id}
                                          ▼
                                  Telethon ──► Telegram-канал
```

Три процесса должны крутиться одновременно:
1. **uvicorn** — API на :8000
2. **celery worker** — исполняет таски
3. **celery beat** — кладёт таски по расписанию

---

## Запуск через Docker (рекомендую)

### 1. Сначала локально получи Telegram-сессию

Telethon при первом запуске спросит код из SMS и (если есть) 2FA-пароль. В контейнере это сделать нельзя — нет интерактивного ввода. Поэтому **один раз авторизуйся локально**:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # на Windows: copy .env.example .env
# заполни .env (см. раздел «Переменные окружения» ниже)

python scripts/tg_login.py
```

Введи код из SMS (и 2FA-пароль, если он у тебя стоит). После успеха в корне появится файл `tg_session.session`. Этот файл — твой ключ к аккаунту, **не коммить его в git** (уже в `.gitignore`).

### 2. Подготовь папку для данных

Docker нужно явно показать, что `aibot.db` и `tg_session.session` — это **файлы**, а не директории. Положи их в папку `./data/` рядом с проектом:

```bash
mkdir -p data
cp aibot.db data/aibot.db                    # если уже есть после локального запуска
cp tg_session.session data/tg_session.session  # обязательно — после шага 1
```

Если `aibot.db` ещё нет — создай пустой файл: `touch data/aibot.db` (Linux/Mac) или `type nul > data\aibot.db` (Windows).

### 3. Запусти docker-compose

```bash
docker compose up --build
```

Compose поднимет 4 сервиса: redis, app (uvicorn :8000), worker, beat. Файлы из `./data/` монтируются как volume, переживают перезапуск.

API доступно на http://localhost:8000/docs

### 4. Засей источники (один раз)

В отдельном терминале:

```bash
docker compose exec app python scripts/seed_sources.py
```

Это добавит 6 рабочих RSS (Коммерсант, Лента, ТАСС, РИА, Хабр, РБК). Команда идемпотентная — можно запускать сколько угодно раз, дубликатов не будет.

### 5. Остановить

```bash
docker compose down
```

Данные (БД и сессия) останутся в `./data/`.

---

## Запуск без Docker (Windows, нативный режим)

Если Docker не хочется ставить — поднимай руками. Нужно **3 окна PowerShell**, в каждом активируй venv.

### Один раз: установка

```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
copy .env.example .env
# отредактируй .env
python scripts\tg_login.py
python scripts\seed_sources.py
```

Redis на Windows нативно нет. Поставь один из вариантов:
- **Docker Desktop** + `docker run -d -p 6379:6379 --name redis redis:7-alpine`
- **WSL** + `sudo apt install redis-server`
- **Memurai** (платный, бесплатная dev-версия) — Redis-совместимый

### Окно 1 — API

```powershell
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

### Окно 2 — Celery worker

```powershell
.\venv\Scripts\activate
celery -A celery_worker.celery_app worker --loglevel=info --pool=solo
```

⚠️ `--pool=solo` на Windows **обязательно**. Без него Celery упадёт.

### Окно 3 — Celery beat

```powershell
.\venv\Scripts\activate
celery -A celery_worker.celery_app beat --loglevel=info
```

---

## Переменные окружения (.env)

```ini
# База
DATABASE_URL=sqlite:///./aibot.db

# Очередь (в docker-compose: redis://redis:6379/0)
REDIS_URL=redis://localhost:6379/0

# AI через OpenRouter
OPENAI_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=google/gemma-4-31b-it:free

# Telegram (Telethon, user-account)
TELEGRAM_API_ID=6
TELEGRAM_API_HASH=eb06d4abfb49dc3eeb1aeb98ae0f581e
TELEGRAM_PHONE=+7XXXXXXXXXX
TELEGRAM_CHANNEL=@your_channel
TELEGRAM_SESSION_NAME=tg_session
```

Где взять ключи:
- **OPENAI_API_KEY** — https://openrouter.ai/keys (есть бесплатные модели)
- **TELEGRAM_API_ID/HASH** — либо свои с https://my.telegram.org/apps, либо публичные тестовые из официальной доки Telethon (`6` / `eb06d4abfb49dc3eeb1aeb98ae0f581e`). Тестовые **только для учебных проектов**.

---

## API endpoints

Полный Swagger: http://localhost:8000/docs

### Источники
- `POST /api/sources` — добавить RSS-источник
- `GET /api/sources` — список источников

### Новости
- `GET /api/news` — последние спарсенные новости
- `POST /api/parse/run` — запустить парсинг **синхронно** (для отладки)
- `POST /api/parse/run-async` — запустить парсинг **через Celery** (вернёт task_id)

### Посты
- `POST /api/generate/{news_id}` — сгенерировать пост из конкретной новости
- `GET /api/posts` — список постов (draft / published)

### Публикация
- `POST /api/publish/{post_id}` — опубликовать пост **синхронно**
- `POST /api/publish/run-async/{post_id}` — опубликовать **через Celery**
- `POST /api/pipeline/run-async` — полный цикл «парсинг → AI → публикация» одним вызовом

---

## Типичные грабли

**`RuntimeError: There is no current event loop in thread 'AnyIO worker thread'`**
FastAPI sync-endpoint запускает Telethon в воркер-треде без asyncio loop. Лечится `_ensure_event_loop()` в `app/telegram/bot.py` (уже исправлено).

**Celery worker сразу падает на Windows**
Добавь `--pool=solo`. Дефолтный prefork на Windows не работает.

**Telethon собирается из исходников и падает по таймауту**
На Python 3.13 нет колеса telethon. Перед установкой обнови инструменты:
```bash
python -m pip install --upgrade pip setuptools wheel
```

**Worker не видит изменения в коде**
В отличие от `uvicorn --reload`, Celery worker не следит за файлами. **Перезапускай руками** после правки `.py`.

**Изменил `.env` — ничего не поменялось**
`--reload` смотрит только `.py`. После правки `.env` перезапусти **все три** процесса.

**Парсер ничего не находит**
Источники в БД пустые? Запусти `python scripts/seed_sources.py`. Или RSS физически мёртвый — проверь его в браузере.

**`tg_session.session` нельзя коммитить**
Это полный доступ к твоему аккаунту Telegram. Если случайно закоммитил — отзови сессию в настройках Telegram → Devices.

---

## Структура проекта

```
M4AleZharAIPOST/
├── app/
│   ├── api/endpoints.py        # все HTTP endpoints
│   ├── ai/generator.py         # OpenAI/OpenRouter генерация
│   ├── telegram/
│   │   ├── bot.py              # Telethon: send_message
│   │   └── publisher.py        # бизнес-логика публикации
│   ├── parsers/                # RSS + (опц.) Telegram parsing
│   ├── tasks.py                # Celery-таски
│   ├── models.py               # SQLAlchemy: Source, NewsItem, Post
│   ├── database.py             # engine + SessionLocal
│   ├── config.py               # pydantic settings из .env
│   └── main.py                 # FastAPI app
├── scripts/
│   ├── tg_login.py             # первичная авторизация Telethon
│   └── seed_sources.py         # засев RSS-источников
├── celery_worker.py            # точка входа Celery + beat schedule
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
└── README.md
```

---

## Что можно улучшить дальше

- **Промпт для AI** — сейчас модель иногда «улетает» от темы новости. Доработать system-prompt в `app/ai/generator.py`, добавить ограничение по длине, явно требовать ссылку на источник.
- **Защита от дублей** — фильтр по контенту, не только по URL.
- **Postgres вместо SQLite** — когда нагрузка вырастет.
- **Alembic-миграции** — сейчас `Base.metadata.create_all`, для прода нужен Alembic.
- **Логирование в файл** — сейчас всё в stdout.
- **Авторизация API** — сейчас всё открыто, любой может дёрнуть `/api/publish`.
- **Веб-морда** — простая страница со списком драфтов и кнопкой «опубликовать».

---

## Лицензия и оговорки

Учебный проект. Тестовые ключи Telethon (`API_ID=6`) — только для обучения, не для боевого использования. Не публикуй чужой контент без разрешения правообладателя.
