# Установка

> [!NOTE] Внимание!
>В разработаке, могут быть изменения, дополнения и улучшения!

## Инструкция по настройке

### Клонируем проект (если нужно)

```sh
git clone <repository-url> bugflow
cd bugflow
```

### Создаем структуру папок

```sh
mkdir -p backend/{app/{core,models,schemas,api/{v1/endpoints}},alembic/versions,requirements,tests}
mkdir -p frontend/{src/{components,views,stores,composables,router,api},public}
```

### Переходим в backend

```sh
cd backend
```

### Создаем виртуальное окружение

```sh
python -m venv venv
```

### Активируем (Windows)

```sh
venv\Scripts\activate
```

### ИЛИ Активируем (Linux/Mac)

```sh
source venv/bin/activate
```

### Устанавливаем зависимости

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

### Создаем файлы конфигурации

```sh
cp .env.example .env
```

### Запускаем БД и Redis

```sh
make db
```

### Создаем миграции

```sh
alembic init alembic
```

### Настраиваем переменные

- Настраиваем alembic/env.py (нужно добавить импорт моделей)
- Открываем backend/alembic/env.py и добавляем:
  - from app.models import Base
  - target_metadata = Base.metadata

### Создаем первую миграцию

```sh
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Запускаем сервер

```sh
make dev
```

## Проверка установки

создадим временный файл:

```py
# backend/app/main.py (временный файл для проверки)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="BugFlow API",
    version="0.1.0",
    description="Lightweight bug tracker API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "BugFlow API is running!", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

#### Проверка работы

```bash
# Установка завершена, проверяем:
curl http://localhost:8000/
# Должен вернуть: {"message": "BugFlow API is running!", "version": "0.1.0"}

curl http://localhost:8000/health
# Должен вернуть: {"status": "healthy"}

# Открываем документацию API:
# http://localhost:8000/api/docs
# http://localhost:8000/api/redoc
```

🎯 Следующие шаги

После настройки окружения мы можем:

- Настроить Alembic миграции с правильным env.py
- Создать конфигурацию приложения в app/core/config.py
- Реализовать подключение к БД с зависимостями
- Написать базовые CRUD операции для User
- Реализовать аутентификацию с JWT