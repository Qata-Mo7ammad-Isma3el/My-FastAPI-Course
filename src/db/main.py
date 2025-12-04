# > using sqlalchemy to create an async engine for postgresql database
# > in this way we can perform async database operations using sqlmodel and sqlalchemy
#! this is an basic engine object not an async engine object

# // engine = AsyncEngine(
# //     create_engine(
# //         url=settings.DATABASE_URL,
# //         echo=True,
# //     )
# // )
# // async def init_db():
# //     async with engine.begin() as conn:
# //         await conn.run_sync(SQLModel.metadata.create_all)

from sqlmodel import SQLModel
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from src.config import settings


#! thisss is important to register the models
# Import models so SQLModel can register them
from src.db.models import User, Book


DATABASE_URL = settings.DATABASE_URL

# main.py
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # Only echo in debug mode
    pool_size=20,  # Number of connections to keep open
    max_overflow=10,  # Allow up to 10 connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections every hour
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    connect_args={"server_settings": {"timezone": "UTC"}},
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,  # > allow us to access object attributes after commit
    class_=AsyncSession,
)


## this is the dependency that will be used to get the session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# main.py
async def check_db_health() -> dict:
    """Check database connection health"""
    try:
        async with engine.begin() as conn:
            # Simple query to test connection
            result = await conn.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "database": engine.url.database,
                "pool_status": {
                    "checked_out": engine.pool.checkedout(),
                    "connections": engine.pool.size(),
                },
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": engine.url.database if hasattr(engine, "url") else "unknown",
        }


# from tenacity import retry, stop_after_attempt, wait_exponential

# @retry(
#     stop=stop_after_attempt(3),
#     wait=wait_exponential(multiplier=1, min=4, max=10)
# )
# async def get_session_with_retry() -> AsyncGenerator[AsyncSession, None]:
#     """Get session with retry logic for transient failures"""
#     async with SessionLocal() as session:
#         yield session
