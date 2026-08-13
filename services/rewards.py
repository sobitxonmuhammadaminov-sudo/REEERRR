import datetime
from aiogram import Bot
from database.database import get_session
from database.models import ChannelType
from database import queries
from utils.logger import logger
from config import REQUIRED_REFERRALS

async def check_and_give_reward(user_telegram_id: int, bot: Bot) -> dict:
    async for session in get_session():
        referral_count = await queries.get_referral_count(session, user_telegram_id)
        rewarded_channels = await queries.get_user_rewarded_channels(session, user_telegram_id)
        available_channels = await queries.get_channels_by_type(session, ChannelType.REWARD)
        
        # Foydalanuvchi hali mukofot olmagan kanallarni topamiz
        unrewarded_channels = [ch for ch in available_channels if ch.id not in rewarded_channels]
        
        if referral_count >= REQUIRED_REFERRALS and unrewarded_channels:
            channel_to_reward = unrewarded_channels[0] # Navbat bo'yicha birinchisini beramiz
            
            try:
                # TELEGRAM API ORQALI 1 MARTALIK LINK YARATISH
                invite = await bot.create_chat_invite_link(
                    chat_id=channel_to_reward.channel_id,
                    name=f"Reward for {user_telegram_id}",
                    member_limit=1, # Faqat 1 kishiga ishlaydi
                    expire_date=datetime.datetime.now() + datetime.timedelta(days=1) # 1 kun ichida ishlatishi kerak
                )
                
                # Bazada saqlab qolish uchun link oxirgi qismini token sifatida olamiz
                token = invite.invite_link.split("/")[-1]
                await queries.create_reward_link(session, token=token, channel_id=channel_to_reward.id, user_id=user_telegram_id)
                
                return {
                    "status": "success", 
                    "link": invite.invite_link, # Tayyor 1 martalik link
                    "channel_title": channel_to_reward.title
                }
            except Exception as e:
                logger.error(f"Link yaratishda xatolik (Kanal: {channel_to_reward.channel_id}): {e}")
                return {"status": "error_api", "message": "Botga kanalda admin huquqi berilmagan yoki link yaratishga ruxsat yo'q!"}
        
        elif not unrewarded_channels and referral_count >= REQUIRED_REFERRALS:
            return {"status": "no_more_channels"}
            
        return {"status": "not_enough", "current": referral_count, "required": REQUIRED_REFERRALS}
    return {"status": "error"}