from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def build_channel_buttons(channels: list, check_callback: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    
    for ch in channels:
        title = ch.get('title', 'Kanal')
        link = ch.get('username') 
        
        # AGAR HAVOLA (LINK) MAVJUD BO'LSA TUGMANI CHIQARAMIZ
        if link:
            btn = InlineKeyboardButton(text=f"📢 {title}", url=link)
            kb.inline_keyboard.append([btn])
        else:
            # Agar admin link kiritmagan bo'lsa, foydalanuvchiga ogohlantirish ko'rsatamiz
            btn = InlineKeyboardButton(text=f"⚠️ {title} (Havola kiritilmagan)", callback_data="no_link")
            kb.inline_keyboard.append([btn])
        
    # Obunani tekshirish tugmasi doim ko'rinadi
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data=check_callback)
    ])
    
    return kb