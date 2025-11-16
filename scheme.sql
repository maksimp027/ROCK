-- Таблиця артистів
CREATE TABLE Artists (
    artist_mbid TEXT PRIMARY KEY, -- Ключ - це MBID з API
    artist_name TEXT NOT NULL
);

-- Таблиця країн
CREATE TABLE Countries (
    country_code TEXT PRIMARY KEY, -- 'DE', 'PL', 'UA'
    country_name TEXT NOT NULL
);

-- Таблиця міст
CREATE TABLE Cities (
    city_id SERIAL PRIMARY KEY, -- Ми генеруємо свій ID
    city_name TEXT NOT NULL,
    country_code TEXT REFERENCES Countries(country_code),
    UNIQUE(city_name, country_code)
);

-- Таблиця місць проведення
CREATE TABLE Venues (
    venue_id SERIAL PRIMARY KEY, -- Ми генеруємо свій ID
    venue_name TEXT NOT NULL,
    city_id INTEGER REFERENCES Cities(city_id),
    UNIQUE(venue_name, city_id)
);

-- Головна таблиця концертів
CREATE TABLE Concerts (
    concert_id TEXT PRIMARY KEY, -- Ключ - це ID концерту з API
    artist_mbid TEXT REFERENCES Artists(artist_mbid),
    venue_id INTEGER REFERENCES Venues(venue_id),
    concert_date DATE NOT NULL,
    tour_name TEXT
);

-- Таблиця з піснями в сетлістах
CREATE TABLE SetlistItems (
    item_id SERIAL PRIMARY KEY,
    concert_id TEXT REFERENCES Concerts(concert_id),
    song_name TEXT NOT NULL,
    position_in_set INTEGER,
    is_cover BOOLEAN DEFAULT false,
    UNIQUE(concert_id, position_in_set)
);