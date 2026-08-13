from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Profilim", callback_data="menu_profile")],
        [InlineKeyboardButton(text="🔗 Referralim", callback_data="menu_referral")],
        [InlineKeyboardButton(text="📊 Referral statistikasi", callback_data="menu_ref_stats")],
        [InlineKeyboardButton(text="🎁 Mukofotim", callback_data="menu_reward")],
        [InlineKeyboardButton(text="📢 Majburiy kanallar", callback_data="menu_channels")],
        [InlineKeyboardButton(text="❓ Yordam", callback_data="menu_help")]
    ])

def back_to_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
    ])