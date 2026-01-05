from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List, Optional

model_config = ConfigDict(from_attributes=True)


# --- Base Models ---

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


# --- Response Models ---

class ConcertBasicInfo(BaseModel):
    model_config = model_config
    concert_id: str
    concert_date: date
    tour_name: Optional[str] = None
    venue_name: str
    city_name: str
    country_name: str


class ConcertDetail(BaseModel):
    model_config = model_config
    concert_id: str
    concert_date: date
    tour_name: Optional[str] = None
    artist: ArtistBase
    venue: VenueBase
    setlist: List[SetlistItemBase] = []


class ArtistDetail(BaseModel):
    model_config = model_config
    artist: ArtistBase
    concerts: List[ConcertBasicInfo] = []


# --- Statistics ---

class StatTopItem(BaseModel):
    model_config = model_config
    name: str
    count: int


class StatYearItem(BaseModel):
    model_config = model_config
    year: int
    count: int


class StatGeoItem(BaseModel):
    model_config = model_config
    name: str
    count: int


class StatHeatmapItem(BaseModel):
    model_config = model_config
    year: int
    month: int
    count: int


# --- External API Models (moved from make_data.py) ---

class ExternalArtist(BaseModel):
    mbid: str
    name: str


class ExternalCountry(BaseModel):
    code: str
    name: str


class ExternalCity(BaseModel):
    name: str
    country: ExternalCountry


class ExternalVenue(BaseModel):
    name: str
    city: ExternalCity


class ExternalSong(BaseModel):
    name: str


class ExternalSet(BaseModel):
    song: List[ExternalSong] = []


class ExternalSets(BaseModel):
    set: List[ExternalSet] = []


class ExternalSetlist(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    eventDate: str
    artist: ExternalArtist
    venue: ExternalVenue
    sets: Optional[ExternalSets] = None
    tour: Optional[dict] = None
