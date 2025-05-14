# -*- coding: utf-8 -*-
import logging
import time # Added for mute_info check in handle_message
from aiogram import Dispatcher, types, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold, hitalic, hcode
from aiogram.enums import ChatMemberStatus

import config
from utils import (is_admin, is_owner, mute_user_in_chat, unmute_user_in_chat,
                   get_user_status_in_chat, manage_list_item)

logger = logging.getLogger(__name__)

# Store active chats where the bot is an admin
active_chats = set() # In a production bot, this would ideally be in a persistent database

def setup_handlers(dp: Dispatcher, bot_instance: Bot): # Added type hint for bot_instance
    # --- Command Handlers ---
    @dp.message(CommandStart())
    async def send_welcome(message: types.Message):
        user_id = message.from_user.id
        if await is_admin(user_id):
            await admin_help(message) # Call the existing admin_help function
        else:
            await message.reply(f"Salom, {hbold(message.from_user.full_name)}! Men reklama va haqoratni bloklovchi botman.")

    @dp.message(Command("help_admin"))
    async def admin_help(message: types.Message):
        if not await is_admin(message.from_user.id):
            await message.reply("Sizda bu buyruqni ishlatish uchun ruxsat yo\\'q.")
            return

        panel_title = hbold("[Admin Panel]")

        admin_commands_list = [
            hitalic("/status") + " - Botning joriy holati.",
            hitalic("/toggle_blocking") + " - Bloklashni yoqish/o\\'chirish.",
            hbold("[Ro\\'yxatlarni Boshqarish]:"),
            "  " + hitalic("/add_keyword <soz>") + " - Kalit so\\'z qo\\'shish.",
            "  " + hitalic("/remove_keyword <soz>") + " - Kalit so\\'zni o\\'chirish.",
            "  " + hitalic("/list_keywords") + " - Kalit so\\'zlar ro\\'yxati.",
            "  " + hitalic("/add_domain <domen>") + " - Domen qo\\'shish.",
            "  " + hitalic("/remove_domain <domen>") + " - Domenni o\\'chirish.",
            "  " + hitalic("/list_domains") + " - Domenlar ro\\'yxati.",
            "  " + hitalic("/add_offensive <soz>") + " - Haqoratli so\\'z qo\\'shish.",
            "  " + hitalic("/remove_offensive <soz>") + " - Haqoratli so\\'zni o\\'chirish.",
            "  " + hitalic("/list_offensive") + " - Haqoratli so\\'zlar ro\\'yxati.",
            hbold("[Foydalanuvchilarni Boshqarish]:"),
            "  " + hitalic("/unmute <user_id>") + " - Foydalanuvchini \\'mute\\'dan chiqarish."
        ]

        help_text_parts = [panel_title, "\n".join(admin_commands_list)]

        if await is_owner(message.from_user.id):
            owner_commands_list = [
                "\n" + hbold("[Ega Sozlamalari]"),
                hbold("[Adminlarni Boshqarish]:"),
                "  " + hitalic("/add_admin <user_id>") + " - Yangi admin qo\\'shish.",
                "  " + hitalic("/remove_admin <user_id>") + " - Adminni o\\'chirish.",
                "  " + hitalic("/list_admins") + " - Adminlar ro\\'yxati.",
                hbold("[Bot Sozlamalari]:"),
                "  " + hitalic("/set_swear_mute <daqiqa>") + " - Haqorat uchun mute muddatini sozlash.",
                "  " + hitalic("/set_ad_mute <daqiqa>") + " - Reklama uchun mute muddatini sozlash.",
                "  " + hitalic("/set_greeting <xabar>") + " - Salomlashish xabarini sozlash.",
                "  " + hitalic("/toggle_mute_notify") + " - Mute bildirishnomasini yoqish/o\\'chirish.",
                hbold("[Guruhlar]:"),
                "  " + hitalic("/list_bot_groups") + " - Bot admin bo\\'lgan guruhlar ro\\'yxati."
            ]
            help_text_parts.append("\n".join(owner_commands_list))

        await message.reply("\n\n".join(help_text_parts))

    @dp.message(Command("list_bot_groups"))
    async def list_bot_groups_command(message: types.Message):
        if not await is_owner(message.from_user.id):
            return await message.reply("Faqat bot egasi bu buyruqni ishlata oladi.")

        if not active_chats:
            return await message.reply("Bot hozircha hech qaysi guruhda admin emas.")

        response_lines = [hbold("Bot Admin Bo\u2018lgan Guruhlar:")] # Using unicode escape for apostrophe
        for chat_id_item in active_chats:
            try:
                chat_info = await bot_instance.get_chat(chat_id_item)
                response_lines.append(f"- {hitalic(chat_info.title)} (ID: {hcode(str(chat_id_item))})")
            except Exception as e:
                logger.error(f"Could not get info for chat {chat_id_item}: {e}")
                response_lines.append(f"- Noma\\'lum guruh (ID: {hcode(str(chat_id_item))}) - xatolik")

        await message.reply("\n".join(response_lines))

    @dp.message(Command("set_swear_mute"))
    async def set_swear_mute_duration_command(message: types.Message):
        if not await is_owner(message.from_user.id):
            await message.reply("Faqat bot egasi bu sozlamani o\\'zgartira oladi.")
            return
        try:
            duration = int(message.text.split()[1])
            if 0 < duration <= 1440:
                config.bot_config["swear_mute_duration_minutes"] = duration
                await message.reply(f"Haqorat uchun mute muddati {duration} daqiqaga o\\'rnatildi.")
            else:
                await message.reply("Mute muddati 1 dan 1440 (24 soat) gacha bo\\'lishi kerak.")
        except (IndexError, ValueError):
            await message.reply("Noto\\'g\\'ri format. Misol: /set_swear_mute 30")

    @dp.message(Command("set_ad_mute"))
    async def set_ad_mute_duration_command(message: types.Message):
        if not await is_owner(message.from_user.id):
            await message.reply("Faqat bot egasi bu sozlamani o\\'zgartira oladi.")
            return
        try:
            duration = int(message.text.split()[1])
            if 0 < duration <= 1440:
                config.bot_config["ad_mute_duration_minutes"] = duration
                await message.reply(f"Reklama uchun mute muddati {duration} daqiqaga o\\'rnatildi.")
            else:
                await message.reply("Mute muddati 1 dan 1440 (24 soat) gacha bo\\'lishi kerak.")
        except (IndexError, ValueError):
            await message.reply("Noto\\'g\\'ri format. Misol: /set_ad_mute 20")

    @dp.message(Command("set_greeting"))
    async def set_greeting_command(message: types.Message):
        if not await is_owner(message.from_user.id):
            await message.reply("Faqat bot egasi bu sozlamani o\\'zgartira oladi.")
            return
        try:
            greeting = message.text.split(maxsplit=1)[1]
            if "{member_name}" not in greeting:
                await message.reply("Salomlashish xabarida {member_name} bo\\'lishi kerak.")
                return
            config.bot_config["greeting_message"] = greeting
            await message.reply(f"Yangi a\\'zolar uchun salomlashish xabari o\\'rnatildi: {hcode(greeting)}")
        except IndexError:
            await message.reply("Noto\\'g\\'ri format. Misol: /set_greeting Salom, {member_name}!")

    @dp.message(Command("toggle_mute_notify"))
    async def toggle_mute_notify_command(message: types.Message):
        if not await is_owner(message.from_user.id):
            await message.reply("Faqat bot egasi bu sozlamani o\\'zgartira oladi.")
            return
        config.bot_config["notify_on_mute"] = not config.bot_config["notify_on_mute"]
        status = "yoqildi" if config.bot_config["notify_on_mute"] else "o\\'chirildi"
        await message.reply(f"Mute haqida bildirishnoma yuborish {status}.")

    @dp.message(Command("add_admin"))
    async def add_admin_command(message: types.Message):
        if not await is_owner(message.from_user.id): return await message.reply("Faqat bot egasi admin qo\\'sha oladi.")
        try:
            new_admin_id = int(message.text.split()[1])
            config.admin_ids.add(new_admin_id)
            await message.reply(f"Foydalanuvchi {new_admin_id} adminlar ro\\'yxatiga qo\\'shildi.")
        except (IndexError, ValueError): await message.reply("Noto\\'g\\'ri format. Misol: /add_admin 123456789")

    @dp.message(Command("remove_admin"))
    async def remove_admin_command(message: types.Message):
        if not await is_owner(message.from_user.id): return await message.reply("Faqat bot egasi adminni o\\'chira oladi.")
        try:
            admin_to_remove_id = int(message.text.split()[1])
            if admin_to_remove_id == config.OWNER_ID: return await message.reply("Bot egasini o\\'chirib bo\\'lmaydi.")
            if admin_to_remove_id in config.admin_ids:
                config.admin_ids.remove(admin_to_remove_id)
                await message.reply(f"Foydalanuvchi {admin_to_remove_id} adminlardan o\\'chirildi.")
            else: await message.reply(f"Foydalanuvchi {admin_to_remove_id} admin emas.")
        except (IndexError, ValueError): await message.reply("Noto\\'g\\'ri format. Misol: /remove_admin 123456789")

    @dp.message(Command("list_admins"))
    async def list_admins_command(message: types.Message):
        if not await is_owner(message.from_user.id): return await message.reply("Faqat bot egasi ko\\'ra oladi.")
        admins_list_str = "\n".join(map(str, sorted(list(config.admin_ids))))
        await message.reply(hbold("Adminlar:") + f"\n{admins_list_str}" if config.admin_ids else "Adminlar yo\\'q.")

    @dp.message(Command("toggle_blocking"))
    async def toggle_blocking_command(message: types.Message):
        if not await is_admin(message.from_user.id): return await message.reply("Ruxsat yo\\'q.")
        config.blocking_enabled = not config.blocking_enabled
        status_text = "yoqildi" if config.blocking_enabled else "o\\'chirildi"
        await message.reply(f"Bloklash {status_text}.")

    @dp.message(Command("status"))
    async def status_command(message: types.Message):
        if not await is_admin(message.from_user.id): return await message.reply("Ruxsat yo\\'q.")
        status_text = "Yoqilgan" if config.blocking_enabled else "O\\'chirilgan"
        config_str = (
            hbold("Bot Holati:") + "\n"
            f"Bloklash: {hitalic(status_text)}\n"
            f"Blok. kalit so\\'zlar: {len(config.blocked_keywords)}\n"
            f"Blok. domenlar: {len(config.blocked_domains)}\n"
            f"Haqoratli so\\'zlar: {len(config.offensive_words)}\n"
            f"Haqorat mute: {config.bot_config['swear_mute_duration_minutes']} daq.\n"
            f"Reklama mute: {config.bot_config['ad_mute_duration_minutes']} daq.\n"
            f"Mute bildirishnomasi: {'Yoqilgan' if config.bot_config['notify_on_mute'] else 'Ochirilgan'}"
        )
        await message.reply(config_str)

    @dp.message(Command("add_keyword"))
    async def add_keyword_c(m: types.Message): await manage_list_item(m, "keyword", config.blocked_keywords, "add")
    @dp.message(Command("remove_keyword"))
    async def rem_keyword_c(m: types.Message): await manage_list_item(m, "keyword", config.blocked_keywords, "remove")
    @dp.message(Command("list_keywords"))
    async def list_keywords_c(m: types.Message):
        if not await is_admin(m.from_user.id):
            return await m.reply("Ruxsat yo\\'q.")
        header = hbold("Blok. kalit so\\'zlar:")
        if config.blocked_keywords:
            items_str = "\n".join(sorted(list(config.blocked_keywords)))
            reply_text = f"{header}\n{items_str}"
        else:
            reply_text = "Kalit so\\'zlar yo\\'q."
        await m.reply(reply_text)

    @dp.message(Command("add_domain"))
    async def add_domain_c(m: types.Message): await manage_list_item(m, "domain", config.blocked_domains, "add")
    @dp.message(Command("remove_domain"))
    async def rem_domain_c(m: types.Message): await manage_list_item(m, "domain", config.blocked_domains, "remove")
    @dp.message(Command("list_domains"))
    async def list_domains_c(m: types.Message):
        if not await is_admin(m.from_user.id):
            return await m.reply("Ruxsat yo\\'q.")
        header = hbold("Blok. domenlar:")
        if config.blocked_domains:
            items_str = "\n".join(sorted(list(config.blocked_domains)))
            reply_text = f"{header}\n{items_str}"
        else:
            reply_text = "Domenlar yo\\'q."
        await m.reply(reply_text)

    @dp.message(Command("add_offensive"))
    async def add_offensive_c(m: types.Message): await manage_list_item(m, "offensive", config.offensive_words, "add")
    @dp.message(Command("remove_offensive"))
    async def rem_offensive_c(m: types.Message): await manage_list_item(m, "offensive", config.offensive_words, "remove")
    @dp.message(Command("list_offensive"))
    async def list_offensive_c(m: types.Message):
        if not await is_admin(m.from_user.id):
            return await m.reply("Ruxsat yo\\'q.")
        header = hbold("Haqoratli so\\'zlar:")
        if config.offensive_words:
            items_str = "\n".join(sorted(list(config.offensive_words)))
            reply_text = f"{header}\n{items_str}"
        else:
            reply_text = "Haqoratli so\\'zlar yo\\'q."
        await m.reply(reply_text)

    @dp.message(Command("unmute"))
    async def unmute_command(message: types.Message):
        if not await is_admin(message.from_user.id):
            return await message.reply("Sizda bu buyruqni ishlatish uchun ruxsat yo\\'q.")
        try:
            user_to_unmute_id = int(message.text.split()[1])
            chat_admins = await bot_instance.get_chat_administrators(message.chat.id)
            bot_member = next((admin for admin in chat_admins if admin.user.id == bot_instance.id), None)
            if not (bot_member and bot_member.can_restrict_members):
                return await message.reply("Bot bu guruhda foydalanuvchilarni \\'mute\\' qila olmaydi yoki \\'mute\\'dan chiqara olmaydi (yetarli huquqlar yo\\'q).")
            await unmute_user_in_chat(bot_instance, message.chat.id, user_to_unmute_id, manual_unmute=True)
        except (IndexError, ValueError):
            await message.reply("Noto\\'g\\'ri format. Misol: /unmute 123456789")
        except Exception as e:
            await message.reply(f"Foydalanuvchini \\'mute\\'dan chiqarishda xatolik: {e}")
            logger.error(f"Error in /unmute command: {e}")

    @dp.my_chat_member(F.chat.type.in_(["group", "supergroup"]) & F.new_chat_member.status.in_([ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]))
    async def bot_added_to_group_handler(update: types.ChatMemberUpdated, bot: Bot):
        chat_id = update.chat.id
        chat_title = update.chat.title if update.chat.title else "Noma'lum Guruh"
        if update.new_chat_member.user.id == bot.id:
            if update.new_chat_member.status == ChatMemberStatus.ADMINISTRATOR:
                active_chats.add(chat_id)
                logger.info(f"Bot was made ADMIN in chat: {chat_title} ({chat_id})")
                chat_title_h = hbold(chat_title)
                chat_id_h = hcode(str(chat_id))
                admin_h = hbold('ADMIN')
                owner_message_admin = f"Bot {chat_title_h} ({chat_id_h}) guruhida {admin_h} bo\\'ldi!"
                await bot.send_message(config.OWNER_ID, owner_message_admin)
            elif update.new_chat_member.status == ChatMemberStatus.MEMBER:
                active_chats.add(chat_id)
                logger.info(f"Bot was ADDED to chat: {chat_title} ({chat_id})")
                chat_title_h = hbold(chat_title)
                chat_id_h = hcode(str(chat_id))
                owner_message_member = f"Bot {chat_title_h} ({chat_id_h}) guruhiga qo\\'shildi (admin emas). Admin huquqlarini bering."
                await bot.send_message(config.OWNER_ID, owner_message_member)

    @dp.my_chat_member(F.chat.type.in_(["group", "supergroup"]) & F.new_chat_member.status == ChatMemberStatus.LEFT)
    async def bot_left_group_handler(update: types.ChatMemberUpdated, bot: Bot):
        chat_id = update.chat.id
        chat_title = update.chat.title if update.chat.title else "Noma'lum Guruh"
        if update.new_chat_member.user.id == bot.id:
            if chat_id in active_chats:
                active_chats.remove(chat_id)
            logger.info(f"Bot was REMOVED from chat: {chat_title} ({chat_id})")
            chat_title_h = hbold(chat_title)
            chat_id_h = hcode(str(chat_id))
            owner_message_left = f"Bot {chat_title_h} ({chat_id_h}) guruhidan chiqarildi."
            await bot.send_message(config.OWNER_ID, owner_message_left)

    @dp.message(F.new_chat_members)
    async def greet_new_members(message: types.Message, bot: Bot):
        for member in message.new_chat_members:
            if member.id == bot.id:
                pass
            else:
                greeting = config.bot_config["greeting_message"].format(member_name=hbold(member.full_name))
                await message.answer(greeting)
                logger.info(f"New member {member.full_name} (ID: {member.id}) joined chat {message.chat.id}")

    @dp.message(F.chat.type.in_(["group", "supergroup"]))
    async def handle_message(message: types.Message, bot: Bot):
        if not message.from_user: return
        user_id = message.from_user.id
        chat_id = message.chat.id

        if chat_id not in active_chats:
            try:
                chat_member_bot = await bot.get_chat_member(chat_id, bot.id)
                if chat_member_bot.status == ChatMemberStatus.ADMINISTRATOR:
                    active_chats.add(chat_id)
            except Exception:
                pass

        mute_info = config.muted_users.get((chat_id, user_id))
        if mute_info and time.time() < mute_info:
            try: await message.delete(); logger.info(f"Deleted message from muted user {user_id} in {chat_id}")
            except Exception: pass
            return
        elif mute_info and time.time() >= mute_info:
            if (chat_id, user_id) in config.muted_users:
                del config.muted_users[(chat_id, user_id)]

        if not config.blocking_enabled: return
        if await is_admin(user_id): return

        bot_chat_member = await bot.get_chat_member(chat_id, bot.id)
        if bot_chat_member.status != ChatMemberStatus.ADMINISTRATOR:
            return

        can_delete = bot_chat_member.can_delete_messages
        can_restrict = bot_chat_member.can_restrict_members

        text_to_check = (message.text or message.caption or "").lower()
        action_taken = False

        for swear in config.offensive_words:
            if swear in text_to_check:
                if can_delete:
                    try: await message.delete(); logger.info(f"Deleted offensive message from {user_id} in {chat_id}")
                    except Exception as e_del: logger.error(f"Failed to delete offensive msg: {e_del}")
                if can_restrict: await mute_user_in_chat(bot, chat_id, user_id, config.bot_config["swear_mute_duration_minutes"], "haqoratli so\\'z")
                action_taken = True
                break
        if action_taken: return

        ad_reason = None
        if message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    url = entity.url if entity.type == "text_link" else message.text[entity.offset : entity.offset + entity.length]
                    for domain in config.blocked_domains:
                        if domain in url.lower(): ad_reason = f"bloklangan domen ({domain})"; break
                    if not ad_reason: ad_reason = "havola"
                    break

        if not ad_reason:
            for keyword in config.blocked_keywords:
                if keyword in text_to_check:
                    ad_reason = f"bloklangan kalit so\\'z ('{keyword}')"
                    break

        if not ad_reason and message.forward_from_chat and message.forward_from_chat.type == "channel":
            ad_reason = "kanaldan yuborilgan xabar"

        if not ad_reason and len(text_to_check) > 20:
            uppercase_chars = sum(1 for char in text_to_check if char.isupper())
            if (uppercase_chars / len(text_to_check)) > 0.7:
                ad_reason = "xabar formati (ko\\'p bosh harflar)"

        if ad_reason:
            if can_delete:
                try: await message.delete(); logger.info(f"Deleted ad message ({ad_reason}) from {user_id} in {chat_id}")
                except Exception as e_del_ad: logger.error(f"Failed to delete ad msg: {e_del_ad}")
            if can_restrict: await mute_user_in_chat(bot, chat_id, user_id, config.bot_config["ad_mute_duration_minutes"], f"reklama ({ad_reason})")
            return

        if can_delete:
            try: await message.delete(); logger.info(f"Deleted message from {user_id} in {chat_id}")
            except Exception as e_del: logger.error(f"Failed to delete msg: {e_del}")