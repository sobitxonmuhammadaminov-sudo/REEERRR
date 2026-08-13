from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import DATABASE_URL
from utils.logger import logger

# Baza asosiy klassi (Base) shu yerda yaratiladi
class Base(DeclarativeBase):
    pass

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        # Jadvallarni yaratish
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Baza muvaffaqiyatli yaratildi va ulandi.")

async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database xatolik: {e}")
            raise