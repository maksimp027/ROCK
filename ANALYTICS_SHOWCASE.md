# Engineering Showcase: Advanced ETL & Analytical Patterns

This document explores the technical depth behind the Rock Scene Europe data pipeline, focusing on ETL robustness, type-safe ORM modeling, and complex analytical aggregations.

## 1. The ETL Challenge (Setlist.fm Integration)

External music APIs are inherently noisy: records can be incomplete, paginated inconsistently, delayed by rate limits, or duplicated across pulls. In Rock Scene Europe, `make_data.py` and `load_to_db.py` are designed to absorb that real-world chaos without polluting downstream analytics.

**Rate limiting and fault tolerance**

- The ingestion layer explicitly handles HTTP `429` responses, backs off, and retries.
- Network/transient failures are isolated from the full run, allowing partial progress instead of all-or-nothing failure modes.
- Long-running collections use checkpoint-friendly behavior (save progress even on interruption).

**Normalization strategy for dirty records**

- Nested source entities (artist, country, city, venue, setlist songs) are flattened into relational entities.
- Location hierarchy is standardized as `Country -> City -> Venue`, reducing ambiguity in geographic analytics.
- Missing fields are validated and filtered using schema-first checks so malformed payloads are rejected early.

**Idempotency through check-then-write upsert semantics**

The loader implements deterministic `get_or_create` patterns for reference entities (Artist, Country, City, Venue), then inserts concert facts and setlist rows only when absent.

- This behaves like an application-level upsert for data sources without strong natural keys.
- Re-running the loader is safe: duplicates are skipped, and referential integrity remains consistent.
- The result is repeatable ingestion, a core requirement for operational data pipelines.

**Why ELT over strict ETL?**

Although some transformations are done pre-load, the architecture follows an ELT-oriented principle: persist normalized, relationally complete data first, then run heavy analytical shaping in SQL/API/reporting layers. This keeps ingestion resilient and moves expensive business logic closer to the database engine.

## 2. Modern Data Modeling (SQLAlchemy 2.0)

The data model uses SQLAlchemy 2.0 typed ORM patterns (`Mapped`, `mapped_column`) to make schema intent explicit and tooling-friendly.

**Typed ORM benefits**

- Static typing improves maintainability and refactor safety in a multi-module backend.
- Relationship graphs (`Artist -> Concert -> SetlistItem`, `Country -> City -> Venue -> Concert`) are encoded declaratively.
- Constraints (`ForeignKey`, `UniqueConstraint`) enforce correctness at the storage layer, not only in application logic.

**Asynchronous gateway behavior**

- FastAPI endpoints consume `AsyncSession` dependencies for non-blocking query execution.
- Async connection pooling (`asyncpg` + SQLAlchemy engine/session factory) supports concurrent analytical reads efficiently.
- Lifespan hooks initialize and close database resources predictably, preventing connection leaks under load.

**Schema decoupling: API contracts vs persistence model**

- `api_schemas.py` (Pydantic) defines external contracts and validation boundaries.
- `models.py` (SQLAlchemy) represents relational state and joins.
- This separation prevents transport-level changes from destabilizing persistence concerns, and vice versa.

## 3. Analytical SQL & Window Functions

A typical advanced scenario is **Artist Tour Density**: measuring how concentrated an artist's touring activity is across countries over time. This is stronger than a simple count because it highlights distribution shape, ranking, and concentration dynamics.

### Hypothetical Analytical Goal

For each artist-year-country tuple:

1. Count shows in that country.
2. Compute total yearly shows for that artist.
3. Derive density ratio (`country_shows / yearly_shows`).
4. Rank countries by share within each artist-year.
5. Compare concentration against global average via window aggregates.

### SQL Logic (PostgreSQL Window Functions)

```sql
WITH country_activity AS (
    SELECT
        c.artist_mbid,
        a.artist_name,
        EXTRACT(YEAR FROM c.concert_date)::INT AS year,
        co.country_code,
        co.country_name,
        COUNT(*)::INT AS country_shows
    FROM concerts c
    JOIN artists a ON a.artist_mbid = c.artist_mbid
    JOIN venues v ON v.venue_id = c.venue_id
    JOIN cities ci ON ci.city_id = v.city_id
    JOIN countries co ON co.country_code = ci.country_code
    GROUP BY c.artist_mbid, a.artist_name, year, co.country_code, co.country_name
),
ranked_density AS (
    SELECT
        artist_mbid,
        artist_name,
        year,
        country_code,
        country_name,
        country_shows,
        SUM(country_shows) OVER (PARTITION BY artist_mbid, year) AS yearly_shows,
        country_shows::NUMERIC
            / NULLIF(SUM(country_shows) OVER (PARTITION BY artist_mbid, year), 0) AS density_ratio,
        DENSE_RANK() OVER (
            PARTITION BY artist_mbid, year
            ORDER BY country_shows DESC, country_name ASC
        ) AS country_rank,
        AVG(country_shows) OVER (PARTITION BY year, country_code) AS avg_country_load_in_year
    FROM country_activity
)
SELECT
    artist_name,
    year,
    country_name,
    country_shows,
    yearly_shows,
    ROUND(density_ratio, 4) AS density_ratio,
    country_rank,
    ROUND(avg_country_load_in_year, 2) AS avg_country_load_in_year
FROM ranked_density
WHERE year >= 2015
ORDER BY year DESC, artist_name ASC, country_rank ASC;
```

### Engineering Value

- Window functions avoid repeated subqueries and keep analytical intent explicit.
- The query can back dashboard endpoints, forecasting features, or executive packs without changing source facts.
- This pattern scales naturally into materialized views or scheduled marts when workload grows.

## 4. Automated Reporting Engine

The reporting component (`analytics.py`, equivalent to a dedicated reporting engine module) operationalizes insights for non-technical stakeholders.

**Execution flow**

1. Run SQL aggregations against PostgreSQL.
2. Load result sets into Pandas DataFrames.
3. Build visual analytics with Seaborn/Matplotlib (heatmaps, distributions, trend regressions).
4. Export all figures into a single PDF report (`PdfPages`) for executive consumption.

**Why this design works**

- SQL handles grouping/filtering at source, minimizing in-memory post-processing.
- Pandas provides deterministic shaping for chart-ready datasets.
- Seaborn enforces visually consistent statistical plots suitable for business reviews.
- Automated PDF generation turns analytics into a repeatable operational artifact, not an ad-hoc notebook exercise.

**Operational outcome**

The platform closes the loop from unstable external API payloads to reproducible BI deliverables: ingestion resilience, relational integrity, async analytical serving, and stakeholder-ready reporting in one cohesive architecture.

