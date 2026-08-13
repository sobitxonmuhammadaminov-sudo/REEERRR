from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select, delete

from database.database import get_session
from database.models import Channel, ChannelType
from config import ADMIN_IDS
from keyboards.admin import admin_panel_kb, channel_management_kb, channel_list_kb
from utils.logger import logger

router = Router()

# ---------------------------------------------------------
# SHU YERGA KO'TARIB CHIQILDI
# ---------------------------------------------------------
class AdminStates(StatesGroup):
    waiting_for_mandatory = State()
    waiting_for_reward = State()

# ---------------------------------------------------------
# /ADMIN KOMANDASI
# ---------------------------------------------------------
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("👑 <b>Admin panelga xush kelibsiz!</b>", reply_markup=admin_panel_kb(), parse_mode="HTML")
    else:
        await message.answer("❌ Sizda admin huquqlari mavjud emas.")

# ---------------------------------------------------------
# ASOSIY ADMIN PANEL CALLBACKLARI
# ---------------------------------------------------------
async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e

@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    await safe_edit(callback, "👑 <b>Admin panelga xush kelibsiz!</b>", admin_panel_kb())

@router.callback_query(F.data == "adm_mandatory_menu")
async def adm_mandatory_menu(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    await safe_edit(callback, "📢 <b>Majburiy kanallar bo'limi</b>", channel_management_kb("mandatory"))

@router.callback_query(F.data == "adm_reward_menu")
async def adm_reward_menu(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    await safe_edit(callback, "🎁 <b>Oddiy (Reward) kanallar bo'limi</b>", channel_management_kb("reward"))

@router.callback_query(F.data.startswith("adm_add_"))
async def adm_add_channel(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    ch_type = callback.data.split("_")[-1]
    text = "Quyidagi ma'lumotlarni <b>qatordan-qatorga</b> yuboring:\n\n1-line: Kanal IDsi (masalan: -100xxxxxxxxx)\n2-line: Kanal nomi\n3-line: Username (@my_channel yoki bo'sh qoldiring)\n4-line: Invite link (https://t.me/+Abc123 yoki bo'sh qoldiring)"
    await safe_edit(callback, text)
    if ch_type == "mandatory":
        await state.set_state(AdminStates.waiting_for_mandatory)
    else:
        await state.set_state(AdminStates.waiting_for_reward)

@router.message(AdminStates.waiting_for_mandatory)
@router.message(AdminStates.waiting_for_reward)
async def process_add_channel(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    lines = message.text.strip().split('\n')
    if len(lines) < 2:
        await message.answer("❌ Noto'g'ri format. Kamida 1 va 2-qatorlarni to'ldiring.", reply_markup=admin_panel_kb())
        await state.clear()
        return

    channel_id_str = lines[0].strip()
    title = lines[1].strip()
    username = lines[2].strip() if len(lines) > 2 else None
    invite_link = lines[3].strip() if len(lines) > 3 else ""

    try:
        channel_id = int(channel_id_str)
    except ValueError:
        await message.answer("❌ Kanal IDsi raqam bo'lishi kerak.", reply_markup=admin_panel_kb())
        await state.clear()
        return

    ch_type = ChannelType.MANDATORY if await state.get_state() == "AdminStates:waiting_for_mandatory" else ChannelType.REWARD
    await state.clear()
    
    async for session in get_session():
        try:
            new_channel = Channel(channel_id=channel_id, title=title, username=username, invite_link=invite_link, channel_type=ch_type)
            session.add(new_channel)
            await session.commit()
            await message.answer(f"✅ <b>{title}</b> kanali muvaffaqiyatli qo'shildi!", reply_markup=admin_panel_kb(), parse_mode="HTML")
        except Exception as e:
            logger.error(f"Kanal qo'shishda xato: {e}")
            await message.answer(f"❌ Xatolik (Ehtimol bu ID mavjud).", reply_markup=admin_panel_kb())

@router.callback_query(F.data.startswith("adm_list_"))
async def adm_list_channels(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    ch_type_str = callback.data.split("_")[-1]
    ch_type = ChannelType.MANDATORY if ch_type_str == "mandatory" else ChannelType.REWARD
    async for session in get_session():
        stmt = select(Channel).where(Channel.channel_type == ch_type)
        result = await session.execute(stmt)
        channels = result.scalars().all()
        
    if not channels:
        await safe_edit(callback, "ℹ️ Hech qanday kanal topilmadi.", channel_management_kb(ch_type_str))
    else:
        await safe_edit(callback, f"📋 <b>{ch_type_str} kanallar ro'yxati:</b>\n\nO'chirish uchun kanalni tanlang:", channel_list_kb(channels, ch_type_str))

@router.callback_query(F.data.startswith("adm_del_"))
async def adm_del_channel(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    parts = callback.data.split("_")
    ch_type_str = parts[2]
    ch_type = ChannelType.MANDATORY if ch_type_str == "mandatory" else ChannelType.REWARD
    channel_id = int(parts[3])
    
    async for session in get_session():
        stmt = delete(Channel).where(Channel.id == channel_id)
        await session.execute(stmt)
        await session.commit()
        
    await callback.answer("Kanal o'chirildi!", show_alert=True)
    
    async for session in get_session():
        stmt = select(Channel).where(Channel.channel_type == ch_type)
        result = await session.execute(stmt)
        channels = result.scalars().all()
        
    if not channels:
        await safe_edit(callback, "✅ Kanal o'chirildi.\n\nℹ️ Boshqa kanallar yo'q.", channel_management_kb(ch_type_str))
    else:
        await safe_edit(callback, f"✅ Kanal o'chirildi.\n\n📋 <b>{ch_type_str} kanallar ro'yxati:</b>", channel_list_kb(channels, ch_type_str))