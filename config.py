import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# Bot settings (configurable by owner via commands, with these as defaults)
DEFAULT_BOT_CONFIG = {
    "swear_mute_duration_minutes": 30,
    "ad_mute_duration_minutes": 20,
    "greeting_message": "Assalomu alaykum, {member_name}! Guruhimizga xush kelibsiz!",
    "notify_on_mute": True
}

# In-memory storage for runtime configuration and data
# In a production bot, these would ideally be in a persistent database
admin_ids = {OWNER_ID}  # Initialize with Owner ID
blocking_enabled = True
bot_config = DEFAULT_BOT_CONFIG.copy()

blocked_keywords = {
    "reklama", "aksiya", "chegirma", "sotaman", "pul ishlash",
    "kriptovalyuta", "investitsiya", "daromad", "tez pul", "onlayn kazino",
    "stavka", "bukmeker", "bonus", "ro'yxatdan o'ting"
}
blocked_domains = {
    "example.com", "spamlink.ru", "badsite.org", "1xbet", "mostbet", "parimatch"
}
offensive_words = {
    "ahmoq", "jinni", "tentak"
}

# Structure: {(chat_id, user_id): unmute_timestamp}
muted_users = {}

