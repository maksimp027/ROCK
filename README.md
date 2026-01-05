# Rock Scene Europe | Live Analytics Platform

> **Data-driven insights for the European live music industry**  
> A full-stack analytics platform that transforms raw concert data into actionable intelligence through automated ETL pipelines, real-time APIs, and visual reporting.

---

## Project Overview

**Rock Scene Europe** is a production-ready analytics system built for music industry professionals, event organizers, and data enthusiasts. It provides:

- **Comprehensive concert database** covering 2000-2024 across major European markets
- **Real-time REST API** with async PostgreSQL queries for instant insights
- **Interactive web dashboard** with responsive visualizations
- **Automated PDF reports** featuring advanced statistical analysis

---

## Key Features

### Robust ETL Pipeline
- **Automated data collection** from Setlist.fm API with rate limiting and error handling
- **Pydantic v2 validation** ensuring data integrity at ingestion time
- **SQLAlchemy 2.0 ORM** with modern `Mapped` annotations for type-safe database operations
- **Intelligent deduplication** using "get-or-create" patterns for artists, venues, and locations

### High-Performance API
- **Async FastAPI backend** with connection pooling for optimal throughput
- **Lifespan management** for graceful startup/shutdown of database connections
- **Complex aggregations** (top artists, geographic distribution, temporal trends)
- **Built-in Swagger UI** at `/docs` for interactive exploration

### Advanced Analytics
- **Seaborn-powered visualizations**: heatmaps, regression plots, and distribution analysis
- **PDF report generation** with publication-quality charts
- **Activity heatmaps** revealing seasonality patterns (2010-2024)
- **Market penetration analysis** across European cities and countries

### Modern Frontend
- **Responsive dashboard** built with Tailwind CSS
- **Real-time Chart.js visualizations** with gradient effects and dark theme
- **KPI cards** displaying live statistics from the API
- **Professional UI/UX** following design system principles

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | FastAPI 0.115+ with async/await, Uvicorn ASGI server |
| **Database** | PostgreSQL 15 with asyncpg driver |
| **ORM** | SQLAlchemy 2.0 (Declarative Base, Mapped annotations) |
| **Validation** | Pydantic v2 with Settings management |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib 3.8+, Seaborn 0.13+ |
| **Frontend** | HTML5, Tailwind CSS 3.x, Chart.js 4.x |
| **DevOps** | Docker, Docker Compose |
| **HTTP Client** | Requests (with retry logic) |

---

## Architecture

```
rock-scene-europe/
├── api_main.py          # FastAPI application with lifespan hooks
├── api_crud.py          # Database queries using SQLAlchemy ORM
├── api_database.py      # Connection pool & session management
├── api_schemas.py       # Pydantic models for request/response validation
├── models.py            # SQLAlchemy ORM models (Artist, Concert, Venue, etc.)
├── load_to_db.py        # ETL script with get-or-create logic
├── make_data.py         # Data collection from Setlist.fm API
├── analytics.py         # Seaborn report generation
├── config.py            # Settings management with Pydantic
├── index.html           # Frontend dashboard
├── docker-compose.yml   # Multi-container orchestration
└── Dockerfile           # API service containerization
```

**Design Principles:**
- **Separation of concerns**: API layer, business logic, and data access are isolated
- **Dependency injection**: Database sessions passed via FastAPI `Depends()`
- **Configuration as code**: Environment variables managed through Pydantic Settings
- **Async by default**: All I/O operations use async/await for concurrency

---

## Quick Start

### Prerequisites
- Docker 24.0+
- Docker Compose 2.20+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/maksimp027/ROCK.git
   cd ROCK
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and Setlist.fm API key
   ```

3. **Launch the platform**
   ```bash
   docker-compose up --build
   ```

4. **Access the services**
   - **Dashboard**: http://localhost:8001 (open `index.html` in browser)
   - **API Documentation**: http://localhost:8001/docs
   - **PostgreSQL**: `localhost:5432`

### Data Population

```bash
# Collect data from Setlist.fm (requires API key in .env)
python make_data.py

# Load data into PostgreSQL
python load_to_db.py

# Generate PDF analytics report
python analytics.py
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8001/api/v1
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/stats/top-artists` | GET | Top 10 artists by concert count |
| `/stats/top-songs` | GET | Top 20 most performed songs |
| `/stats/concerts-by-year` | GET | Annual concert trends |
| `/stats/geography` | GET | Top countries by event volume |
| `/stats/heatmap` | GET | Monthly activity density (2010-2024) |
| `/artists/{mbid}` | GET | Artist details with full concert history |
| `/concerts/{id}` | GET | Concert details with setlist |

### Example Response

```json
GET /api/v1/stats/top-artists

[
  {
    "name": "Metallica",
    "count": 342
  },
  {
    "name": "Rammstein",
    "count": 198
  }
]
```

**Interactive Swagger UI** available at `/docs` for testing all endpoints.

---

## Visualizations

### Live Dashboard
![Dashboard Preview](docs/dashboard-preview.png)
*Real-time analytics with interactive charts and KPI cards*

### PDF Report Sample
![PDF Report](docs/pdf-report-preview.png)
*Professional statistical analysis with Seaborn visualizations*

---

## Database Schema

**Core Tables:**
- `artists` - MusicBrainz ID, name
- `countries` - ISO 3166-1 alpha-2 codes
- `cities` - Name + country reference
- `venues` - Name + city reference
- `concerts` - Event metadata (date, tour, relationships)
- `setlistitems` - Song-level data with position and cover flags

**Relationships:**
- One-to-Many: Country → Cities → Venues → Concerts
- One-to-Many: Artist → Concerts → SetlistItems
- Enforced referential integrity with foreign keys

---

## Environment Variables

Create a `.env` file with the following:

```env
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rock_concerts

SETLIST_FM_API_KEY=your_api_key_here
```

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Setlist.fm API** for comprehensive concert data
- **FastAPI** team for the excellent async framework
- **SQLAlchemy** for the powerful ORM capabilities

---

**Built with for the rock community by [maksimp027](https://github.com/maksimp027)**