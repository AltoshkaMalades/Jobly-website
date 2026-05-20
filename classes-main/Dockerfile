# Используем официальный легкий образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Отключаем буферизацию логов Python (чтобы сразу видеть ошибки в терминале)
ENV PYTHONUNBUFFERED=1

# Копируем файл зависимостей
COPY requirements.txt /app/

# Обновляем pip и устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# На всякий случай доустанавливаем embed-video, если его забыли внести в requirements.txt
RUN pip install --no-cache-dir django-embed-video

# Копируем весь остальной код проекта в контейнер
COPY . /app/

# Открываем порт 8000 для Джанго
EXPOSE 8000

# Команда для запуска сервера внутри Docker
CMD ["sh", "-c", "python manage.py migrate && python manage.py seed_learning && gunicorn core.wsgi:application --bind 0.0.0.0:10000"]