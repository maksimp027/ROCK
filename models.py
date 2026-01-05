from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Date, Integer, Boolean, UniqueConstraint
from datetime import date
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class Artist(Base):
    __tablename__ = "artists"

    artist_mbid: Mapped[str] = mapped_column(String, primary_key=True)
    artist_name: Mapped[str] = mapped_column(String, nullable=False)

    concerts: Mapped[List["Concert"]] = relationship(back_populates="artist", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Artist(mbid={self.artist_mbid}, name={self.artist_name})>"


class Country(Base):
    __tablename__ = "countries"

    country_code: Mapped[str] = mapped_column(String(2), primary_key=True)
    country_name: Mapped[str] = mapped_column(String, nullable=False)

    cities: Mapped[List["City"]] = relationship(back_populates="country", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Country(code={self.country_code}, name={self.country_name})>"


class City(Base):
    __tablename__ = "cities"

    city_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city_name: Mapped[str] = mapped_column(String, nullable=False)
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.country_code"), nullable=False)

    country: Mapped["Country"] = relationship(back_populates="cities")
    venues: Mapped[List["Venue"]] = relationship(back_populates="city", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("city_name", "country_code", name="uq_city_country"),
    )

    def __repr__(self) -> str:
        return f"<City(id={self.city_id}, name={self.city_name}, country={self.country_code})>"


class Venue(Base):
    __tablename__ = "venues"

    venue_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venue_name: Mapped[str] = mapped_column(String, nullable=False)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.city_id"), nullable=False)

    city: Mapped["City"] = relationship(back_populates="venues")
    concerts: Mapped[List["Concert"]] = relationship(back_populates="venue", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("venue_name", "city_id", name="uq_venue_city"),
    )

    def __repr__(self) -> str:
        return f"<Venue(id={self.venue_id}, name={self.venue_name}, city_id={self.city_id})>"


class Concert(Base):
    __tablename__ = "concerts"

    concert_id: Mapped[str] = mapped_column(String, primary_key=True)
    artist_mbid: Mapped[str] = mapped_column(ForeignKey("artists.artist_mbid"), nullable=False)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.venue_id"), nullable=False)
    concert_date: Mapped[date] = mapped_column(Date, nullable=False)
    tour_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    artist: Mapped["Artist"] = relationship(back_populates="concerts")
    venue: Mapped["Venue"] = relationship(back_populates="concerts")
    setlist_items: Mapped[List["SetlistItem"]] = relationship(back_populates="concert", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Concert(id={self.concert_id}, date={self.concert_date}, artist={self.artist_mbid})>"


class SetlistItem(Base):
    __tablename__ = "setlistitems"

    item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    concert_id: Mapped[str] = mapped_column(ForeignKey("concerts.concert_id"), nullable=False)
    song_name: Mapped[str] = mapped_column(String, nullable=False)
    position_in_set: Mapped[int] = mapped_column(Integer, nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    concert: Mapped["Concert"] = relationship(back_populates="setlist_items")

    __table_args__ = (
        UniqueConstraint("concert_id", "position_in_set", name="uq_concert_position"),
    )

    def __repr__(self) -> str:
        return f"<SetlistItem(id={self.item_id}, concert={self.concert_id}, song={self.song_name}, pos={self.position_in_set})>"
