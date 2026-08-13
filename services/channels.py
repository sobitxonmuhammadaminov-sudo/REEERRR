from database.database import get_session
from database.models import ChannelType
from database import queries
from utils.logger import logger

async def add_new_channel(channel_id: int, username: str, title: str, invite_link: str, channel_type: ChannelType, admin_id: int):
    async for session in get_session():
        await queries.add_channel(session, channel_id, username, title, invite_link, channel_type)
        type_name = "Majburiy" if channel_type == ChannelType.MANDATORY else "Oddiy"
        await queries.add_admin_log(session, admin_id, f"{type_name} kanal qo'shildi: {title} (@{username})")
        logger.info(f"Admin {admin_id} tomonidan {type_name} kanal qo'shildi: {title}")

async def remove_channel(channel_db_id: int, admin_id: int):
    async for session in get_session():
        channel = await queries.get_channel_by_id(session, channel_db_id)
        if channel:
            type_name = "Majburiy" if channel.channel_type == ChannelType.MANDATORY else "Oddiy"
            await queries.delete_channel(session, channel_db_id)
            await queries.add_admin_log(session, admin_id, f"{type_name} kanal o'chirildi: {channel.title}")
            logger.info(f"Admin {admin_id} tomonidan {type_name} kanal o'chirildi: {channel.title}")
            return True
        return False

async def switch_channel_status(channel_db_id: int, admin_id: int):
    async for session in get_session():
        new_status = await queries.toggle_channel_status(session, channel_db_id)
        if new_status is not None:
            status_text = "Aktiv" if new_status else "Deaktiv"
            await queries.add_admin_log(session, admin_id, f"Kanal (ID: {channel_db_id}) holati {status_text} ga o'zgartirildi.")
            return new_status
        return None