# Один образ на app/worker/beat: код общий, отличается только команда запуска
# (она задаётся в docker-compose.yml для каждого сервиса).

FROM python:3.12-slim

# Системные зависимости: build-essential нужен для сборки некоторых колёс
# (например, telethon на момент учебника не имел готового wheel под 3.13).
# На 3.12 в большинстве случаев всё ставится из колёс, но оставляем gcc на всякий.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ставим зависимости отдельным слоем — кэш не инвалидируется при правке кода
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Порт API
EXPOSE 8000

# Команда по умолчанию — uvicorn.
# Для worker/beat docker-compose переопределяет CMD.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
