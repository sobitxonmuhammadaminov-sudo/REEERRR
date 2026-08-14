from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_channel_buttons(
    channels: list,
    check_callback: str
) -> InlineKeyboardMarkup:

    kb = InlineKeyboardMarkup(
        inline_keyboard=[]
    )

    for ch in channels:

        title = ch.get(
            "title",
            "Kanal"
        )

        link = ch.get(
            "username"
        )

        # Kanal havolasi mavjud bo'lsa
        if link:

            btn = InlineKeyboardButton(
                text=f"📢 {title}",
                url=link
            )

            kb.inline_keyboard.append(
                [btn]
            )

        else:

            btn = InlineKeyboardButton(
                text=f"⚠️ {title} (Havola kiritilmagan)",
                callback_data="no_link"
            )

            kb.inline_keyboard.append(
                [btn]
            )

    # ==========================================
    # DONE TUGMASI
    # ==========================================

    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="✅ Done",
                callback_data=check_callback
            )
        ]
    )

    return kb
