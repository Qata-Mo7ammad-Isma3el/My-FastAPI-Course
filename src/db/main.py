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
from src.config import settings


#! thisss is important to register the models
# Import models so SQLModel can register them
from src.db.models import User, Book


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
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
