# This module is part of https://github.com/nabilanavab/ilovepdf
# Feel free to use and contribute to this project. Your contributions are welcome!
# copyright ©️ 2021 nabilanavab

file_name = "plugins/dm/__check__.py"

from plugins import *
from configs.db import *
from lang import langList
from pyrogram import enums
from configs.log import log
from plugins.utils import *
from configs.config import *
from .start import extract_data
from pyrogram.types import Message
from lang.__users__ import userLang
from configs.db import dataBASE, myID
from pyrogram.errors import UserNotParticipant
from pyrogram import Client as ILovePDF, filters

if dataBASE.MONGODB_URI:
    from database import db


async def stopBot(_, __, message: Message):
    if (message.chat.id in dm.ADMINS) and message.text == "/stop":
        return False
    return True if settings.STOP_BOT else False


_stop_bot = filters.create(stopBot)
@ILovePDF.on_message(_stop_bot & filters.incoming)
async def stop_bot(bot, message):
    try:
        lang_code = await util.getLang(message.chat.id)
        await message.reply_chat_action(enums.ChatAction.TYPING)
        if dataBASE.MONGODB_URI:  # CHECK IF USER IN DATABASE
            lang_code, referID, get_pdf, md5_str = await extract_data(
                f"{message.text}-"
            )
            await log.newUser(bot, message, lang_code, referID)
        trans_txt, trans_btn = await util.translate(
            text="_STOP", button="_STOP_CB", lang_code=lang_code
        )
        return await message.reply_photo(
            photo=images.WELCOME_PIC,
            reply_markup=trans_btn,
            caption=trans_txt.format(
                message.from_user.mention, myID[0].mention
            )
        )
    except Exception as Error:
        logger.exception("🐞 %s stop_bot: %s" % (file_name, Error))


# BANNED USER
async def bannedUsers(_, __, message: Message):
    if (
        (message.from_user.id in dm.BANNED_USERS)
        or ((dm.ADMIN_ONLY) and (message.from_user.id not in dm.ADMINS))
        or ((dataBASE.MONGODB_URI) and (message.from_user.id in BANNED_USR_DB))
    ):
        return True
    return False


banned_user = filters.create(bannedUsers)
@ILovePDF.on_message(filters.private & banned_user & filters.incoming)
async def bannedUsr(bot, message):
    try:
        lang_code = await util.getLang(message.chat.id)
        await message.reply_chat_action(enums.ChatAction.TYPING)
        # IF USER BANNED FROM DATABASE
        if message.from_user.id in BANNED_USR_DB:
            ban = await db.get_key(id=message.from_user.id, key="banned")
            trans_txt, trans_btn = await util.translate(
                text="BAN['UCantUseDB']", button="BAN['banCB']", lang_code=lang_code
            )
            return await message.reply_photo(
                photo=images.BANNED_PIC,
                reply_markup=trans_btn,
                quote=True,
                caption=trans_txt.format(message.from_user.mention, ban),
            )
        # IF USER BANNED FROM CONFIG.VAR
        trans_txt, trans_btn = await util.translate(
            text="BAN['UCantUse']", button="BAN['banCB']", lang_code=lang_code
        )
        return await message.reply_photo(
            photo=images.BANNED_PIC,
            reply_markup=trans_btn,
            quote=True,
            caption=trans_txt.format(message.from_user.mention),
        )
    except Exception as Error:
        logger.exception("🐞 %s bannedUsr: %s" % (file_name, Error))


#  BANNED GROUP 
async def bannedGroups(_, __, message: Message):
    if (
        (message.chat.id in group.BANNED_GROUP)
        or ((group.ADMIN_GROUP_ONLY) and (message.chat.id not in group.ADMIN_GROUPS))
        or ((dataBASE.MONGODB_URI) and (message.chat.id in BANNED_GRP_DB))
    ):
        return True
    return False


banned_group = filters.create(bannedGroups)
async def setDb(_, bot, message: Message):
    if (dataBASE.MONGODB_URI) and (message.chat.id not in GROUPS):
        await log.newUser(bot, message, False, False)
        GROUPS.append(message.chat.id)
    return True


