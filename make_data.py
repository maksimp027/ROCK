import requests
import time
import json
import logging
from typing import List
from pydantic import ValidationError
from config import settings
from api_schemas import ExternalSetlist

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_and_filter(raw_setlists: list, european_filter: set) -> list:
    """Validate raw data through Pydantic and filter by countries"""
    valid_data = []
    for item in raw_setlists:
        try:
            obj = ExternalSetlist.model_validate(item)
            if obj.venue.city.country.code in european_filter:
                valid_data.append(obj.model_dump())
        except ValidationError as e:
            logger.debug(f"Object {item.get('id')} failed validation: {e.json()}")
            continue
    return valid_data

def fetch_artist_year_data(artist: str, year: int, european_filter: set):
    """Fetch data from API with pagination and validation"""
    all_filtered = []
    current_page = 1
    total_pages = 1

    search_url = "https://api.setlist.fm/rest/1.0/search/setlists"
    headers = {
        "x-api-key": settings.setlist_api_key,
        "Accept": "application/json"
    }

    while current_page <= total_pages:
        params = {"artistName": artist, "year": year, "p": current_page}
        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=10)

            if response.status_code == 429:
                logger.warning(f"Rate limit hit. Sleeping 10s... [{artist}, {year}]")
                time.sleep(10)
                continue

            if response.status_code != 200:
                logger.error(f"Error {response.status_code} for {artist} on page {current_page}")
                break

            data = response.json()

            if current_page == 1:
                total_items = data.get('total', 0)
                if total_items == 0:
                    break
                items_per_page = data.get('itemsPerPage', 20)
                total_pages = (total_items + items_per_page - 1) // items_per_page
                logger.info(f"Found {total_items} shows: {artist} ({year})")

            raw_page_data = data.get('setlist', [])
            filtered_page = validate_and_filter(raw_page_data, european_filter)
            all_filtered.extend(filtered_page)

            current_page += 1
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            break

    return all_filtered

def save_to_json(data: list, filename: str):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(data)} objects to {filename}")
    except Exception:
        logger.exception("Error saving JSON")

def main():
    target_artists = ["Metallica", "Korn", "Slipknot", "Rammstein", "System of a Down"]
    target_years = list(range(2020, 2025))
    eu_countries = {"DE", "PL", "FR", "IT", "ES", "GB", "NL", "BE", "UA"}

    collected_data = []
    output_file = "all_setlists_filtered.json"

    logger.info("--- START WORK ---")
    try:
        for artist in target_artists:
            for year in target_years:
                results = fetch_artist_year_data(artist, year, eu_countries)
                collected_data.extend(results)
    except KeyboardInterrupt:
        logger.warning("Collection interrupted. Saving progress...")
    finally:
        save_to_json(collected_data, output_file)

if __name__ == "__main__":
    main()
