# 🐳 DOCKER: ЗАПУСК ПРОЕКТА

**Дата обновления:** 2 июня 2026 г.

## 🚀 БЫСТРЫЙ СТАРТ (5 минут)

### 1. Установить Docker
Скачай [Docker Desktop](https://www.docker.com/products/docker-desktop) и установи.

### 2. Запустить проект
```bash
cd classes-main
docker-compose up -d
```

### 3. Проверить статус
```bash
docker-compose ps
```

**Ожидаемо:**
```
NAME                  STATUS
simulator-web         Up (healthy)
simulator-redis       Up
simulator-db          Up (healthy)
simulator-celery      Up
simulator-celery-beat Up
```

### 4. Открыть приложение
```
http://localhost:8000
```

### 5. Запустить тесты
```bash
docker-compose exec web pytest tests/performance/ -s -v
```

### 6. Остановить
```bash
docker-compose down
```

---

## 📚 ПОЛНАЯ ДОКУМЕНТАЦИЯ

Для всех команд и подробностей смотри:
**`classes-main/DOCKER_GUIDE.md`**

---

## ⚡ БЫСТРЫЕ КОМАНДЫ

```bash
# Посмотреть логи
docker-compose logs -f web

# Запустить миграцию
docker-compose exec web python manage.py migrate

# Создать супер-юзера
docker-compose exec web python manage.py createsuperuser

# Запустить shell
docker-compose exec web python manage.py shell

# Вход в БД
docker-compose exec db psql -U postgres

# Вход в Redis
docker-compose exec redis redis-cli

# Запустить bash в контейнере
docker-compose exec web bash

# Очистить всё (БД будет удалена!)
docker-compose down -v
```

---

## 🛠️ ШПАРГАЛКА

Для быстрого доступа к командам смотри:
**`classes-main/DOCKER_CHEATSHEET.sh`**

---

## 📖 СТРУКТУРА DOCKER

```
docker-compose.yml
├── web          → Django приложение (8000)
├── redis        → Кэш (6379)
├── db           → PostgreSQL (5432)
├── celery       → Worker для задач
└── celery-beat  → Scheduler
```

---

## 🆘 ПРОБЛЕМЫ?

| Проблема | Решение |
|----------|---------|
| Port занят | `docker-compose down && docker-compose up -d` |
| Контейнер не стартует | `docker-compose logs web` |
| БД недоступна | `docker-compose restart db` |
| Тесты падают | `docker-compose exec web pytest -s` |

---

**Подробная помощь:** `DOCKER_GUIDE.md`
