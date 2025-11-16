import asyncpg
import os

# --- НАЛАШТУВАННЯ БАЗИ ДАНИХ ---
# Беремо ті самі налаштування, що й у load_to_db.py
DB_CONFIG = {
    "database": "postgres",       # База, де лежать ваші таблиці
    "user": "postgres",
    "password": "123",  # <-- !!! ВАШ ПАРОЛЬ ТУТ !!!
    "host": "localhost",
    "port": 5432
}
# --------------------------------

# Глобальна змінна для зберігання "пулу" з'єднань
# 'pool' - це набір готових, відкритих з'єднань з БД
pool = None

async def get_db_pool():
    """
    Повертає глобальний пул з'єднань.
    Якщо він ще не створений, створює його.
    """
    global pool
    if pool is None:
        print("Створюю новий пул з'єднань з БД...")
        try:
            pool = await asyncpg.create_pool(
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                database=DB_CONFIG["database"],
                min_size=5,  # 5 з'єднань будуть готові одразу
                max_size=20  # До 20 одночасних з'єднань
            )
            print("Пул з'єднань успішно створено.")
        except Exception as e:
            print(f"ПОМИЛКА: Не вдалося створити пул з'єднань: {e}")
            # Це критична помилка, сервер не зможе запуститися
            raise
    return pool

async def close_db_pool():
    """
    Закриває пул з'єднань при зупинці сервера.
    """
    global pool
    if pool:
        print("Закриваю пул з'єднань з БД...")
        await pool.close()
        pool = None
        print("Пул з'єднань закрито.")

# --- Функція-помічник для запитів ---
# Це зекономить нам багато часу:
# вона бере з'єднання з пулу, виконує запит і повертає результат

async def fetch_all(query: str, *args):
    """
    Виконує запит (SELECT) і повертає ВСІ рядки.
    """
    db_pool = await get_db_pool()
    async with db_pool.acquire() as connection:
        # asyncpg.Record повертає об'єкти, схожі на dict,
        # що дуже зручно для перетворення в JSON
        records = await connection.fetch(query, *args)
        return records

async def fetch_one(query: str, *args):
    """
    Виконує запит (SELECT) і повертає ОДИН рядок.
    """
    db_pool = await get_db_pool()
    async with db_pool.acquire() as connection:
        record = await connection.fetchrow(query, *args)
        return record