from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select, func

from keyboards.user import main_menu_kb
from utils.helpers import build_channel_buttons
from services.subscriptions import get_unsubscribed_mandatory_channels
from database.database import get_session
from database import queries
from database.models import Channel, ChannelType, RewardLink, User
from config import REQUIRED_REFERRALS
from utils.logger import logger


router = Router()


# ============================================================
# MY PROFILE
# ============================================================

@router.message(F.text == "👤 My Profile")
async def show_profile(message: Message):
    user_id = message.from_user.id

    logger.info(f"👤 My Profile bosildi: {user_id}")

    user = None

    async for session in get_session():
        user = await queries.get_user_by_telegram_id(
            session,
            user_id
        )

    if not user:
        await message.answer(
            "❌ User not found."
        )
        return

    name = user.full_name or "Not specified"
    username = user.username or "None"

    text = (
        "👤 <b>Your Profile</b>\n\n"
        f"🆔 ID: <code>{user.telegram_id}</code>\n"
        f"📛 Name: {name}\n"
        f"🌐 Username: @{username}"
    )

    await message.answer(
        text,
        parse_mode="HTML"
    )


# ============================================================
# MY REFERRALS
# ============================================================

@router.message(F.text == "📊 My Referrals")
async def show_stats(message: Message):
    user_id = message.from_user.id

    logger.info(f"📊 My Referrals bosildi: {user_id}")

    count = 0

    async for session in get_session():

        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.referred_by == user_id)
        )

        result = await session.execute(stmt)

        count = result.scalar() or 0

    remaining = max(
        0,
        REQUIRED_REFERRALS - count
    )

    text = (
        "📊 <b>My Referrals</b>\n\n"
        f"👥 Total Invites: <b>{count}</b>\n"
        f"🎯 Required: <b>{REQUIRED_REFERRALS}</b>\n"
        f"⏳ Remaining: <b>{remaining}</b>"
    )

    await message.answer(
        text,
        parse_mode="HTML"
    )


# ============================================================
# CLAIM REWARD
# ============================================================

@router.message(F.text == "🎁 Claim Reward")
async def show_reward(
    message: Message,
    bot: Bot
):
    user_id = message.from_user.id

    logger.info(f"🎁 Claim Reward bosildi: {user_id}")

    count = 0

    # --------------------------------------------------------
    # Referral sonini tekshirish
    # --------------------------------------------------------

    async for session in get_session():

        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.referred_by == user_id)
        )

        result = await session.execute(stmt)

        count = result.scalar() or 0

    # --------------------------------------------------------
    # Yetarli referral bo'lmasa
    # --------------------------------------------------------

    if count < REQUIRED_REFERRALS:

        remaining = max(
            0,
            REQUIRED_REFERRALS - count
        )

        text = (
            "🎁 <b>Reward</b>\n\n"
            f"👥 You need <b>{remaining}</b> "
            "more friends.\n\n"
            "🔗 Invite your friends using "
            "your referral link!"
        )

        await message.answer(
            text,
            parse_mode="HTML"
        )

        return

    # --------------------------------------------------------
    # Reward channel va link
    # --------------------------------------------------------

    async for session in get_session():

        # Oldingi reward linkni qidiramiz
        stmt_check = (
            select(RewardLink)
            .where(
                RewardLink.user_id == user_id
            )
        )

        result_check = await session.execute(
            stmt_check
        )

        existing_link = (
            result_check.scalar_one_or_none()
        )

        # Reward channelni qidiramiz
        stmt_channel = (
            select(Channel)
            .where(
                Channel.channel_type
                == ChannelType.REWARD
            )
        )

        result_channel = await session.execute(
            stmt_channel
        )

        reward_channel = (
            result_channel.scalars().first()
        )

        if not reward_channel:

            await message.answer(
                "❌ There are no reward channels "
                "available right now."
            )

            return

        # ----------------------------------------------------
        # Agar link oldin yaratilgan bo'lsa
        # ----------------------------------------------------

        if existing_link:

            generated_link = existing_link.token

        else:

            try:

                chat_invite = (
                    await bot.create_chat_invite_link(
                        chat_id=reward_channel.channel_id,
                        member_limit=1,
                        name=f"Reward for {user_id}"
                    )
                )

                generated_link = (
                    chat_invite.invite_link
                )

                new_link = RewardLink(
                    token=generated_link,
                    channel_id=reward_channel.id,
                    user_id=user_id
                )

                session.add(new_link)

                await session.commit()

            except TelegramBadRequest as e:

                logger.error(
                    f"Reward link yaratishda xato: {e}"
                )

                await message.answer(
                    "❌ Error creating reward link.\n\n"
                    "The bot must be an administrator "
                    "of the reward channel."
                )

                return

    # --------------------------------------------------------
    # Linkni foydalanuvchiga yuborish
    # --------------------------------------------------------

    await message.answer(
        "🎉 <b>Congratulations!</b>\n\n"
        f"You have invited "
        f"<b>{REQUIRED_REFERRALS}</b> friends!\n\n"
        "🎁 <b>Your exclusive 1-time link:</b>\n\n"
        f"{generated_link}\n\n"
        "⚠️ Click on it to join the channel!",
        parse_mode="HTML"
    )


