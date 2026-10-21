# Базовый образ Python для промышленного развертывания
FROM python:3.12-slim

# Настройки среды выполнения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Установка системных утилит (curl для health-check)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория приложения
WORKDIR /app

# Копирование файла зависимостей и их установка
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода проекта
COPY . /app/

# Сборка статических файлов Django и миграции
RUN python manage.py collectstatic --noinput || true

# Открытие сетевого порта
EXPOSE 8000

# Health-check мониторинг состояния сервиса (ПР7)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Запуск WSGI-сервера Gunicorn в промышленном режиме с 3 воркерами
CMD ["gunicorn", "coursework_service.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
