import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List

# --- 1. Імпортуємо ВСЕ, що нам потрібно ---

# Функції для підключення до БД
from api_database import get_db_pool, close_db_pool

# Наші Pydantic-схеми (JSON-креслення)
from api_schemas import (
    StatTopItem, StatYearItem, ArtistDetail, ConcertDetail
)

# Наші SQL-функції (CRUD)
import api_crud as crud


# --- 2. Керування життєвим циклом (Lifespan) ---
# (Без змін)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск сервера...")
    await get_db_pool()
    print("Сервер успішно запущено. Пул БД готовий.")

    yield

    print("Зупинка сервера...")
    await close_db_pool()
    print("Сервер успішно зупинено. Пул БД закрито.")


# --- 3. Створення додатку FastAPI ---
# (Без змін)
app = FastAPI(
    title="Rock Concerts API",
    description="API для бази даних концертів з Setlist.fm",
    version="1.0.0",
    lifespan=lifespan
)

# --- 4. Налаштування CORS ---
# (Без змін)
origins = [
    "http://localhost", "http://localhost:8000",
    "http://127.0.0.1:8000", "null",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 5. Створення Ендпоінтів API ---

@app.get("/")
async def get_root():
    """
    Корінь API. Просто перевіряє, чи сервер живий.
    """
    return {"message": "Привіт! Ваш Rock API працює."}


# === Маршрути для Статистики ===

@app.get("/api/v1/stats/top-artists", response_model=List[StatTopItem])
async def get_top_artists():
    """
    Отримує Топ-10 артистів за кількістю концертів.
    """
    # response_model=List[StatTopItem] автоматично конвертує
    # дані з БД у валідований JSON
    return await crud.get_stats_top_artists()


@app.get("/api/v1/stats/top-songs", response_model=List[StatTopItem])
async def get_top_songs():
    """
    Отримує Топ-20 найпопулярніших пісень.
    """
    return await crud.get_stats_top_songs()


@app.get("/api/v1/stats/concerts-by-year", response_model=List[StatYearItem])
async def get_concerts_by_year():
    """
    Отримує кількість концертів по роках.
    """
    return await crud.get_stats_concerts_by_year()


# === Маршрути для Деталізації ===

@app.get("/api/v1/artists/{artist_mbid}", response_model=ArtistDetail)
async def get_artist_by_mbid(artist_mbid: str):
    """
    Отримує повну інформацію про артиста за його MusicBrainz ID (mbid).
    """
    artist_data = await crud.get_artist_details(artist_mbid)

    if artist_data is None:
        # Якщо CRUD-функція повернула None, кидаємо помилку 404
        raise HTTPException(
            status_code=404,
            detail=f"Артиста з mbid '{artist_mbid}' не знайдено."
        )

    return artist_data


@app.get("/api/v1/concerts/{concert_id}", response_model=ConcertDetail)
async def get_concert_by_id(concert_id: str):
    """
    Отримує повну інформацію про концерт за його ID.
    """
    concert_data = await crud.get_concert_details(concert_id)

    if concert_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Концерт з ID '{concert_id}' не знайдено."
        )

    return concert_data


# --- 6. Запуск сервера ---
# (Без змін)
if __name__ == "__main__":
    print("--- Запуск API сервера (режим розробки) ---")
    uvicorn.run(
        "api_main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )