# Rock Scene Europe: Live Music Analytics Platform

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC2927?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=for-the-badge)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

An End-to-End Data Engineering pipeline and Analytics API that transforms raw, chaotic concert data into actionable business intelligence for the live music industry.

## Live Analytics Preview

Experience the platform's visual power without setting up the environment.

**Open Live Interactive Demo:** [https://maksimp027.github.io/ROCK/preview.html](https://maksimp027.github.io/ROCK/preview.html)

> Orange-Purple Neon dashboard aesthetic, static portfolio-ready dataset, and zero backend setup required.

### For Technical Reviewers

Read the engineering deep-dive in [`ANALYTICS_SHOWCASE.md`](ANALYTICS_SHOWCASE.md) for ETL architecture decisions, SQLAlchemy 2.0 modeling strategy, and advanced analytical query patterns.

## The Business Value

Rock Scene Europe exists to convert noisy external event data into decision-ready insights for:

- **Tour Promoters** planning cost-efficient, high-demand routes.
- **Booking Agencies** comparing market saturation across cities and countries.
- **Music Label Analysts** tracking artist momentum, setlist behavior, and growth trends over time.

### 1) Tour Logistics Optimization

The platform analyzes concert density by country, city, month, and year to help teams build better European tour plans, reduce routing friction, and prioritize high-activity markets.

### 2) Trend & Setlist Analysis

Historical data is transformed into artist-level and song-level analytics, enabling teams to detect genre/artist trajectory shifts and forecast ticket sales potential with evidence, not assumptions.

### 3) Automated Executive Reporting

Using `analytics.py` and Seaborn, stakeholders can generate presentation-ready PDF reports with a single operational trigger, accelerating weekly and quarterly reporting cycles.

## Platform Capabilities

- **Production-style ETL flow** from Setlist.fm with validation, filtering, deduplication, and normalization.
- **Async analytical API** built on FastAPI + SQLAlchemy 2.0 for scalable read workloads.
- **Typed schemas** powered by Pydantic v2 for contract reliability across ETL and API layers.
- **Dashboard-ready endpoints** for top artists, top songs, geography distribution, yearly trends, and heatmaps.
- **Publication-quality analytics** using Pandas, Matplotlib, and Seaborn.

## The Data Architecture

### Phase 1: ETL & Data Cleansing (`make_data.py`, `load_to_db.py`)

- Extracts setlist and concert metadata from Setlist.fm API.
- Handles external API instability and rate limits.
- Validates incoming payloads with Pydantic models.
- Deduplicates artists, countries, cities, and venues.
- Normalizes dirty nested JSON into relational entities.

### Phase 2: Storage (PostgreSQL + SQLAlchemy 2.0 ORM)

- Stores cleaned data in PostgreSQL with strict schema relationships.
- Uses SQLAlchemy 2.0 typed models (`Mapped`, `mapped_column`).
- Enforces referential integrity for analytics-grade consistency.

### Phase 3: The API Gate (`api_main.py`, `api_crud.py`, `api_database.py`)

- Exposes analytical endpoints through FastAPI.
- Uses async sessions and dependency-injected database access.
- Serves aggregation-heavy queries for BI and dashboard consumption.

### Phase 4: Reporting Engine (`analytics.py`)

- Executes SQL-backed analytics with Pandas.
- Builds executive charts with Seaborn and Matplotlib.
- Exports print-ready PDF reports for business stakeholders.

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend API | FastAPI, Uvicorn, Lifespan management |
| Data Access | SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL |
| Validation & Settings | Pydantic v2, Pydantic Settings |
| Analytics | Pandas, Matplotlib, Seaborn |
| Frontend | Tailwind CSS, Chart.js |
| DevOps | Docker, Docker Compose |

## Quick Start

### 1) Environment Setup

Create environment variables (or copy from `.env.example` if present) and make sure these keys exist:

```env
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rock_concerts
SETLIST_API_KEY=your_setlist_fm_api_key
```

### 2) Run with Docker Compose (recommended)

```bash
docker-compose up --build
```

After startup:

- API: `http://localhost:8001`
- Swagger UI: `http://localhost:8001/docs`
- PostgreSQL: `localhost:5432`

<<<<<<< HEAD
## Acknowledgments
=======
### 3) Run ETL and Reporting Scripts

```bash
python make_data.py
python load_to_db.py
python analytics.py
```

### 4) Run API Locally (without Docker)

```bash
uvicorn api_main:app --host 0.0.0.0 --port 8001 --reload
```
>>>>>>> d9d395e (feat: finalize portfolio release with live preview and technical showcase)

## API Surface (Analytics Endpoints)

Base path:

<<<<<<< HEAD
**Built with for the rock community by [maksimp027](https://github.com/maksimp027)**
=======
```text
/api/v1
```

Key endpoints:

- `GET /stats/top-artists`
- `GET /stats/top-songs`
- `GET /stats/concerts-by-year`
- `GET /stats/geography`
- `GET /stats/cities`
- `GET /stats/heatmap`
- `GET /artists/{artist_mbid}`
- `GET /concerts/{concert_id}`

## Repository Layout

```text
ROCK/
├── api_main.py        # FastAPI entrypoint and route layer
├── api_crud.py        # Analytical query logic
├── api_database.py    # Async DB session/pool wiring
├── api_schemas.py     # Pydantic DTOs and external payload schemas
├── models.py          # SQLAlchemy ORM models
├── make_data.py       # External API extraction + validation
├── load_to_db.py      # ETL loading and normalization into PostgreSQL
├── analytics.py       # PDF analytics/reporting engine
├── index.html         # Dashboard UI
├── docker-compose.yml
└── Dockerfile
```

## Why This Project Matters

Most live-music data sources are incomplete, inconsistent, and hard to operationalize. Rock Scene Europe demonstrates a practical, business-first approach to Data Engineering:

- turn fragmented third-party API payloads into clean relational datasets,
- expose trusted metrics through a robust analytics API,
- and automate insight delivery through stakeholder-friendly reporting artifacts.

It is built as a portfolio-grade platform to showcase production-minded engineering across ETL, data modeling, API architecture, and analytics delivery.
>>>>>>> d9d395e (feat: finalize portfolio release with live preview and technical showcase)
