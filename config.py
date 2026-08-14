import os
from dotenv import load_dotenv

load_dotenv()

# Telegram bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin ID'lar
ADMIN_IDS = (
    list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
    if os.getenv("ADMIN_IDS")
    else []
)

# PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# DATABASE_URL majburiy
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL topilmadi! Render Environment Variables "
        "ichida DATABASE_URL qo'shing."
    )

# Referral uchun kerakli takliflar soni
REQUIRED_REFERRALS = 3
