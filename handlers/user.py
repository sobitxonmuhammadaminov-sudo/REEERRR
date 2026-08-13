from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select

from keyboards.user import main_menu_kb, back_to_main_kb
from utils.helpers import build_channel_buttons
from services.subscriptions import get_unsubscribed_mandatory_channels
from database.database import get_session
from database import queries
from database.models import Channel, ChannelType
from config import REQUIRED_REFERRALS

router = Router()

async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e

@router.callback_query(F.data == "menu_profile")
async def show_profile(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    user = None
    async for session in get_session():
        user = await queries.get_user_by_telegram_id(session, user_id)
    
    if user:
        ism = user.full_name or "Ko'rsatilmagan"
        username = user.username or "yo'q"
        text = f"👤 <b>Sizning profilingiz</b>\n\n🆔 ID: <code>{user.telegram_id}</code>\n📛 Ism: {ism}\n🌐 Username: @{username}"
    else:
        text = "❌ Ma'lumot topilmadi."
    await safe_edit(callback, text, reply_markup=back_to_main_kb())

@router.callback_query(F.data == "menu_referral")
async def show_referral(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={callback.from_user.id}"
    text = f"🔗 <b>Sizning havolangiz:</b>\n\n<code>{link}</code>\n\n📌 Do'stlaringizga yuboring. Sizga yana <b>{REQUIRED_REFERRALS}</b> ta odam kerak."
    await safe_edit(callback, text, reply_markup=back_to_main_kb())

@router.callback_query(F.data == "menu_ref_stats")
async def show_stats(callback: CallbackQuery):
    await callback.answer()
    count = 0 
    text = f"📊 <b>Statistika</b>\n\nJami takliflar: <b>{count}</b> ta\nKerakli: <b>{REQUIRED_REFERRALS}</b> ta\nQolgan: <b>{max(0, REQUIRED_REFERRALS - count)}</b> ta"
    await safe_edit(callback, text, reply_markup=back_to_main_kb())

@router.callback_query(F.data == "menu_reward")
async def show_reward(callback: CallbackQuery):
    await callback.answer()
    count = 0 
    if count >= REQUIRED_REFERRALS:
        async for session in get_session():
            stmt = select(Channel).where(Channel.channel_type == ChannelType.REWARD, Channel.is_active == True).first()
            result = await session.execute(stmt)
            reward_ch = result.scalar_one_or_none()
            
        if reward_ch:
            link = reward_ch.invite_link
            if not link and reward_ch.username:
                link = f"https://t.me/{reward_ch.username.lstrip('@')}"
            text = f"🎉 <b>Tabriklaymiz!</b> Siz {REQUIRED_REFERRALS} ta odamni taklif qildingiz!\n\n🎁 <b>Mukofot kanali:</b>\n{link}"
        else:
            text = "❌ Hozirda mukofot kanallari mavjud emas."
    else:
        text = f"🎁 <b>Mukofot</b>\n\nSizga yana <b>{max(0, REQUIRED_REFERRALS - count)}</b> ta odam kerak."
    await safe_edit(callback, text, reply_markup=back_to_main_kb())

@router.callback_query(F.data == "menu_channels")
async def show_channels(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    unsubscribed = await get_unsubscribed_mandatory_channels(bot, callback.from_user.id)
    if unsubscribed:
        text = "📢 <b>Majburiy kanallar</b>\n\nObuna bo'ling:"
        kb = build_channel_buttons(unsubscribed, "check_sub_from_menu")
        await safe_edit(callback, text, reply_markup=kb)
    else:
        text = "✅ Siz barcha kanallarga obuna bo'ldingiz!"
        await safe_edit(callback, text, reply_markup=back_to_main_kb())

@router.callback_query(F.data == "check_sub_from_menu")
async def check_sub_from_menu(callback: CallbackQuery, bot: Bot):
    from handlers.start import check_sub_again
    await check_sub_again(callback, bot)

@router.callback_query(F.data == "no_link")
async def no_link_warning(callback: CallbackQuery):
    await callback.answer("⚠️ Ushbu kanal uchun admin tomonidan havola kiritilmagan!", show_alert=True)

@router.callback_query(F.data == "menu_help")
async def show_help(callback: CallbackQuery):
    await callback.answer()
    text = "❓ <b>Yordam</b>\n\n1. Kanallarga obuna bo'ling.\n2. Havolani do'stlaringizga yuboring.\n3. Kerakli miqdorni to'ldiring va mukofot oling."
    await safe_edit(callback, text, reply_markup=back_to_main_kb())

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    text = "Assalomu alaykum! Botga xush kelibsiz.\n\nQuyidagi menyu orqali boshlang:"
    await safe_edit(callback, text, reply_markup=main_menu_kb())