import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from api_database import get_db_pool, close_db_pool, get_db
from api_schemas import (
    StatTopItem, StatYearItem, ArtistDetail, ConcertDetail,
    StatGeoItem, StatHeatmapItem
)
import api_crud as crud

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server. Initializing DB pool...")
    await get_db_pool()
    yield
    logger.info("Shutting down server. Closing resources...")
    await close_db_pool()

app = FastAPI(
    title="Rock Concerts API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---

@app.get("/")
async def get_root():
    return {"message": "Rock API is working!"}

@app.get("/api/v1/stats/top-artists", response_model=List[StatTopItem])
async def get_top_artists(db: AsyncSession = Depends(get_db)):
    return await crud.get_stats_top_artists(db)

@app.get("/api/v1/stats/top-songs", response_model=List[StatTopItem])
async def get_top_songs():
    return await crud.get_stats_top_songs()

@app.get("/api/v1/stats/concerts-by-year", response_model=List[StatYearItem])
async def get_concerts_by_year():
    return await crud.get_stats_concerts_by_year()

@app.get("/api/v1/stats/geography", response_model=List[StatGeoItem])
async def get_geography():
    return await crud.get_stats_geography()

@app.get("/api/v1/stats/cities", response_model=List[StatGeoItem])
async def get_cities():
    return await crud.get_stats_cities()

@app.get("/api/v1/stats/heatmap", response_model=List[StatHeatmapItem])
async def get_heatmap():
    return await crud.get_stats_heatmap()

@app.get("/api/v1/artists/{artist_mbid}", response_model=ArtistDetail)
async def get_artist_by_mbid(artist_mbid: str):
    data = await crud.get_artist_details(artist_mbid)
    if not data:
        raise HTTPException(404, "Artist not found")
    return data

@app.get("/api/v1/concerts/{concert_id}", response_model=ConcertDetail)
async def get_concert_by_id(concert_id: str):
    data = await crud.get_concert_details(concert_id)
    if not data:
        raise HTTPException(404, "Concert not found")
    return data

if __name__ == "__main__":
    uvicorn.run("api_main:app", host="0.0.0.0", port=8001, reload=True)
