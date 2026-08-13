from database.database import get_session
from database import queries
from utils.logger import logger

async def process_referral(user_telegram_id: int, referrer_telegram_id: int) -> bool:
    if user_telegram_id == referrer_telegram_id:
        logger.warning(f"Foydalanuvchi {user_telegram_id} o'zining referral linkidan foydalandi.")
        return False

    async for session in get_session():
        existing_user = await queries.get_user_by_telegram_id(session, user_telegram_id)
        if existing_user:
            return False

        referrer = await queries.get_user_by_telegram_id(session, referrer_telegram_id)
        if not referrer:
            return False

        return True
    return False