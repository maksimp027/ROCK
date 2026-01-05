import json
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from config import settings
from models import Base, Artist, Country, City, Venue, Concert, SetlistItem

logger = logging.getLogger(__name__)


def get_engine():
    """Create SQLAlchemy engine"""
    connection_string = (
        f"postgresql+pg8000://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )
    return create_engine(connection_string, echo=False)


def load_data_from_json(filename: str) -> Optional[list]:
    """Load concert data from JSON file"""
    if not os.path.exists(filename):
        logger.error(f"File '{filename}' not found. Run 'make_data.py' first!")
        return None

    try:
        with open(filename, "r", encoding="utf-8") as f:
            logger.info(f"Reading file '{filename}'...")
            data = json.load(f)
            logger.info(f"Successfully loaded {len(data)} records from JSON")
            return data
    except json.JSONDecodeError:
        logger.error(f"File '{filename}' is corrupted or contains invalid JSON")
        return None
    except Exception as e:
        logger.exception(f"Unknown error reading file: {e}")
        return None


def get_or_create_artist(session: Session, mbid: str, name: str) -> Artist:
    """Get existing artist or create new one"""
    stmt = select(Artist).where(Artist.artist_mbid == mbid)
    artist = session.scalar(stmt)

    if not artist:
        artist = Artist(artist_mbid=mbid, artist_name=name)
        session.add(artist)
        logger.debug(f"Created new artist: {name}")

    return artist


def get_or_create_country(session: Session, code: str, name: str) -> Country:
    """Get existing country or create new one"""
    stmt = select(Country).where(Country.country_code == code)
    country = session.scalar(stmt)

    if not country:
        country = Country(country_code=code, country_name=name)
        session.add(country)
        logger.debug(f"Created new country: {name} ({code})")

    return country


def get_or_create_city(session: Session, city_name: str, country_code: str) -> City:
    """Get existing city or create new one"""
    stmt = select(City).where(
        City.city_name == city_name,
        City.country_code == country_code
    )
    city = session.scalar(stmt)

    if not city:
        city = City(city_name=city_name, country_code=country_code)
        session.add(city)
        session.flush()  # Get city_id immediately
        logger.debug(f"Created new city: {city_name} in {country_code}")

    return city


def get_or_create_venue(session: Session, venue_name: str, city_id: int) -> Venue:
    """Get existing venue or create new one"""
    stmt = select(Venue).where(
        Venue.venue_name == venue_name,
        Venue.city_id == city_id
    )
    venue = session.scalar(stmt)

    if not venue:
        venue = Venue(venue_name=venue_name, city_id=city_id)
        session.add(venue)
        session.flush()  # Get venue_id immediately
        logger.debug(f"Created new venue: {venue_name}")

    return venue


def parse_date(date_string: str) -> Optional[datetime.date]:
    """Parse date from DD-MM-YYYY format"""
    try:
        return datetime.strptime(date_string, "%d-%m-%Y").date()
    except ValueError as e:
        logger.warning(f"Invalid date format '{date_string}': {e}")
        return None


def process_concert(session: Session, concert_data: Dict[str, Any], stats: Dict[str, int]) -> bool:
    """Process a single concert record"""
    try:
        # Extract nested data
        artist_data = concert_data.get('artist')
        venue_data = concert_data.get('venue')
        city_data = venue_data.get('city') if venue_data else None
        country_data = city_data.get('country') if city_data else None

        # Validate required fields
        if not all([artist_data, venue_data, city_data, country_data]):
            logger.warning(f"Missing required data for concert {concert_data.get('id')}")
            stats["skipped"] += 1
            return False

        concert_id = concert_data.get('id')
        event_date_str = concert_data.get('eventDate')
        concert_date = parse_date(event_date_str)

        if not concert_date:
            logger.warning(f"Invalid date for concert {concert_id}")
            stats["skipped"] += 1
            return False

        # Check if concert already exists
        stmt = select(Concert).where(Concert.concert_id == concert_id)
        if session.scalar(stmt):
            logger.debug(f"Concert {concert_id} already exists, skipping")
            stats["skipped"] += 1
            return False

        # Get or create related entities
        artist = get_or_create_artist(
            session,
            artist_data['mbid'],
            artist_data['name']
        )

        country = get_or_create_country(
            session,
            country_data['code'],
            country_data['name']
        )

        city = get_or_create_city(
            session,
            city_data['name'],
            country_data['code']
        )

        venue = get_or_create_venue(
            session,
            venue_data['name'],
            city.city_id
        )

        # Create concert
        tour_data = concert_data.get('tour')
        tour_name = tour_data.get('name') if tour_data else None

        concert = Concert(
            concert_id=concert_id,
            artist_mbid=artist.artist_mbid,
            venue_id=venue.venue_id,
            concert_date=concert_date,
            tour_name=tour_name
        )
        session.add(concert)

        # Process setlist items
        sets_data = concert_data.get('sets', {}).get('set', [])
        song_position = 1

        for set_data in sets_data:
            songs_in_set = set_data.get('song', [])
            for song in songs_in_set:
                song_name = song.get('name')
                if song_name:
                    setlist_item = SetlistItem(
                        concert_id=concert_id,
                        song_name=song_name,
                        position_in_set=song_position,
                        is_cover='cover' in song
                    )
                    session.add(setlist_item)
                    stats["songs"] += 1
                    song_position += 1

        stats["concerts"] += 1
        return True

    except Exception as e:
        logger.error(f"Error processing concert {concert_data.get('id')}: {e}")
        stats["skipped"] += 1
        return False


def process_data(concert_list: list) -> None:
    """Process all concerts and load into database"""
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)

    stats = {"concerts": 0, "songs": 0, "skipped": 0}
    total_concerts = len(concert_list)

    logger.info(f"Found {total_concerts} concerts in JSON file. Starting upload to database...")

    with SessionLocal() as session:
        try:
            for index, concert_data in enumerate(concert_list):
                success = process_concert(session, concert_data, stats)

                # Commit in batches of 50 for better performance
                if (index + 1) % 50 == 0:
                    try:
                        session.commit()
                        logger.info(f"Processed {index + 1} / {total_concerts} concerts...")
                    except SQLAlchemyError as e:
                        logger.error(f"Commit error at batch {index + 1}: {e}")
                        session.rollback()

            # Final commit
            session.commit()
            logger.info("Final commit completed successfully")

        except KeyboardInterrupt:
            logger.warning("Process interrupted by user. Rolling back current transaction...")
            session.rollback()
        except Exception as e:
            logger.exception(f"Critical error during data processing: {e}")
            session.rollback()
        finally:
            logger.info("\n--- Upload completed ---")
            logger.info(f"Successfully imported: {stats['concerts']} concerts")
            logger.info(f"Processed songs: {stats['songs']}")
            logger.info(f"Skipped due to errors/duplicates: {stats['skipped']}")


def main():
    """Main entry point"""
    JSON_FILE_NAME = "all_setlists_filtered.json"

    logger.info("=== Starting data load process ===")

    raw_data = load_data_from_json(JSON_FILE_NAME)
    if raw_data:
        process_data(raw_data)
    else:
        logger.error("Failed to load data from JSON file")


if __name__ == "__main__":
    main()

