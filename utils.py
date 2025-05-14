import time
from datetime import timedelta
from aiogram import Bot
from aiogram.types import ChatPermissions, Message
from aiogram.utils.markdown import hbold # hbold is not used here, but kept for consistency if added later

import config
import logging

logger = logging.getLogger(__name__)

async def is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids

async def is_owner(user_id: int) -> bool:
    return user_id == config.OWNER_ID

async def get_user_status_in_chat(bot: Bot, chat_id: int, user_id: int) -> str:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status
    except Exception as e:
        logger.error(f"Error getting chat member status for {user_id} in {chat_id}: {e}")
        return "error"

async def mute_user_in_chat(bot: Bot, chat_id: int, user_id: int, duration_minutes: int, reason: str):
    try:
        until_timestamp = int(time.time() + duration_minutes * 60)
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=timedelta(minutes=duration_minutes)
        )
        config.muted_users[(chat_id, user_id)] = until_timestamp
        logger.info(f"User {user_id} muted in chat {chat_id} for {duration_minutes} minutes. Reason: {reason}")
        if config.bot_config["notify_on_mute"]:
            user_info = await bot.get_chat(user_id)
            await bot.send_message(chat_id, f"{user_info.mention_html()} {duration_minutes} daqiqaga 'mute' qilindi. Sabab: {reason}")
        return True
    except Exception as e:
        logger.error(f"Error muting user {user_id} in chat {chat_id}: {e}")
        return False

async def unmute_user_in_chat(bot: Bot, chat_id: int, user_id: int, manual_unmute: bool = False):
    try:
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_polls=True, can_send_other_messages=True,
                can_add_web_page_previews=True, can_invite_users=True
            )
        )
        if (chat_id, user_id) in config.muted_users:
            del config.muted_users[(chat_id, user_id)]
        logger.info(f"User {user_id} unmuted in chat {chat_id}. Manual: {manual_unmute}")
        if manual_unmute:
            user_info = await bot.get_chat(user_id)
            await bot.send_message(chat_id, f"{user_info.mention_html()} muddatidan oldin 'mute' rejimidan chiqarildi.")
        return True
    except Exception as e:
        logger.error(f"Error unmuting user {user_id} in chat {chat_id}: {e}")
        return False

async def manage_list_item(message: Message, item_type: str, item_list: set, action: str):
    if not await is_admin(message.from_user.id):
        return await message.reply("Ruxsat yo'q.")
    try:
        item = message.text.split(maxsplit=1)[1].lower()
        if action == "add":
            if item_type == "domain" and ("." not in item or " " in item):
                return await message.reply("Noto'g'ri domen formati.")
            item_list.add(item)
            await message.reply(f"{item_type.capitalize()} '{item}' ro'yxatga qo'shildi.")
        elif action == "remove":
            if item in item_list:
                item_list.remove(item)
                await message.reply(f"{item_type.capitalize()} '{item}' o'chirildi.")
            else:
                await message.reply(f"{item_type.capitalize()} '{item}' topilmadi.")
    except IndexError:
        await message.reply(f"Noto'g'ri format. Misol: /{action}_{item_type} <{item_type if item_type != 'offensive' else 'soz'}>")

