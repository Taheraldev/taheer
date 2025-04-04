# This module is part of https://github.com/nabilanavab/ilovepdf
# Feel free to use and contribute to this project. Your contributions are welcome!
# copyright ©️ 2021 nabilanavab

file_name = "__main__.py"

iLovePDF = '''
  _   _                  ___  ___  ____ ™
 | | | |   _____ _____  | _ \|   \|  __| 
 | | | |__/ _ \ V / -_) |  _/| |) |  _|  
 |_| |___,\___/\_/\___| |_|  |___/|_|    
                         ❤ [Nabil A Navab] 
                         ❤ Email: nabilanavab@gmail.com
                         ❤ Telegram: @nabilanavab
'''

import asyncio, os
import shutil, sys
from pdf import works
from configs.db import *
from logger import logger
from pyromod import listen
from lang import __users__
from plugins.utils import *
from configs.log import log
from configs.beta import BETA
from configs.config import bot, settings, images
from pyrogram import Client as ILovePDF, errors
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand

if dataBASE.MONGODB_URI:
    from database import db

if not bot.API_TOKEN or not bot.API_HASH or not bot.API_ID:
    logger.debug(f"bot.API_TOKEN, bot.API_HASH, bot.API_ID : MANDATORY")
    sys.exit()

# تعريف دالة getLang للتحقق من لغة المستخدم
async def getLang(user_id: int) -> str:
    """
    تسترجع لغة المستخدم المحددة في __users__.userLang، 
    وإلا تُعيد اللغة الافتراضية من الإعدادات.
    """
    return __users__.userLang.get(user_id, settings.DEFAULT_LANG)

