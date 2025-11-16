from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List, Optional

# Pydantic (на відміну від SQL) не любить 'orm_mode = True'
# Тепер ми використовуємо 'ConfigDict'
model_config = ConfigDict(from_attributes=True)


# --- Базові моделі (для вкладення) ---
# Описують окремі частини наших таблиць

class ArtistBase(BaseModel):
    model_config = model_config
    artist_mbid: str
    artist_name: str


class VenueBase(BaseModel):
    model_config = model_config
    venue_name: str
    city_name: str
    country_name: str


class SetlistItemBase(BaseModel):
    model_config = model_config
    song_name: str
    position_in_set: int
    is_cover: bool


# --- Моделі для відповідей (Response Models) ---
# Це те, що наш API буде реально відправляти у JSON

class ConcertBasicInfo(BaseModel):
    """
    Скорочена інформація про концерт (для списків).
    """
    model_config = model_config
    concert_id: str
    concert_date: date
    tour_name: Optional[str] = None  # 'None' дозволяє полю бути null
    venue_name: str
    city_name: str
    country_name: str


class ConcertDetail(BaseModel):
    """
    Повна, детальна інформація про ОДИН концерт.
    """
    model_config = model_config
    concert_id: str
    concert_date: date
    tour_name: Optional[str] = None

    # Вкладені об'єкти
    artist: ArtistBase
    venue: VenueBase

    # Список пісень
    setlist: List[SetlistItemBase] = []


class ArtistDetail(BaseModel):
    """
    Повна, детальна інформація про ОДНОГО артиста.
    """
    model_config = model_config
    artist: ArtistBase

    # Список його концертів
    concerts: List[ConcertBasicInfo] = []


# --- Моделі для статистики ---

class StatTopItem(BaseModel):
    """
    Універсальна модель для "Топ-10" (напр. 'Metallica', 150)
    """
    model_config = model_config
    name: str
    count: int


class StatYearItem(BaseModel):
    """
    Модель для статистики по роках (напр. '2023', 500)
    """
    model_config = model_config
    year: int
    count: int