set_db = filters.create(setDb)
@ILovePDF.on_message(filters.group & set_db & banned_group & filters.incoming)
async def bannedGrp(bot, message):
    try:
        lang_code = await util.getLang(message.chat.id)
        await message.reply_chat_action(enums.ChatAction.TYPING)
        if message.chat.id in BANNED_GRP_DB:
            ban = await db.get_key(id=message.chat.id, key="banned", typ="group")
            trans_txt, trans_btn = await util.translate(
                text="BAN['GroupCantUseDB']", button="BAN['banCB']", lang_code=lang_code
            )
            toPin = await message.reply_photo(
                photo=images.BANNED_PIC,
                reply_markup=trans_btn,
                quote=True,
                caption=trans_txt.format(message.chat.title, ban),
            )
        else:
            trans_txt, trans_btn = await util.translate(
                text="BAN['GroupCantUse']", button="BAN['banCB']", lang_code=lang_code
            )
            toPin = await message.reply_photo(
                photo=images.BANNED_PIC,
                reply_markup=trans_btn,
                caption=trans_txt.format(message.chat.title),
                quote=True,
            )
        try:
            await toPin.pin()
        except Exception:
            pass
        await bot.leave_chat(message.chat.id)
    except Exception as Error:
        logger.exception("🐞 %s bannedGrp: %s" % (file_name, Error))


#   IF FORCE SUBSCRIPTION
async def notSubscribed(_, bot, message: Message):
    if message.text and message.text.startswith("/start"):
        msg = message.text.split(" ")
        if "-" in message.text:
            lang_code, referID, get_pdf, md5_str = await extract_data(
                f"{message.text}-"
            )
            if lang_code and settings.MULTI_LANG_SUP and lang_code in langList:
                userLang[message.chat.id] = lang_code
        else:
            referID = None
        lang_code = await util.getLang(message.chat.id)
        if dataBASE.MONGODB_URI:  # CHECK IF USER IN DATABASE
            await log.newUser(bot, message, lang_code, referID)

    if len(invite_link) == 0:
        return False  # IF FORCE SUB. TREAT AS SUBSCRIBED
    else:
        try:
            userStatus = await bot.get_chat_member(
                str(settings.UPDATE_CHANNEL), message.from_user.id
            )
            if userStatus.status == "kicked":  # IF USER BANNED FROM CHANNEL
                return True
            return False
        except UserNotParticipant:
            return True
        except Exception as e:
            return True


not_subscribed = filters.create(notSubscribed)
@ILovePDF.on_message(filters.private & filters.incoming & not_subscribed)
async def non_subscriber(bot, message):
    try:
        lang_code = await util.getLang(message.chat.id)
        await message.reply_chat_action(enums.ChatAction.TYPING)
        if (
            message.text
            and message.text.startswith("/start")
            and ("-g" or "-m" in message.text)
        ):
            _lang_code, referID, get_pdf, md5_str = await extract_data(
                f"{message.text}-"
            )
            if get_pdf:
                code = f"-g{get_pdf}"
            elif md5_str:
                code = f"-m{md5_str}"
            else:
                code = ""
        else:
            code = ""
        tTXT, tBTN = await util.translate(
            text="BAN['Force']",
            button="BAN['ForceCB']",
            asString=True,
            lang_code=lang_code,
        )
        tBTN = await util.editDICT(inDir=tBTN, value=[invite_link[0], code])
        await message.reply_photo(
            photo=images.WELCOME_PIC,
            quote=True,
            caption=tTXT.format(message.from_user.first_name, message.from_user.id),
            reply_markup=await util.createBUTTON(btn=tBTN, order="11"),
        )
        if (
            settings.MULTI_LANG_SUP
            and message.from_user.language_code
            and message.from_user.language_code != "en"
            and lang_code == "eng"
        ):
            change, close = await util.translate(
                text="SETTINGS['lang']",
                button="RESTART['btn']",
                asString=True,
                lang_code=lang_code,
            )
            LANG = {
                langList[lang][1]: f"https://t.me/{myID[0].username}?start=-l{lang}"
                for lang in langList
            }
            LANG.update(close)
            BUTTON = await util.createBUTTON(
                btn=LANG, order=int(f"{((len(LANG)-1)//2)*'2'}{(len(LANG)-1)%2}1")
            )
            await message.reply(text=change, reply_markup=BUTTON)
        return
    except Exception as Error:
        logger.exception("🐞 %s non_subscriber: %s" % (file_name, Error))

# If you have any questions or suggestions, please feel free to reach out.
# Together, we can make this project even better, Happy coding!  XD
