from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from database.database import get_session
from sqlalchemy import select
from utils.logger import logger

async def get_unsubscribed_mandatory_channels(bot: Bot, user_id: int) -> list:
    unsubscribed = []
    async for session in get_session():
        try:
            from database.models import Channel, ChannelType
            stmt = select(Channel).where(Channel.channel_type == ChannelType.MANDATORY, Channel.is_active == True)
            result = await session.execute(stmt)
            channels = result.scalars().all()
        except Exception as e:
            logger.error(f"MB xatolik: {e}")
            return []

        for ch in channels:
            chat_id = ch.channel_id 
            if not chat_id: continue
            
            try:
                member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                if member.status in ['left', 'kicked']:
                    # Havolani tayyorlash: birinchi invite_link, keyin username
                    link = ch.invite_link 
                    if not link and ch.username:
                        link = f"https://t.me/{ch.username.lstrip('@')}"
                    
                    unsubscribed.append({
                        'title': ch.title or 'Kanal',
                        'username': link # helpers.py ga shu link yuboriladi
                    })
            except TelegramBadRequest as e:
                logger.error(f"Obuna tekshirishda xatolik: {e}")
                link = ch.invite_link or (f"https://t.me/{ch.username.lstrip('@')}" if ch.username else "")
                unsubscribed.append({'title': ch.title or 'Kanal', 'username': link})
    return unsubscribed