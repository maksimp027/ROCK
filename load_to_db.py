import json
import pg8000.dbapi as db  # <-- Змінено: імпортуємо pg8000
import sys
import os

# Примітки про кодування (os.environ) нам більше не потрібні,
# оскільки pg8000 є чистим Python.

# --- НАЛАШТУВАННЯ БАЗИ ДАНИХ ---
# !!! Змініть 'your_password' на ваш справжній пароль !!!
DB_CONFIG = {
    "database": "postgres",  # <-- ПРАВИЛЬНО
    "user": "postgres",
    "password": "123", # Не забудьте свій пароль
    "host": "localhost",
    "port": 5432
}


# --------------------------------

def get_db_connection():
    try:
        # --- Новий підхід: використовуємо pg8000 ---
        # Передаємо параметри як іменовані аргументи
        conn = db.connect(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"]
        )
        return conn

    except (Exception, db.Error) as e:  # <-- Змінено: відловлюємо помилки pg8000
        print(f"ПОМИЛКА: Не можу підключитися до PostgreSQL.")
        print(f"Перевірте, чи запущений сервер і чи правильні дані в DB_CONFIG.")
        print(f"Деталі: {e}")
        return None


def load_data_from_json(filename):
    if not os.path.exists(filename):
        print(f"ПОМИЛКА: Файл '{filename}' не знайдено.")
        print("Спочатку запустіть 'make_data.py'!")
        return None

    try:
        with open(filename, "r", encoding="utf-8") as f:
            print(f"Читаю файл '{filename}'...")
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        print(f"ПОМИЛКА: Файл '{filename}' пошкоджений або порожній.")
        return None
    except Exception as e:
        print(f"Невідома помилка при читанні файлу: {e}")
        return None


def process_data(concert_list):
    conn = get_db_connection()
    if conn is None:
        print("Не вдалося підключитися до БД. Завантаження скасовано.")
        return

    cur = conn.cursor()
    stats = {"concerts": 0, "songs": 0, "skipped": 0}
    total_concerts = len(concert_list)

    print(f"Знайдено {total_concerts} концертів у .json файлі. Починаю завантаження в SQL...")

    for index, concert_data in enumerate(concert_list):
        try:
            artist_data = concert_data.get('artist')
            venue_data = concert_data.get('venue')
            city_data = venue_data.get('city') if venue_data else None
            country_data = city_data.get('country') if city_data else None

            if not all([artist_data, venue_data, city_data, country_data]):
                stats["skipped"] += 1
                continue

            tour_data = concert_data.get('tour')
            sets_data = concert_data.get('sets', {}).get('set', [])

            # Artist
            cur.execute(
                "INSERT INTO Artists (artist_mbid, artist_name) VALUES (%s, %s) ON CONFLICT (artist_mbid) DO NOTHING;",
                (artist_data['mbid'], artist_data['name'])
            )

            # Country
            cur.execute(
                "INSERT INTO Countries (country_code, country_name) VALUES (%s, %s) ON CONFLICT (country_code) DO NOTHING;",
                (country_data['code'], country_data['name'])
            )

            # City (Get ID)
            # pg8000 (як і psycopg2) підтримує RETURNING
            cur.execute(
                "INSERT INTO Cities (city_name, country_code) VALUES (%s, %s) ON CONFLICT (city_name, country_code) DO NOTHING RETURNING city_id;",
                (city_data['name'], country_data['code'])
            )
            city_id_row = cur.fetchone()

            if city_id_row:
                city_id = city_id_row[0]
            else:
                cur.execute("SELECT city_id FROM Cities WHERE city_name = %s AND country_code = %s;",
                            (city_data['name'], country_data['code']))
                city_id = cur.fetchone()[0]

            # Venue (Get ID)
            cur.execute(
                "INSERT INTO Venues (venue_name, city_id) VALUES (%s, %s) ON CONFLICT (venue_name, city_id) DO NOTHING RETURNING venue_id;",
                (venue_data['name'], city_id)
            )
            venue_id_row = cur.fetchone()

            if venue_id_row:
                venue_id = venue_id_row[0]
            else:
                cur.execute("SELECT venue_id FROM Venues WHERE venue_name = %s AND city_id = %s;",
                            (venue_data['name'], city_id))
                venue_id = cur.fetchone()[0]

            # Concert
            tour_name = tour_data.get('name') if tour_data else None
            concert_id = concert_data['id']

            cur.execute(
                """
                INSERT INTO Concerts (concert_id, artist_mbid, venue_id, concert_date, tour_name)
                VALUES (%s, %s, %s, TO_DATE(%s, 'DD-MM-YYYY'), %s) ON CONFLICT (concert_id) DO NOTHING;
                """,
                (concert_id, artist_data['mbid'], venue_id, concert_data['eventDate'], tour_name)
            )

            # SetlistItems
            if sets_data:
                song_position = 1
                for s in sets_data:
                    songs_in_set = s.get('song', [])
                    for song in songs_in_set:
                        if song.get('name'):
                            cur.execute(
                                """
                                INSERT INTO SetlistItems (concert_id, song_name, position_in_set, is_cover)
                                VALUES (%s, %s, %s, %s) ON CONFLICT (concert_id, position_in_set) DO NOTHING;
                                """,
                                (concert_id, song['name'], song_position, 'cover' in song)
                            )
                            stats["songs"] += 1
                            song_position += 1

            conn.commit()
            stats["concerts"] += 1

            if (index + 1) % 100 == 0:
                print(f"Оброблено {index + 1} / {total_concerts} концертів...")

        except (Exception, db.Error) as e:  # <-- Змінено: відловлюємо помилки pg8000
            print(f"\nПОМИЛКА при обробці концерту {concert_data.get('id')}: {e}")
            if conn:
                conn.rollback()
            stats["skipped"] += 1

    if conn:
        cur.close()
        conn.close()

    print("\n--- Завантаження завершено ---")
    print(f"Успішно імпортовано/оновлено: {stats['concerts']} концертів")
    print(f"Пропущено через помилки/відсутність даних: {stats['skipped']}")
    print(f"Оброблено пісень: {stats['songs']}")


if __name__ == "__main__":
    JSON_FILE_NAME = "all_setlists_filtered.json"

    raw_data = load_data_from_json(JSON_FILE_NAME)
    if raw_data:
        process_data(raw_data)