# PYROGRAM
class Bot(ILovePDF):
    def __init__(self):
        super().__init__(
            name="ILovePDF",
            api_id=bot.API_ID,
            api_hash=bot.API_HASH,
            bot_token=bot.API_TOKEN,
            plugins={"root": "plugins"},
        )

    async def start(self):
        if dataBASE.MONGODB_URI:
            # --- Loads Banned UsersId to List -----
            b_users, b_chats = await db.get_banned()
            BANNED_USR_DB.extend(b_users)
            BANNED_GRP_DB.extend(b_chats)

            beta_users = await db.get_beta()
            BETA.extend(beta_users)
            # ------- Loads UsersId with custom THUMBNAIL ---------
            users = await db.get_all_users()  # Get all users' Data
            async for user in users:
                if settings.MULTI_LANG_SUP:
                    lang = user.get("lang", False)
                    if lang and lang != settings.DEFAULT_LANG:
                        __users__.userLang[user.get("id")] = f"{lang}"
                if user.get("thumb", False):
                    CUSTOM_THUMBNAIL_U.append(user["id"])

            groups = await db.get_all_chats()
            async for group in groups:
                GROUPS.append(group["id"])
                if settings.MULTI_LANG_SUP:
                    lang = group.get("lang", False)
                    if lang and lang != settings.DEFAULT_LANG:
                        __users__.userLang[group.get("id")] = f"{lang}"
                if group.get("thumb", False):
                    CUSTOM_THUMBNAIL_C.append(group["id"])

            # -- Loads Other Necessary Data --
            users = await db.get_all_users()
            async for user in users:
                if user.get("api", False) or user.get("fname", False) or user.get("capt", False):
                    DATA[user.get("id")] = [0, 0, 0]
                    if user.get("api", False):
                        DATA[user.get("id")][0] = 1
                    if user.get("fname", False):
                        DATA[user.get("id")][1] = 1
                    if user.get("capt", False):
                        DATA[user.get("id")][2] = 1

        # -----> Telebot/Pyrogram Client Starting <-----
        try:
            await super().start()
        except errors.FloodWait as e:
            logger.debug(f"wait {e.value} seconds.. automatically restarting..")
            for remaining in range(e.value, 0, -10):
                await asyncio.sleep(10)
                if remaining % 10 == 0:
                    logger.debug(f"Remaining seconds: {remaining}")
            await super().start()

        myID.append(await app.get_me())
        command, _ = await util.translate(
            text="BOT_COMMAND", lang_code=settings.DEFAULT_LANG
        )
        await app.set_bot_commands(
            [BotCommand(i, command[i]) for i in command], language_code="en"
        )

        # -----> SETTING FORCE SUBSCRIPTION <-----
        if settings.UPDATE_CHANNEL:
            try:
                inviteLink = await app.get_chat(int(settings.UPDATE_CHANNEL))
                chanlCount = inviteLink.members_count
                if not inviteLink and inviteLink.username:
                    inviteLink = await app.create_chat_invite_link(int(settings.UPDATE_CHANNEL))
                    invite_link.append(inviteLink.invite_link)
                else:
                    inviteLink = f"https://telegram.dog/{inviteLink.username}"
                    invite_link.append(inviteLink)
            except errors.ChannelInvalid:
                settings.UPDATE_CHANNEL = False
                logger.debug("Bot is not admin in UPDATE_CHANNEL")
            except Exception as error:
                logger.debug(f"⚠️ FORCE SUBSCRIPTION ERROR : {error}", exc_info=True)

        logger.debug(
            f"\n"
            f"❤ BOT ID: {myID[0].id}\n"
            f"❤ BOT FILENAME: {myID[0].first_name}\n"
            f"❤ BOT USERNAME: {myID[0].username}\n\n"
            f"❤ SOURCE-CODE By: @nabilanavab 👑\n"
            f"❤ BOT CHANNEL: t.me/iLovePDF_bot\n\n"
            f"{iLovePDF}"
        )

        # ----> NOTIFY. BROKEN WORKS <----
        if settings.SEND_RESTART and len(works["u"]):
            for u in works["u"]:
                lang_code = await getLang(int(u))
                msg, btn = await translate(
                    text="RESTART['msg']", button="RESTART['btn']", lang_code=lang_code
                )
                await app.send_message(chat_id=int(u), text=msg, reply_markup=btn)
        if settings.SEND_RESTART and len(works["g"]):
            for g in works["g"]:
                await app.send_message(chat_id=int(g[0]), text=f"restarted.. {g[1]}")

        # -----> SETTING LOG CHANNEL <-----
        if log.LOG_CHANNEL:
            try:
                if settings.UPDATE_CHANNEL:
                    caption = (
                        f"{myID[0].first_name} started successfully...✅\n\n"
                        f"FORCED CHANNEL:\n"
                        f"invite_link: {str(invite_link[0]) if invite_link[0] is not None else '❌'}\n"
                        f"get_member : {str(chanlCount) if invite_link[0] is not None else '❌'}\n"
                    )
                else:
                    caption = f"{myID[0].first_name} started successfully...✅"
                if log.LOG_FILE and log.LOG_FILE[-4:] == ".log":
                    doc = f"./{log.LOG_FILE}"
                    markUp = InlineKeyboardMarkup(
                        [[InlineKeyboardButton("♻️ refresh log ♻️", callback_data="log")],
                         [InlineKeyboardButton("◍ Close ◍", callback_data="close|admin")]]
                    )
                else:
                    doc = images.THUMBNAIL_URL
                    markUp = InlineKeyboardMarkup(
                        [[InlineKeyboardButton("◍ close ◍", callback_data="close|admin")]]
                    )
                await app.send_document(
                    chat_id=int(log.LOG_CHANNEL),
                    document=doc,
                    caption=caption,
                    reply_markup=markUp,
                )
            except errors.ChannelInvalid:
                log.LOG_CHANNEL = False
                logger.debug("Bot is not admin in Log Channel")
            except Exception as error:
                logger.debug(f"⚠️ ERROR IN LOG CHANNEL - {error}", exc_info=True)

    async def stop(self, *args):
        await super().stop()

if __name__ == "__main__":
    work_path = os.path.join(os.path.abspath(os.getcwd()), "work", "nabilanavab")
    if os.path.exists(work_path):
        for chat in os.listdir(work_path):
            if chat.startswith("-100"):
                works["g"].append([chat, [user for user in os.listdir(os.path.join(work_path, chat))]])
            else:
                works["u"].append(chat)
        shutil.rmtree(os.path.join(os.path.abspath(os.getcwd()), "work"))
    os.makedirs(work_path, exist_ok=True)

    app = Bot()
    app.run()

# If you have any questions or suggestions, please feel free to reach out.
# Together, we can make this project even better, Happy coding! XD
