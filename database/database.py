from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL
from utils.logger import logger


class Base(DeclarativeBase):
    pass


# Neon PostgreSQL
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "ssl": "require"
    },
)


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Baza muvaffaqiyatli yaratildi va ulandi.")

    except Exception as e:
        logger.error(f"Database ulanish xatosi: {e}")
        raise


async def get_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.error(f"Database xatolik: {e}")
            raise


async def close_db():
    await engine.dispose()
    logger.info("Database connection yopildi.")
