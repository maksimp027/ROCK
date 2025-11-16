import requests
import time
import json
import os

# --- ВАШІ НАЛАШТУВАННЯ ---
API_KEY = "Zwdz6Xp0x776Fe5O1JdmRrD9ox_iWfm9SI2z"

# Використовуємо ендпоінт ПОШУКУ
SEARCH_URL = "https://api.setlist.fm/rest/1.0/search/setlists"

# Заголовки (headers) для авторизації
headers = {
    "x-api-key": API_KEY,
    "Accept": "application/json"
}

# 1. Цільові артисти
ARTISTS_TO_FETCH = [
    "Metallica", "Iron Maiden", "Rammstein", "AC/DC", "Slipknot",
    "Foo Fighters", "Muse", "Guns N' Roses", "Green Day",
    "Red Hot Chili Peppers", "Judas Priest", "Slayer", "Tool", "Korn",
    "System of a Down", "Avenged Sevenfold", "Linkin Park",
    "Ozzy Osbourne","Black Sabbath","Scorpions", "Def Leppard",
    "Sabaton", "Volbeat", "Gojira", "Bring Me The Horizon", "Ghost",
    "Nightwish", "Queens of the Stone Age",
    "Placebo", "Die Toten Hosen", "Arctic Monkeys"
]

# 2. Список років
# (Ви можете змінити на range(2000, 2025))
YEARS_TO_FETCH = list(range(2000, 2025))
# Для тесту: [2023, 2024]

# 3. Список країн Європи (для ФІЛЬТРАЦІЇ)
# Використовуємо 'set' для швидкого пошуку (x in set)
EUROPEAN_COUNTRIES_FILTER = {
    "DE", "PL", "FR", "IT", "ES", "GB", "NL", "BE", "SE", "NO",
    "FI", "DK", "CH", "AT", "CZ", "HU", "PT", "IE", "UA", "RO",
    "GR", "BG", "RS", "HR", "SI", "SK", "LT", "LV", "EE", "LU", "IS"
    # Додайте сюди всі коди, які вас цікавлять
}

# Тут ми будемо зберігати ВСІ зібрані дані
all_data = []
output_filename = "all_setlists_filtered.json"

print(f"Починаємо збір даних для {len(ARTISTS_TO_FETCH)} артистів за {len(YEARS_TO_FETCH)} років.")
print(f"Фільтруємо за {len(EUROPEAN_COUNTRIES_FILTER)} країнами Європи.")

try:
    # 3. Зовнішній цикл: Артисти
    for artist in ARTISTS_TO_FETCH:

        # 4. Середній цикл: Роки
        for year in YEARS_TO_FETCH:

            print(f"\n--- Починаю збір: Артист='{artist}', Рік={year} ---")
            current_page = 1
            total_pages = 1  # API оновить це значення
            total_found_for_this_query = 0

            # 5. Внутрішній цикл: Пагінація (гортання сторінок)
            while current_page <= total_pages:

                params = {
                    "artistName": artist,  # <-- Ключова зміна
                    "year": year,
                    "p": current_page  # Номер сторінки
                }

                response = requests.get(SEARCH_URL, headers=headers, params=params)

                if response.status_code == 429:  # 429 = Too Many Requests
                    print("Забагато запитів! Спимо 10 секунд...")
                    time.sleep(10)
                    continue  # Повторюємо спробу для цієї ж сторінки

                if response.status_code != 200:
                    print(
                        f"Помилка {response.status_code} (напр. 404 Not Found) на сторінці {current_page}. Пропускаємо.")
                    break  # Виходимо з циклу пагінації

                data = response.json()

                # Оновлюємо загальну кількість сторінок (лише 1 раз)
                if current_page == 1:
                    total_items = data.get('total', 0)
                    if total_items == 0:
                        print("Результатів (0). Переходимо до наступного року.")
                        break  # Немає концертів для цього артиста/року

                    items_per_page = data.get('itemsPerPage', 20)
                    total_pages = (total_items + items_per_page - 1) // items_per_page
                    print(f"Знайдено {total_items} світових концертів, {total_pages} сторінок.")

                setlists_on_page = data.get('setlist', [])
                if not setlists_on_page:
                    print("На цій сторінці немає даних. Завершуємо.")
                    break

                # 6. ФІЛЬТРАЦІЯ в Python
                filtered_setlists = []
                for setlist in setlists_on_page:
                    try:
                        # Безпечно отримуємо код країни
                        country_code = setlist['venue']['city']['country']['code']

                        # Перевіряємо, чи входить країна в наш список
                        if country_code in EUROPEAN_COUNTRIES_FILTER:
                            filtered_setlists.append(setlist)
                    except (KeyError, TypeError):
                        # Пропускаємо сетліст, якщо у нього неповні дані
                        # (немає 'venue', 'city' або 'country')
                        continue

                # Додаємо лише відфільтровані дані
                if filtered_setlists:
                    all_data.extend(filtered_setlists)
                    total_found_for_this_query += len(filtered_setlists)

                print(f"Сторінка {current_page}/{total_pages} завантажена. "
                      f"Знайдено європейських: {len(filtered_setlists)}. "
                      f"Всього зібрано: {len(all_data)}")

                current_page += 1

                # !!! КРИТИЧНО ВАЖЛИВО !!!
                # Пауза 1 секунда між КОЖНИМ запитом
                time.sleep(1)

except KeyboardInterrupt:
    print("\n! Збір перервано користувачем (Ctrl+C). Зберігаємо те, що встигли зібрати...")
except Exception as e:
    print(f"\n! Сталася критична помилка: {e}. Зберігаємо те, що встигли зібрати...")

finally:
    # 7. Зберігаємо ВСЕ у файл
    print(f"\n--- Збір завершено ---")
    print(f"Всього зібрано {len(all_data)} сетлістів.")
    print(f"Зберігаємо у файл '{output_filename}'...")

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print("Готово.")
    except Exception as e:
        print(f"Помилка при збереженні файлу: {e}")