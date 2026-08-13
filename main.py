import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.database import engine, Base
from utils.logger import logger

# Bot ishga tushishidan AVVAL ma'lumotlar bazasi jadvallarini yaratamiz
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Baza muvaffaqiyatli yaratildi va ulandi.")

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Boshlang'ich sozlamalarni bajarish (Jadval yaratish)
    await on_startup()
    
    # Routerni ulash (importlar shu yerga ko'chirildi, xato berishini oldini oladi)
    from handlers.start import router as start_router
    from handlers.user import router as user_router
    from handlers.admin import router as admin_router

    dp.include_router(start_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)
    
    logger.info("Bot ishga tushdi...")
    
    try:
        # drop_pending_updates=True server uchun juda muhim
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), drop_pending_updates=True)
    except Exception as e:
        logger.critical(f"Bot to'xtadi: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    # Agar bot xatolik yuzaga kelsa, u o'chib qolmaydi, 5 soniyadan so'ng qayta ishga tushadi
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Bot to'xtatildi (Ctrl+C)")
            break
        except Exception as e:
            logger.error(f"Qayta ishga tushirish... Sabab: {e}")
            asyncio.sleep(5)