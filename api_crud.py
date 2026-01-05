from typing import List, Optional
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models import Artist, Concert, Country, City, Venue, SetlistItem


# --- Statistics (using SQLAlchemy ORM) ---

async def get_stats_top_artists(db: AsyncSession) -> List[dict]:
    """Top 10 artists by concert count"""
    query = (
        select(Artist.artist_name.label("name"), func.count(Concert.concert_id).label("count"))
        .join(Concert)
        .group_by(Artist.artist_name)
        .order_by(func.count(Concert.concert_id).desc())
        .limit(10)
    )
    result = await db.execute(query)
    return [{"name": row.name, "count": row.count} for row in result]


async def get_stats_top_songs(db: AsyncSession) -> List[dict]:
    """Top 20 songs"""
    query = (
        select(SetlistItem.song_name.label("name"), func.count().label("count"))
        .group_by(SetlistItem.song_name)
        .order_by(func.count().desc())
        .limit(20)
    )
    result = await db.execute(query)
    return [{"name": row.name, "count": row.count} for row in result]


async def get_stats_concerts_by_year(db: AsyncSession) -> List[dict]:
    """Concerts by year"""
    query = (
        select(
            extract('YEAR', Concert.concert_date).label("year"),
            func.count().label("count")
        )
        .group_by("year")
        .order_by("year")
    )
    result = await db.execute(query)
    return [{"year": int(row.year), "count": row.count} for row in result]


async def get_stats_geography(db: AsyncSession) -> List[dict]:
    """Top countries by concert count"""
    query = (
        select(Country.country_name.label("name"), func.count().label("count"))
        .join(City, City.country_code == Country.country_code)
        .join(Venue, Venue.city_id == City.city_id)
        .join(Concert, Concert.venue_id == Venue.venue_id)
        .group_by(Country.country_name)
        .order_by(func.count().desc())
        .limit(15)
    )
    result = await db.execute(query)
    return [{"name": row.name, "count": row.count} for row in result]


async def get_stats_cities(db: AsyncSession) -> List[dict]:
    """Top cities by concert count"""
    query = (
        select(City.city_name.label("name"), func.count().label("count"))
        .join(Venue, Venue.city_id == City.city_id)
        .join(Concert, Concert.venue_id == Venue.venue_id)
        .group_by(City.city_name)
        .order_by(func.count().desc())
        .limit(15)
    )
    result = await db.execute(query)
    return [{"name": row.name, "count": row.count} for row in result]


async def get_stats_heatmap(db: AsyncSession) -> List[dict]:
    """Heatmap data (year, month, count)"""
    query = (
        select(
            extract('YEAR', Concert.concert_date).label("year"),
            extract('MONTH', Concert.concert_date).label("month"),
            func.count().label("count")
        )
        .where(extract('YEAR', Concert.concert_date) >= 2010)
        .group_by("year", "month")
        .order_by("year", "month")
    )
    result = await db.execute(query)
    return [{"year": int(row.year), "month": int(row.month), "count": row.count} for row in result]


# --- Details ---

async def get_artist_details(db: AsyncSession, artist_mbid: str) -> Optional[dict]:
    """Full artist information with concerts"""
    query = (
        select(Artist)
        .options(
            selectinload(Artist.concerts)
            .selectinload(Concert.venue)
            .selectinload(Venue.city)
            .selectinload(City.country)
        )
        .where(Artist.artist_mbid == artist_mbid)
    )

    result = await db.execute(query)
    artist = result.scalar_one_or_none()

    if not artist:
        return None

    concerts = [
        {
            "concert_id": concert.concert_id,
            "concert_date": concert.concert_date,
            "tour_name": concert.tour_name,
            "venue_name": concert.venue.venue_name,
            "city_name": concert.venue.city.city_name,
            "country_name": concert.venue.city.country.country_name
        }
        for concert in sorted(artist.concerts, key=lambda c: c.concert_date, reverse=True)
    ]

    return {
        "artist": {
            "artist_mbid": artist.artist_mbid,
            "artist_name": artist.artist_name
        },
        "concerts": concerts
    }


async def get_concert_details(db: AsyncSession, concert_id: str) -> Optional[dict]:
    """Concert details with setlist"""
    query = (
        select(Concert)
        .options(
            selectinload(Concert.artist),
            selectinload(Concert.venue).selectinload(Venue.city).selectinload(City.country),
            selectinload(Concert.setlist_items)
        )
        .where(Concert.concert_id == concert_id)
    )

    result = await db.execute(query)
    concert = result.scalar_one_or_none()

    if not concert:
        return None

    return {
        "concert_id": concert.concert_id,
        "concert_date": concert.concert_date,
        "tour_name": concert.tour_name,
        "artist": {
            "artist_mbid": concert.artist.artist_mbid,
            "artist_name": concert.artist.artist_name
        },
        "venue": {
            "venue_name": concert.venue.venue_name,
            "city_name": concert.venue.city.city_name,
            "country_name": concert.venue.city.country.country_name
        },
        "setlist": [
            {
                "song_name": item.song_name,
                "position_in_set": item.position_in_set,
                "is_cover": item.is_cover
            }
            for item in sorted(concert.setlist_items, key=lambda x: x.position_in_set)
        ]
    }
