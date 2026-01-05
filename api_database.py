import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings

# Initialize pool globally
pool = None

engine = create_async_engine(
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    """SQLAlchemy session dependency"""
    async with async_session() as session:
        yield session

async def get_db_pool():
    """Initialize asyncpg connection pool"""
    global pool
    if pool is None:
        try:
            pool = await asyncpg.create_pool(
                user=settings.db_user,
                password=settings.db_password,
                host=settings.db_host,
                port=settings.db_port,
                database=settings.db_name,
                min_size=5,
                max_size=20
            )
            print("Connection pool created successfully.")
        except Exception as e:
            print(f"ERROR creating pool: {e}")
            raise
    return pool

async def close_db_pool():
    """Close connection pool"""
    global pool
    if pool:
        print("Closing database pool...")
        await pool.close()
        pool = None
        print("Pool closed.")

async def fetch_all(query: str, *args):
    """Execute SELECT query and return all rows"""
    db_pool = await get_db_pool()
    async with db_pool.acquire() as connection:
        return await connection.fetch(query, *args)

async def fetch_one(query: str, *args):
    """Execute SELECT query and return one row"""
    db_pool = await get_db_pool()
    async with db_pool.acquire() as connection:
        return await connection.fetchrow(query, *args)
