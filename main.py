import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties # Added for aiogram 3.7.0+

import config
from handlers import setup_handlers

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main() -> None:
    if not config.API_TOKEN:
        logger.error("Xatolik: API_TOKEN topilmadi. .env faylini tekshiring.")
        return
    if not config.OWNER_ID:
        logger.error("Xatolik: OWNER_ID topilmadi. .env faylini tekshiring.")
        return

    # Bot Initialization - Updated for aiogram 3.7.0+
    bot_properties = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(token=config.API_TOKEN, default=bot_properties)
    dp = Dispatcher()

    # Setup handlers
    setup_handlers(dp, bot) # Pass bot instance to handlers if needed for operations like get_chat_administrators

    logger.info(f"Bot ishga tushmoqda... Owner ID: {config.OWNER_ID}, Admins: {config.admin_ids}")
    
    # Start polling
    try:
        # await bot.delete_webhook(drop_pending_updates=True) # Optional: clear pending updates
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