# ============================================================
# SAFE EDIT
# ============================================================

async def safe_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup=None
):
    try:

        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    except TelegramBadRequest as e:

        if "message is not modified" not in str(e):
            raise


# ============================================================
# CHANNELS
# ============================================================

@router.callback_query(
    F.data == "menu_channels"
)
async def show_channels(
    callback: CallbackQuery,
    bot: Bot
):
    await callback.answer()

    user_id = callback.from_user.id

    unsubscribed = (
        await get_unsubscribed_mandatory_channels(
            bot,
            user_id
        )
    )

    if unsubscribed:

        text = (
            "📢 <b>Mandatory Channels</b>\n\n"
            "Please subscribe:"
        )

        kb = build_channel_buttons(
            unsubscribed,
            "check_sub_from_menu"
        )

        await safe_edit(
            callback,
            text,
            reply_markup=kb
        )

    else:

        text = (
            "✅ You are subscribed "
            "to all channels!"
        )

        await safe_edit(
            callback,
            text,
            reply_markup=main_menu_kb()
        )


# ============================================================
# CHECK SUBSCRIPTION FROM MENU
# ============================================================

@router.callback_query(
    F.data == "check_sub_from_menu"
)
async def check_sub_from_menu(
    callback: CallbackQuery,
    bot: Bot
):
    from handlers.start import check_sub_again

    await check_sub_again(
        callback,
        bot
    )


# ============================================================
# NO LINK
# ============================================================

@router.callback_query(
    F.data == "no_link"
)
async def no_link_warning(
    callback: CallbackQuery
):
    await callback.answer(
        "⚠️ No link provided for this channel by admin!",
        show_alert=True
    )


# ============================================================
# HELP
# ============================================================

@router.callback_query(
    F.data == "menu_help"
)
async def show_help(
    callback: CallbackQuery
):
    await callback.answer()

    text = (
        "❓ <b>Help</b>\n\n"
        "1. Subscribe to the channels.\n"
        "2. Share your link with friends.\n"
        "3. Reach the required amount "
        "to get the reward."
    )

    await safe_edit(
        callback,
        text,
        reply_markup=main_menu_kb()
    )


# ============================================================
# BACK
# ============================================================

@router.callback_query(
    F.data == "back_to_main"
)
async def back_to_main(
    callback: CallbackQuery
):
    await callback.answer()

    text = (
        "Welcome to the bot!\n\n"
        "Please choose an option "
        "from the menu below:"
    )

    await safe_edit(
        callback,
        text,
        reply_markup=main_menu_kb()
    )
