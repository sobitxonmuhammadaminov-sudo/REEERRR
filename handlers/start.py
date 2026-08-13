from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from keyboards.user import main_menu_kb, back_to_main_kb
from utils.helpers import build_channel_buttons
from services.subscriptions import get_unsubscribed_mandatory_channels
from services.referrals import process_referral
from database.database import get_session
from database import queries
from config import ADMIN_IDS
from utils.logger import logger

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, bot):
    user_id = message.from_user.id
    args = message.text.split()
    referrer_id = None

    if len(args) > 1:
        arg = args[1]
        try:
            referrer_id = int(arg)
        except ValueError:
            pass

    async for session in get_session():
        user = await queries.get_user_by_telegram_id(session, user_id)
        if not user:
            can_add = True
            if referrer_id:
                can_add = await process_referral(user_id, referrer_id)
            
            await queries.add_user(
                session=session,
                telegram_id=user_id,
                username=message.from_user.username,
                full_name=message.from_user.first_name,
                referred_by=referrer_id if can_add and referrer_id else None
            )
            logger.info(f"Yangi foydalanuvchi: {user_id} (Referrer: {referrer_id})")

    unsubscribed = await get_unsubscribed_mandatory_channels(bot, user_id)
    
    if unsubscribed:
        text = "📢 Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling!"
        kb = build_channel_buttons(unsubscribed, "check_sub_again")
        await message.answer(text, reply_markup=kb)
    else:
        if user_id in ADMIN_IDS:
            from keyboards.admin import admin_panel_kb
            await message.answer("👑 Admin panelga xush kelibsiz!", reply_markup=admin_panel_kb())
        else:
            await message.answer("Assalomu alaykum! Botga xush kelibsiz.\n\nQuyidagi menyu orqali boshlang:", reply_markup=main_menu_kb())

@router.callback_query(F.data == "check_sub_again")
async def check_sub_again(callback: CallbackQuery, bot):
    await callback.answer()
    user_id = callback.from_user.id
    unsubscribed = await get_unsubscribed_mandatory_channels(bot, user_id)
    
    if unsubscribed:
        text = "❌ Siz hali ham ba'zi kanallarga a'zo bo'lmadingiz!\n\nIltimos, barcha kanallarga a'zo bo'ling:"
        kb = build_channel_buttons(unsubscribed, "check_sub_again")
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise e
    else:
        try:
            await callback.message.edit_text("✅ Tasdiqlandi! Botdan foydalanishingiz mumkin.", parse_mode="HTML")
        except TelegramBadRequest:
            pass
            
        if user_id in ADMIN_IDS:
            from keyboards.admin import admin_panel_kb
            await callback.message.answer("👑 Admin panelga xush kelibsiz!", reply_markup=admin_panel_kb())
        else:
            await callback.message.answer("Quyidagi menyu orqali boshlang:", reply_markup=main_menu_kb())