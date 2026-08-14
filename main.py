import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.database import init_db, close_db
from utils.logger import logger


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()

    try:
        # ==========================================
        # DATABASE
        # ==========================================

        logger.info("🔄 Database ishga tushirilmoqda...")

        await init_db()

        logger.info("✅ Database tayyor.")

        # ==========================================
        # ROUTERS
        # ==========================================

        from handlers.start import router as start_router
        from handlers.user import router as user_router
        from handlers.admin import router as admin_router

        dp.include_router(start_router)
        dp.include_router(user_router)
        dp.include_router(admin_router)

        logger.info("✅ Barcha routerlar ulandi.")

        # ==========================================
        # BOT
        # ==========================================

        logger.info("🤖 ReferralBot ishga tushmoqda...")

        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )

    except Exception as e:
        logger.critical(
            f"❌ Botda kritik xatolik: {e}",
            exc_info=True
        )
        raise

    finally:
        logger.info("🔄 Resurslar yopilmoqda...")

        try:
            await bot.session.close()
        except Exception as e:
            logger.error(
                f"Bot session yopishda xato: {e}"
            )

        try:
            await close_db()
        except Exception as e:
            logger.error(
                f"Database yopishda xato: {e}"
            )

        logger.info("✅ Bot to‘xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info(
            "🛑 Bot foydalanuvchi tomonidan to‘xtatildi."
        )

    except Exception as e:
        logger.critical(
            f"❌ Bot ishga tushmadi: {e}",
            exc_info=True
        )
