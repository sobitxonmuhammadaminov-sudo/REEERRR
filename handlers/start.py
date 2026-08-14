from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest

from keyboards.user import main_menu_kb
from utils.helpers import build_channel_buttons
from services.subscriptions import get_unsubscribed_mandatory_channels
from services.referrals import process_referral

from database.database import get_session
from database import queries

from config import ADMIN_IDS
from utils.logger import logger


router = Router()


# ============================================================
# SAT MARATHON PROMO
# ============================================================

def get_promo_text(referral_link: str) -> str:
    return (
        "⚡️ <b>Join the SAT MARATHON and learn how to ace "
        "the SAT Math section!</b> 🚀\n\n"
        
        "📚 <b>Your teachers will be:</b>\n\n"
        
        "👨‍🏫 Mr. Yoqubjon\n"
        "👨‍🏫 Mr. Xasanbek\n"
        "👨‍🏫 Mr. Xuzayfa\n\n"
        
        "🎯 Learn effective strategies and techniques "
        "to achieve a high score in SAT Math!\n\n"
        
        "🔐 To get access to the private channel, invite "
        "3 of your friends using the referral link below.\n\n"
        
        f"🔗 <b>Your Referral Link:</b>\n"
        f"<code>{referral_link}</code>\n\n"
        
        "Invite your friends and join the SAT MARATHON! 🔥"
    )


# ============================================================
# USER MENU
# ============================================================

def user_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👤 My Profile"),
            ],
            [
                KeyboardButton(text="📊 My Referrals"),
            ],
            [
                KeyboardButton(text="🎁 Claim Reward"),
            ],
        ],
        resize_keyboard=True,
    )


# ============================================================
# START COMMAND
# ============================================================

@router.message(CommandStart())
async def cmd_start(message: Message, bot):
    user_id = message.from_user.id

    # --------------------------------------------------------
    # Referral ID olish
    # --------------------------------------------------------

    args = message.text.split()

    referrer_id = None

    if len(args) > 1:
        arg = args[1]

        try:
            referrer_id = int(arg)
        except ValueError:
            referrer_id = None

    # --------------------------------------------------------
    # User database'ga qo'shish
    # --------------------------------------------------------

    async for session in get_session():

        user = await queries.get_user_by_telegram_id(
            session,
            user_id,
        )

        if not user:

            can_add = True

            if referrer_id:
                can_add = await process_referral(
                    user_id,
                    referrer_id,
                )

            await queries.add_user(
                session=session,
                telegram_id=user_id,
                username=message.from_user.username,
                full_name=message.from_user.first_name,
                referred_by=(
                    referrer_id
                    if can_add and referrer_id
                    else None
                ),
            )

            logger.info(
                f"Yangi foydalanuvchi: "
                f"{user_id} "
                f"(Referrer: {referrer_id})"
            )

    # --------------------------------------------------------
    # Mandatory channel tekshirish
    # --------------------------------------------------------

    unsubscribed = await get_unsubscribed_mandatory_channels(
        bot,
        user_id,
    )

    # --------------------------------------------------------
    # Agar kanallarga obuna bo'lmagan bo'lsa
    # --------------------------------------------------------

    if unsubscribed:

        text = (
            "Assalomu alaykum! 👋\n\n"
            "To participate in the SAT Marathon, "
            "please follow the channels listed below.\n\n"
            "Once you have followed all of them, "
            "click “Done”."
        )

        keyboard = build_channel_buttons(
            unsubscribed,
            "check_sub_again",
        )

        await message.answer(
            text,
            reply_markup=keyboard,
        )

        return

    # --------------------------------------------------------
    # Agar hamma kanalga allaqachon obuna bo'lgan bo'lsa
    # --------------------------------------------------------

    bot_info = await bot.get_me()

    referral_link = (
        f"https://t.me/{bot_info.username}"
        f"?start={user_id}"
    )

    promo_text = get_promo_text(
        referral_link
    )

    keyboard = user_menu()

    await message.answer(
        promo_text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )

    # --------------------------------------------------------
    # Admin panel
    # --------------------------------------------------------

    if user_id in ADMIN_IDS:

        from keyboards.admin import admin_panel_kb

        await message.answer(
            "👑 <b>Welcome to the Admin Panel!</b>",
            reply_markup=admin_panel_kb(),
            parse_mode="HTML",
        )


# ============================================================
# CHECK SUBSCRIPTION
# ============================================================

@router.callback_query(
    F.data == "check_sub_again"
)
async def check_sub_again(
    callback: CallbackQuery,
    bot,
):
    await callback.answer()

    user_id = callback.from_user.id

    # --------------------------------------------------------
    # Kanallarni qayta tekshirish
    # --------------------------------------------------------

    unsubscribed = await get_unsubscribed_mandatory_channels(
        bot,
        user_id,
    )

    # --------------------------------------------------------
    # Hali ham obuna bo'lmagan kanallar mavjud
    # --------------------------------------------------------

    if unsubscribed:

        text = (
            "Assalomu alaykum! 👋\n\n"
            "To participate in the SAT Marathon, "
            "please follow the channels listed below.\n\n"
            "Once you have followed all of them, "
            "click “Done”."
        )

        keyboard = build_channel_buttons(
            unsubscribed,
            "check_sub_again",
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
            )

        except TelegramBadRequest as e:

            if "message is not modified" not in str(e):
                raise

        return

    # --------------------------------------------------------
    # Barcha kanallarga obuna bo'lgan
    # --------------------------------------------------------

    bot_info = await bot.get_me()

    referral_link = (
        f"https://t.me/{bot_info.username}"
        f"?start={user_id}"
    )

    promo_text = get_promo_text(
        referral_link
    )

    keyboard = user_menu()

    # --------------------------------------------------------
    # Eski xabarni promo xabarga almashtirish
    # --------------------------------------------------------

    try:

        await callback.message.edit_text(
            promo_text,
            reply_markup=None,
            parse_mode="HTML",
        )

        # Keyboardni alohida yuboramiz
        await callback.message.answer(
            "👇 Choose an option:",
            reply_markup=keyboard,
        )

    except TelegramBadRequest:

        await callback.message.answer(
            promo_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    # --------------------------------------------------------
    # Admin panel
    # --------------------------------------------------------

    if user_id in ADMIN_IDS:

        from keyboards.admin import admin_panel_kb

        await callback.message.answer(
            "👑 <b>Welcome to the Admin Panel!</b>",
            reply_markup=admin_panel_kb(),
            parse_mode="HTML",
        )
