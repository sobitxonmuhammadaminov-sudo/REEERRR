from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stats")],
        [InlineKeyboardButton(text="📢 MAJ BURIY KANALLAR", callback_data="adm_mandatory_menu")],
        [InlineKeyboardButton(text="🎁 ODDIY KANALLAR", callback_data="adm_reward_menu")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm_users")],
        [InlineKeyboardButton(text="🏆 Mukofotlar", callback_data="adm_rewards")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="adm_settings")]
    ])

def channel_management_kb(ch_type: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data=f"adm_add_{ch_type}")],
        [InlineKeyboardButton(text="📋 Kanallar ro'yxati", callback_data=f"adm_list_{ch_type}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
    ])

def channel_list_kb(channels: list, ch_type: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for ch in channels:
        # E'TIBOR: chat_id EMAS, aynan channel_id
        text = f"❌ {ch.title} (ID: {ch.channel_id})"
        kb.inline_keyboard.append([InlineKeyboardButton(text=text, callback_data=f"adm_del_{ch_type}_{ch.id}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"adm_menu_{ch_type}")])
    return kb