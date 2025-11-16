from typing import List, Optional
from asyncpg import Record  # <-- ПРАВИЛЬНО
# Імпортуємо наші функції-помічники для виконання запитів
from api_database import fetch_all, fetch_one


# --- 1. Статистика (Stats) ---

async def get_stats_top_artists() -> List[Record]:
    """
    Повертає Топ-10 артистів за кількістю концертів.
    """
    query = """
            SELECT T2.artist_name as name, COUNT(T1.concert_id) as count
            FROM Concerts AS T1
                JOIN Artists AS T2 \
            ON T1.artist_mbid = T2.artist_mbid
            GROUP BY T2.artist_name
            ORDER BY count DESC
                LIMIT 10; \
            """
    return await fetch_all(query)


async def get_stats_top_songs() -> List[Record]:
    """
    Повертає Топ-20 найчастіше виконуваних пісень.
    """
    query = """
            SELECT song_name as name, COUNT(*) as count
            FROM SetlistItems
            GROUP BY song_name
            ORDER BY count DESC
                LIMIT 20; \
            """
    return await fetch_all(query)


async def get_stats_concerts_by_year() -> List[Record]:
    """
    Повертає кількість концертів по кожному року.
    """
    query = """
            SELECT EXTRACT(YEAR FROM concert_date) ::INT as year, COUNT(*) as count
            FROM Concerts
            GROUP BY year
            ORDER BY year ASC; \
            """
    return await fetch_all(query)


# --- 2. Деталізація (Details) ---

async def get_artist_details(artist_mbid: str) -> Optional[dict]:
    """
    Повертає повну інформацію про артиста та список його концертів.
    """
    # Запит 1: Отримуємо базову інфо про артиста
    artist_query = "SELECT artist_mbid, artist_name FROM Artists WHERE artist_mbid = $1;"
    artist_record = await fetch_one(artist_query, artist_mbid)

    if not artist_record:
        return None  # Артиста не знайдено

    # Запит 2: Отримуємо список ВСІХ його концертів
    # Це наш перший великий JOIN
    concerts_query = """
                     SELECT T1.concert_id, \
                            T1.concert_date, \
                            T1.tour_name, \
                            T2.venue_name, \
                            T3.city_name, \
                            T4.country_name
                     FROM Concerts AS T1
                              JOIN Venues AS T2 ON T1.venue_id = T2.venue_id
                              JOIN Cities AS T3 ON T2.city_id = T3.city_id
                              JOIN Countries AS T4 ON T3.country_code = T4.country_code
                     WHERE T1.artist_mbid = $1
                     ORDER BY T1.concert_date DESC; \
                     """
    concert_records = await fetch_all(concerts_query, artist_mbid)

    # Збираємо все в один об'єкт, який відповідає нашій схемі ArtistDetail
    return {
        "artist": artist_record,
        "concerts": concert_records
    }


async def get_concert_details(concert_id: str) -> Optional[dict]:
    """
    Повертає повну інформацію про ОДИН концерт.
    """
    # Запит 1: Отримуємо основну інфо (про концерт, артиста, місце)
    # Це наш НАЙБІЛЬШИЙ JOIN
    concert_query = """
                    SELECT T1.concert_id, \
                           T1.concert_date, \
                           T1.tour_name, \
                           T2.artist_mbid, \
                           T2.artist_name, \
                           T3.venue_name, \
                           T4.city_name, \
                           T5.country_name
                    FROM Concerts AS T1
                             JOIN Artists AS T2 ON T1.artist_mbid = T2.artist_mbid
                             JOIN Venues AS T3 ON T1.venue_id = T3.venue_id
                             JOIN Cities AS T4 ON T3.city_id = T4.city_id
                             JOIN Countries AS T5 ON T4.country_code = T5.country_code
                    WHERE T1.concert_id = $1; \
                    """
    concert_record = await fetch_one(concert_query, concert_id)

    if not concert_record:
        return None  # Концерт не знайдено

    # Запит 2: Отримуємо сетліст для цього концерту
    setlist_query = """
                    SELECT song_name, position_in_set, is_cover
                    FROM SetlistItems
                    WHERE concert_id = $1
                    ORDER BY position_in_set ASC; \
                    """
    setlist_records = await fetch_all(setlist_query, concert_id)

    # asyncpg повертає один 'Record', який містить всі дані
    # Нам потрібно реструктурувати його для нашої JSON-схеми

    # 'dict(concert_record)' перетворює Record в словник
    data = dict(concert_record)

    return {
        "concert_id": data["concert_id"],
        "concert_date": data["concert_date"],
        "tour_name": data["tour_name"],
        "artist": {
            "artist_mbid": data["artist_mbid"],
            "artist_name": data["artist_name"]
        },
        "venue": {
            "venue_name": data["venue_name"],
            "city_name": data["city_name"],
            "country_name": data["country_name"]
        },
        "setlist": setlist_records
    }