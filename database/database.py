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


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require",
    },
)


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """
    Database jadvallarini yaratadi.
    Bu funksiya bot ishga tushganda faqat bir marta chaqiriladi.
    """
    try:
        # Modellarni metadata'ga yuklaymiz
        from database import models  # noqa: F401

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Barcha database jadvallari yaratildi.")

    except Exception as e:
        logger.error(f"❌ Database jadvallarini yaratishda xato: {e}")
        raise


async def get_session():
    """
    Database session olish uchun generator.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Database xatolik: {e}")
            raise


async def close_db():
    """
    Database connection pool'ni yopadi.
    """
    try:
        await engine.dispose()
        logger.info("✅ Database connection yopildi.")

    except Exception as e:
        logger.error(f"❌ Database yopishda xato: {e}")
