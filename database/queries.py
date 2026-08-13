from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from database.models import User, Channel, RewardLink, AdminLog, ChannelType
from utils.logger import logger

async def add_user(session: AsyncSession, telegram_id: int, username: str, full_name: str, referred_by: int = None):
    user = User(telegram_id=telegram_id, username=username, full_name=full_name, referred_by=referred_by)
    session.add(user)
    await session.flush()
    return user

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()

async def get_referral_count(session: AsyncSession, telegram_id: int):
    result = await session.execute(select(func.count(User.id)).where(User.referred_by == telegram_id))
    return result.scalar()

async def get_total_users(session: AsyncSession):
    result = await session.execute(select(func.count(User.id)))
    return result.scalar()

async def get_today_users(session: AsyncSession):
    today = datetime.now().date()
    result = await session.execute(select(func.count(User.id)).where(func.date(User.created_at) == today))
    return result.scalar()

async def get_week_users(session: AsyncSession):
    week_ago = datetime.now() - timedelta(days=7)
    result = await session.execute(select(func.count(User.id)).where(User.created_at >= week_ago))
    return result.scalar()

async def add_channel(session: AsyncSession, channel_id: int, username: str, title: str, invite_link: str, channel_type: ChannelType):
    channel = Channel(channel_id=channel_id, username=username, title=title, invite_link=invite_link, channel_type=channel_type)
    session.add(channel)
    await session.flush()
    return channel

async def get_channels_by_type(session: AsyncSession, channel_type: ChannelType, active_only: bool = True):
    query = select(Channel).where(Channel.channel_type == channel_type)
    if active_only:
        query = query.where(Channel.is_active == True)
    result = await session.execute(query)
    return result.scalars().all()

async def get_channel_by_id(session: AsyncSession, channel_db_id: int):
    result = await session.execute(select(Channel).where(Channel.id == channel_db_id))
    return result.scalar_one_or_none()

async def delete_channel(session: AsyncSession, channel_db_id: int):
    channel = await get_channel_by_id(session, channel_db_id)
    if channel:
        await session.delete(channel)
        await session.flush()

async def toggle_channel_status(session: AsyncSession, channel_db_id: int):
    channel = await get_channel_by_id(session, channel_db_id)
    if channel:
        channel.is_active = not channel.is_active
        await session.flush()
        return channel.is_active
    return None

async def create_reward_link(session: AsyncSession, token: str, channel_id: int, user_id: int):
    link = RewardLink(token=token, channel_id=channel_id, user_id=user_id)
    session.add(link)
    await session.flush()
    return link

async def get_reward_link_by_token(session: AsyncSession, token: str):
    result = await session.execute(select(RewardLink).where(RewardLink.token == token))
    return result.scalar_one_or_none()

async def use_reward_link(session: AsyncSession, token: str):
    link = await get_reward_link_by_token(session, token)
    if link and not link.used:
        link.used = True
        link.used_at = datetime.now()
        await session.flush()
        return True
    return False

async def get_user_rewarded_channels(session: AsyncSession, user_id: int):
    result = await session.execute(select(RewardLink.channel_id).where(RewardLink.user_id == user_id))
    return [row[0] for row in result.all()]

async def get_total_rewards_given(session: AsyncSession):
    result = await session.execute(select(func.count(RewardLink.id)))
    return result.scalar()

async def get_total_used_rewards(session: AsyncSession):
    result = await session.execute(select(func.count(RewardLink.id)).where(RewardLink.used == True))
    return result.scalar()

async def add_admin_log(session: AsyncSession, admin_id: int, action: str):
    log = AdminLog(admin_id=admin_id, action=action)
    session.add(log)
    await session.flush()