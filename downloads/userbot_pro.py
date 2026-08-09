# -*- coding: utf-8 -*-
import asyncio
import os
import random
import re
import json
import sys
import subprocess
import time
import csv
import logging
import html
import shutil
from datetime import datetime, timedelta
from platform import python_version

# ========== مكتبات خارجية ==========
from telethon import TelegramClient, events, Button, version
from telethon.sessions import StringSession
from telethon.tl.types import (
    MessageMediaPhoto, 
    ChatBannedRights, 
    ChannelParticipantsAdmins, 
    ChannelParticipantCreator, 
    ChannelParticipantAdmin, 
    InputPeerUser, 
    MessageEntityMentionName,
    ChannelParticipantsKicked,
    ChatAdminRights,
    InputChatPhotoEmpty,
    User,
    InputWebDocument
)
from telethon.errors import (
    FloodWaitError, 
    PhoneNumberInvalidError, 
    PhoneCodeInvalidError, 
    SessionPasswordNeededError, 
    UserAlreadyParticipantError, 
    UserPrivacyRestrictedError, 
    UserNotMutualContactError,
    BadRequestError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
    UserAdminInvalidError,
    UserIdInvalidError,
    YouBlockedUserError,
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
    MessageNotModifiedError
)
from telethon.tl.functions.account import UpdateProfileRequest, GetPrivacyRequest
from telethon.tl.functions.channels import (
    EditBannedRequest, 
    InviteToChannelRequest, 
    GetFullChannelRequest, 
    GetParticipantsRequest,
    EditAdminRequest,
    EditPhotoRequest,
    GetAdminedPublicChannelsRequest,
    UpdateUsernameRequest,
    CreateChannelRequest
)
from telethon.tl.functions.messages import (
    GetFullChatRequest, 
    GetHistoryRequest, 
    ImportChatInviteRequest as Get,
    EditChatDefaultBannedRightsRequest,
    CheckChatInviteRequest
)
from telethon.tl.functions.phone import (
    CreateGroupCallRequest as startvc,
    DiscardGroupCallRequest as stopvc,
    GetGroupCallRequest as getvc,
    InviteToGroupCallRequest as invitetovc
)
from telethon.tl.functions.photos import GetUserPhotosRequest, DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest, GetBlockedRequest
from telethon.utils import get_input_location, get_display_name, resolve_bot_file_id
from telethon.events import CallbackQuery

# ========== مكتبات خارجية ==========
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None
    print("Pillow غير مثبت - سيتم تعطيل ميزات الصور")

try:
    from pySmartDL import SmartDL
except ImportError:
    SmartDL = None
    print("pySmartDL غير مثبت")

try:
    from requests import get
except ImportError:
    get = None
    print("requests غير مثبت")

try:
    from fake_useragent import UserAgent
except ImportError:
    UserAgent = None
    print("fake_useragent غير مثبت")

# ========== خادم ويب ==========
try:
    from aiohttp import web
except ImportError:
    web = None
    print("aiohttp غير مثبت - سيتم تعطيل خادم الويب")

# ========== heroku3 ==========
try:
    import heroku3
except ImportError:
    heroku3 = None
    print("heroku3 غير مثبت - سيتم تعطيل أوامر هيروكو")

# ========== urllib3 ==========
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    urllib3 = None

# ========== validators ==========
try:
    from validators.url import url
except ImportError:
    url = None

# ========== urlextract ==========
try:
    from urlextract import URLExtract
    extractor = URLExtract()
except ImportError:
    URLExtract = None
    extractor = None

# ========== ملفات الإعدادات ==========
CONFIG_FILE = "config.json"
GLOBALS_FILE = "globals.json"
LOCKS_FILE = "locks.json"
MUTE_FILE = "mute.json"
NO_LOG_FILE = "no_log_pms.json"
GBAN_FILE = "gban.json"
SUDOS_FILE = "sudos.json"
PMPERMIT_FILE = "pmpermit.json"

# ========== تحميل الإعدادات ==========
def load_config():
    default_config = {
        "api_id": 0,
        "api_hash": "",
        "session_string": "",
        "bot_token": "",
        "time_enabled": False,
        "saudi_offset_hours": 3,
        "quotes": [
            "النجاح ليس نهائياً، والفشل ليس قاتلاً: الشجاعة للاستمرار هي ما يهم.",
            "كن التغيير الذي تريد رؤيته في العالم.",
            "الحياة ليست عن إيجاد الذات، الحياة عن خلق الذات.",
            "المستقبل لأولئك الذين يؤمنون بجمال أحلامهم.",
            "لا تخف من الفشل، اخشَ عدم المحاولة.",
            "أفضل طريقة لبدء المستقبل هي صنعه.",
            "الطريقة الوحيدة للقيام بعمل عظيم هي أن تحب ما تفعله.",
            "لا تضيع وقتك في الحلم بالنجاح، اعمل من أجله.",
            "الصبر مفتاح الفرج، والمثابرة طريق النجاح.",
            "كل يوم هو فرصة جديدة لتغيير حياتك."
        ],
        "download_settings": {
            "prefer_ffmpeg": True,
            "addmetadata": True,
            "geo-bypass": True,
            "nocheckcertificate": True
        }
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
            return default_config
    else:
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            print("تم إنشاء ملف الإعدادات config.json")
        except Exception as e:
            print(f"خطأ في حفظ الإعدادات: {e}")
        return default_config

CONFIG = load_config()

# ========== دوال المتغيرات العامة ==========
def load_globals():
    if os.path.exists(GLOBALS_FILE):
        try:
            with open(GLOBALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_globals(data):
    with open(GLOBALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def gvarstatus(key):
    data = load_globals()
    return data.get(key)

def addgvar(key, value):
    data = load_globals()
    data[key] = value
    save_globals(data)

def delgvar(key):
    data = load_globals()
    if key in data:
        del data[key]
        save_globals(data)

# ========== دوال المتحكمين (SUDOS) ==========
def load_sudos():
    if os.path.exists(SUDOS_FILE):
        try:
            with open(SUDOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_sudos(data):
    with open(SUDOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_sudo(user_id):
    sudos = load_sudos()
    return user_id in sudos

def add_sudo(user_id):
    sudos = load_sudos()
    if user_id not in sudos:
        sudos.append(user_id)
        save_sudos(sudos)
        return True
    return False

def remove_sudo(user_id):
    sudos = load_sudos()
    if user_id in sudos:
        sudos.remove(user_id)
        save_sudos(sudos)
        return True
    return False

def get_sudos():
    return load_sudos()

# ========== دوال PMPERMIT ==========
def load_pmpermit():
    if os.path.exists(PMPERMIT_FILE):
        try:
            with open(PMPERMIT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_pmpermit(data):
    with open(PMPERMIT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_approved(user_id):
    return user_id in load_pmpermit()

def approve_user(user_id):
    data = load_pmpermit()
    if user_id not in data:
        data.append(user_id)
        save_pmpermit(data)
        return True
    return False

def disapprove_user(user_id):
    data = load_pmpermit()
    if user_id in data:
        data.remove(user_id)
        save_pmpermit(data)
        return True
    return False

def get_approved():
    return load_pmpermit()

# ========== دوال الأقفال ==========
def load_locks():
    if os.path.exists(LOCKS_FILE):
        try:
            with open(LOCKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_locks(data):
    with open(LOCKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_locks(chat_id):
    data = load_locks()
    return data.get(str(chat_id), {})

def is_locked(chat_id, lock_type):
    data = load_locks()
    return data.get(str(chat_id), {}).get(lock_type, False)

def update_lock(chat_id, lock_type, value):
    data = load_locks()
    if str(chat_id) not in data:
        data[str(chat_id)] = {}
    data[str(chat_id)][lock_type] = value
    save_locks(data)

# ========== دوال الكتم ==========
def load_mutes():
    if os.path.exists(MUTE_FILE):
        try:
            with open(MUTE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_mutes(data):
    with open(MUTE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_muted(chat_id, user_id):
    data = load_mutes()
    return data.get(str(chat_id), {}).get(str(user_id), False)

def mute_user(chat_id, user_id):
    data = load_mutes()
    if str(chat_id) not in data:
        data[str(chat_id)] = {}
    data[str(chat_id)][str(user_id)] = True
    save_mutes(data)

def unmute_user(chat_id, user_id):
    data = load_mutes()
    if str(chat_id) in data and str(user_id) in data[str(chat_id)]:
        del data[str(chat_id)][str(user_id)]
        save_mutes(data)

# ========== دوال GBan ==========
def load_gbans():
    if os.path.exists(GBAN_FILE):
        try:
            with open(GBAN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_gbans(data):
    with open(GBAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_gbanned(user_id):
    data = load_gbans()
    return data.get(str(user_id), False)

def gban_user(user_id, reason=None):
    data = load_gbans()
    data[str(user_id)] = reason or "No reason"
    save_gbans(data)

def ungban_user(user_id):
    data = load_gbans()
    if str(user_id) in data:
        del data[str(user_id)]
        save_gbans(data)

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", CONFIG.get("api_id", 0)))
API_HASH = os.environ.get("API_HASH", CONFIG.get("api_hash", ""))
SESSION = os.environ.get("SESSION_STRING", CONFIG.get("session_string", ""))
BOT_TOKEN = os.environ.get("BOT_TOKEN", CONFIG.get("bot_token", ""))

if not API_ID or not API_HASH:
    raise RuntimeError(
        "إعدادات تيليجرام ناقصة: عيّن API_ID و API_HASH في Render Environment Variables "
        "أو داخل config.json قبل التشغيل."
    )

# ========== متغيرات عامة ==========
# Render / Production:
# API_ID, API_HASH, SESSION_STRING, BOT_TOKEN (اختياري) تُقرأ من Environment Variables.
# لا تضع التوكن أو StringSession داخل GitHub.
StartTime = time.time()
JMVERSION = "1.0.0"
time_enabled = CONFIG.get("time_enabled", False)
SAUDI_OFFSET = timedelta(hours=CONFIG.get("saudi_offset_hours", 3))
QUOTES = CONFIG.get("quotes", [])
DEFAULTUSER = gvarstatus("ALIVE_NAME") or "المستخدم"
CHANGE_TIME = int(gvarstatus("CHANGE_TIME")) if gvarstatus("CHANGE_TIME") else 60
BOTLOG = False
BOTLOG_CHATID = None
Config = type('Config', (), {
    'PM_LOGGER_GROUP_ID': -100,
    'ALIVE_ET': 'فحص',
    'A_PIC': None,
    'COMMAND_HAND_LER': '.',
    'TG_BOT_USERNAME': None
})()

# ========== متغيرات البوت المساعد ==========
tgbot = None
my_bot = None

# ========== متغيرات التثبيت ==========
install_waiting = False
install_user_id = None
install_phone = None
install_client = None
install_step = "phone"
install_hash = None
install_password = None

# ========== متغيرات التنصيب بالجلسة ==========
waiting_for_session = False
session_user_id = None

# ========== متغيرات الوقتية ==========
digitalpic_running = False
autoname_running = False
autobio_running = False
repself = True

# ========== إعدادات التحميل ==========
ytd = {
    "prefer_ffmpeg": CONFIG["download_settings"].get("prefer_ffmpeg", True),
    "addmetadata": CONFIG["download_settings"].get("addmetadata", True),
    "geo-bypass": CONFIG["download_settings"].get("geo-bypass", True),
    "nocheckcertificate": CONFIG["download_settings"].get("nocheckcertificate", True),
    "postprocessors": [{"key": "FFmpegMetadata"}],
}

# ========== حقوق الحظر ==========
BANNED_RIGHTS = ChatBannedRights(
    until_date=None, 
    view_messages=True, 
    send_messages=True, 
    send_media=True, 
    send_stickers=True, 
    send_gifs=True, 
    send_games=True, 
    send_inline=True, 
    embed_links=True
)
UNBAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=False)

# ========== متغيرات الصيد ==========
a = "qwertyuiopassdfghjklzxcvbnm"
b = "1234567890"
e = "qwertyuiopassdfghjklzxcvbnm1234567890"
trys, trys2 = [0], [0]
isclaim = ["off"]
isauto = ["off"]

# ========== متغيرات PMPERMIT ==========
COUNT_PM = {}
LASTMSG = {}
WARN_MSGS = {}
U_WARNS = {}
_not_approved = {}
_to_delete = {}

UND = "**⎆ يجب عليك انتظـار رد مالـك الحسـاب 🧸\n ⎆ وإن قمت بالتكرار سوف أقوم بحظرك**"
UNS = "**⌔∮  لـقد أخبرتك ألّا تُـكـرر أرسـال الرسـائل\n❃ يبـدو أنـك لا تُحـسن الـقراءة سيتم حظـرك  :)**" 
NO_REPLY = "**⎆ يجب عليك الرد على المستخدم أو في الخاص.**"

PMPIC = gvarstatus("PMPIC")
LOG_CHAT = gvarstatus("LOG_CHAT")
PMSETTING = gvarstatus("PMSETTING")
AUTOAPPROVE = gvarstatus("AUTOAPPROVE")
PMWARNS = int(gvarstatus("PMWARNS") or 4)
MOVE_ARCHIVE = gvarstatus("MOVE_ARCHIVE")

UNAPPROVED_MSG = "**نظام حماية تيبثـون الخاص بـ {ON}!**\n\n{UND}\n\nلديك {warn}/{twarn} تحذيرات"
if gvarstatus("PM_TEXT"):
    UNAPPROVED_MSG = (
        "**نظام حماية تيبثـون الخاص بـ {ON}!**\n\n"
        + gvarstatus("PM_TEXT")
        + "\n\nلديك {warn}/{twarn} تحذيرات"
    )

def update_pm(userid, message, warns_given):
    try:
        WARN_MSGS.update({userid: message})
    except KeyError:
        pass
    try:
        U_WARNS.update({userid: warns_given})
    except KeyError:
        pass

async def delete_pm_warn_msgs(chat: int):
    try:
        await _to_delete[chat].delete()
    except KeyError:
        pass

# ========== إنشاء عميل ==========
if SESSION:
    print("جاري استخدام الجلسة المخزنة...")
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
else:
    print("لا توجد جلسة! استخدم أمر التنصيب.")
    client = TelegramClient(StringSession(), API_ID, API_HASH)

# ========== دوال مساعدة ==========
async def edit_or_reply(event, text):
    if event.out:
        return await event.edit(text)
    return await event.reply(text)

async def edit_delete(event, text, time=5):
    msg = await edit_or_reply(event, text)
    await asyncio.sleep(time)
    await msg.delete()

async def get_user_from_event(event):
    user = None
    try:
        if event.reply_to_msg_id:
            try:
                previous_message = await event.get_reply_message()
                if previous_message and previous_message.sender_id:
                    user = await event.client.get_entity(previous_message.sender_id)
                    return user, None
            except:
                pass
        
        if hasattr(event, 'pattern_match') and event.pattern_match:
            input_str = event.pattern_match.group(1)
            if input_str:
                input_str = input_str.strip()
                try:
                    if input_str.isdigit():
                        user = await event.client.get_entity(int(input_str))
                    else:
                        user = await event.client.get_entity(input_str)
                    return user, input_str
                except:
                    pass
        
        if event.sender_id:
            user = await event.client.get_entity(event.sender_id)
            return user, None
        
        return None, None
    except Exception as e:
        print(f"خطأ في get_user_from_event: {e}")
        return None, None

async def is_owner(event):
    try:
        me = await event.client.get_me()
        sender = await event.get_sender()
        return sender.id == me.id or is_sudo(sender.id)
    except:
        return False

async def update_name(first_name, last_name=None):
    try:
        request = UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name or ""
        )
        await client(request)
        return True
    except Exception as e:
        print(f"خطأ في تحديث الاسم: {e}")
        return False

def save_config():
    try:
        CONFIG["time_enabled"] = time_enabled
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(CONFIG, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"خطأ في حفظ الإعدادات: {e}")
        return False

async def reply_id(event):
    if event.reply_to_msg_id:
        return event.reply_to_msg_id
    return None

def mention(user):
    if hasattr(user, 'first_name'):
        return f"[{user.first_name}](tg://user?id={user.id})"
    return f"[مستخدم](tg://user?id={user.id})"

def inline_mention(user, html=False):
    if hasattr(user, 'first_name'):
        name = user.first_name
    else:
        name = "مستخدم"
    if html:
        return f'<a href="tg://user?id={user.id}">{name}</a>'
    return f"[{name}](tg://user?id={user.id})"

async def get_readable_time(seconds):
    count = 0
    up_time = ""
    time_list = []
    while count < 4:
        count += 1
        if count == 1:
            if seconds > 0:
                time_list.append(f"{int(seconds)} ثانية")
        elif count == 2:
            minutes = seconds // 60
            if minutes > 0:
                time_list.append(f"{int(minutes)} دقيقة")
        elif count == 3:
            hours = seconds // 3600
            if hours > 0:
                time_list.append(f"{int(hours)} ساعة")
        elif count == 4:
            days = seconds // 86400
            if days > 0:
                time_list.append(f"{int(days)} يوم")
        seconds %= 86400
    if len(time_list) >= 2:
        time_list = time_list[:2]
        up_time = " ".join(time_list[::-1])
    elif len(time_list) == 1:
        up_time = time_list[0]
    else:
        up_time = "0 ثانية"
    return up_time

def check_data_base_heal_th():
    return "✅", "تعمل بنجاح"

def media_type(message):
    if message and message.media:
        if message.photo:
            return "صورة"
        if message.document:
            if message.document.mime_type:
                if "audio" in message.document.mime_type:
                    return "صوت"
                if "video" in message.document.mime_type:
                    return "فيديو"
                if "image" in message.document.mime_type:
                    return "صورة"
            return "ملف"
        if message.sticker:
            return "ملصق"
        if message.gif:
            return "متحركة"
        if message.video:
            return "فيديو"
        if message.voice:
            return "بصمة"
        if message.audio:
            return "صوت"
        if message.contact:
            return "جهة اتصال"
        if message.location:
            return "موقع"
        if message.venue:
            return "مكان"
        if message.poll:
            return "استطلاع"
    return None

def get_saudi_time():
    utc_now = datetime.utcnow()
    saudi_time = utc_now + SAUDI_OFFSET
    return saudi_time

# =====================================================================
#                        تشغيل البوت المساعد
# =====================================================================

async def start_bot():
    global tgbot, my_bot
    try:
        if BOT_TOKEN:
            tgbot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
            my_bot = await tgbot.get_me()
            print(f"✅ البوت المساعد يعمل كـ: {my_bot.first_name} (ID: {my_bot.id})")
            return True
        return False
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت المساعد: {e}")
        return False

# =====================================================================
#                        دوال الصيد
# =====================================================================

def check_user(username):
    try:
        import requests
        from fake_useragent import UserAgent
        url = "https://t.me/" + str(username)
        ua = UserAgent()
        headers = {"User-Agent": ua.random, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}
        session = requests.Session()
        response = session.get(url, headers=headers)
        return response.text.find('If you have <strong>Telegram</strong>, you can contact <a class="tgme_username_link"') >= 0
    except:
        return False

def gen_user(choice):
    if choice == "ثلاثي":
        c = random.choices(a)
        d = random.choices(b)
        s = random.choices(e)
        f = [c[0], "_", d[0], "_", s[0]]
        username = "".join(f)
    elif choice == "خماسي":
        c = d = random.choices(a)
        d = random.choices(b)
        f = [c[0], c[0], c[0], c[0], d[0]]
        random.shuffle(f)
        username = "".join(f)
    elif choice == "خماسي حرفين":
        c = random.choices(a)
        d = random.choices(e)
        f = [c[0], d[0], c[0], c[0], d[0]]
        random.shuffle(f)
        username = "".join(f)
    elif choice == "سداسي":
        c = d = random.choices(a)
        d = random.choices(e)
        f = [c[0], c[0], c[0], c[0], c[0], d[0]]
        random.shuffle(f)
        username = "".join(f)
    elif choice == "سداسي حرفين":
        c = d = random.choices(a)
        d = random.choices(b)
        f = [c[0], d[0], c[0], c[0], c[0], d[0]]
        random.shuffle(f)
        username = "".join(f)
    elif choice == "سباعي":
        c = d = random.choices(a)
        d = random.choices(b)
        f = [c[0], c[0], c[0], c[0], d[0], c[0], c[0]]
        random.shuffle(f)
        username = "".join(f)
    elif choice == "بوتات":
        c = random.choices(a)
        d = random.choices(e)
        s = random.choices(e)
        f = [c[0], s[0], d[0]]
        username = "".join(f) + "bot"
    elif choice == "تيست":
        c = d = random.choices(a)
        d = random.choices(b)
        f = [c[0], d[0], c[0], d[0], d[0], c[0], c[0], d[0], c[0], d[0]]
        random.shuffle(f)
        username = "".join(f)
    else:
        raise ValueError("Invalid choice for username generation.")
    return username

# =====================================================================
#                        أَمْرُ فَحْص
# =====================================================================

ALIVE_ET = Config.ALIVE_ET or "فحص"

@client.on(events.NewMessage(pattern=rf'^{ALIVE_ET}$'))
async def amireallyalive(event):
    if not await is_owner(event):
        return
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time.time() - StartTime))
    start = datetime.now()
    await edit_or_reply(event, "يتـم التـأكـد انتـظر قليلا رجاءا")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    _, check_sgnirts = check_data_base_heal_th()
    EMOJI = gvarstatus("ALIVE_EMOJI") or "✇ ◅"
    ALIVE_TEXT = gvarstatus("ALIVE_TEXT") or "سورس عبود يعمل ✓"
    RR7_IMG = gvarstatus("ALIVE_PIC") or Config.A_PIC
    me = await event.client.get_me()
    temp = """{ALIVE_TEXT}
{EMOJI} قاعدة البيانات : تعمل بنجاح ✓
{EMOJI} إصدار التيليثون : {telever}
{EMOJI} إصدار سورس عبود : {jmver}
{EMOJI} إصدار البايثون : {pyver}
{EMOJI} الوقت : {uptime}
{EMOJI} البنك : {ping}
{EMOJI} المستخدم : {mention}"""
    jmthon_caption = gvarstatus("ALIVE_TEMPLATE") or temp
    caption = jmthon_caption.format(
        ALIVE_TEXT=ALIVE_TEXT,
        EMOJI=EMOJI,
        mention=mention(me),
        uptime=uptime,
        telever=version.__version__,
        jmver=JMVERSION,
        pyver=python_version(),
        dbhealth=check_sgnirts,
        ping=ms,
    )
    if RR7_IMG:
        RR7 = [x for x in RR7_IMG.split()]
        PIC = random.choice(RR7)
        try:
            await event.client.send_file(
                event.chat_id, PIC, caption=caption, reply_to=reply_to_id
            )
            await event.delete()
        except:
            return await edit_or_reply(
                event,
                "الميديا خطأ غير الرابط باستخدام الأمر .اضف_فار ALIVE_PIC رابط صورتك"
            )
    else:
        await edit_or_reply(event, caption)

# =====================================================================
#                        أَمْرُ الْأَوَامِرِ - النسخة المعدلة
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.الاوامر$'))
async def show_commands(event):
    """قائمة أوامر احترافية تعرض الأوامر الموجودة فعلياً في السورس فقط."""
    if not await is_owner(event):
        return

    buttons = [
        [Button.inline("🛡️ الإدارة والمجموعات", b"real_1")],
        [Button.inline("👤 الحساب والملف الشخصي", b"real_2")],
        [Button.inline("⚙️ الإعدادات والمتغيرات", b"real_3")],
        [Button.inline("⏱️ الوقت والأتمتة", b"real_4")],
        [Button.inline("📦 التخزين والقنوات", b"real_5")],
        [Button.inline("🔎 البحث والتحميل", b"real_6")],
        [Button.inline("🔐 حماية الخاص", b"real_7")],
        [Button.inline("👑 المطور والتشغيل", b"real_8")],
    ]

    msg = """
╭━━━『 𝑨𝑩𝑫𝑼𝑳𝑨𝑳𝑨𝑴 𝑼𝑳𝑻𝑹𝑨 』━━━╮
┃ ✦ سورس احترافي — أوامر فعلية
┃ ✦ جميع الأوامر تبدأ بالنقطة .
┃ ✦ اختر القسم من الأسفل
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""
    await event.reply(msg, buttons=buttons)


@client.on(events.CallbackQuery(pattern=b"real_(\\d+)"))
async def real_commands_handler(event):
    if not await is_owner(event):
        return

    num = event.data_match.group(1).decode("utf-8")
    pages = {
        "1": """🛡️ الإدارة والمجموعات

.رفع مشرف
.رفع مالك
.اخفاء
.تنزيل مشرف
.حظر
.الغاء حظر
.كتم
.الغاء كتم
.طرد
.تفليش
.تصفير
.الاعضاء
.المشرفين
.المعلومات
.المحذوفين
.المحذوفين تنظيف
.مسح المحظورين
.غادر
.تاك
.الاحداث
.البوتات
.البوتات طرد""",

        "2": """👤 الحساب والملف الشخصي

.ايدي
.ايديي
.اسمي
.كشف
.id
.رابط الحساب
.المطور
.تغيير اسمي <الاسم>
.تغيير بايو <النص>
.تغيير صورتي  ← بالرد على صورة
.حذف صورتي
.جلسة
.تنظيف""",

        "3": """⚙️ الإعدادات والمتغيرات

.اضف_فار <KEY> <VALUE>
.حذف_فار <KEY>
.فار <KEY>
.كل_الفارات
.اضف متحكم
.حذف متحكم
.المتحكمين
.قفل <النوع>
.فتح <النوع>
.الحاله

أنواع القفل:
البوتات • المعرفات • الدخول • الاضافه
التوجيه • الميديا • الانلاين • الفشار
الروابط • الفارسيه • الكل""",

        "4": """⏱️ الوقت والأتمتة

.تفعيل الوقت
.تعطيل الوقت
.صوره وقتيه
.اسم وقتي
.بايو وقتي
.ايقاف صوره وقتيه
.ايقاف اسم وقتي
.ايقاف بايو وقتي
.الذاتيه
.تفعيل الذاتيه
.تعطيل الذاتيه
.ذاتيه <النص>""",

        "5": """📦 التخزين والقنوات

.نسخ احتياطي
.انشاء مجموعة تخزين
.انشاء مجموعة <الاسم>
.انشاء قناة <الاسم>
.المجموعات
.القنوات
.تشغيل الارشفة
.ايقاف الارشفة
.مسح الارشفة
.قائمة المسموحين""",

        "6": """🔎 البحث والتحميل

.بحث <كلمة>
.فيديو <كلمة>
.اغنية <كلمة>
.تحميل صوتي <رابط>
.تحميل فيد <رابط>
.صوتي
.الكاشف
.كاشف <النص>
.اعلان <رقم> <النص>
.إعلان <رقم> <النص>""",

        "7": """🔐 حماية الرسائل الخاصة

.س
.سماح
.ر
.رفض
.بلوك
.الغاء البلوك
.الغاء البلوك للكل
.تشغيل الارشفة
.ايقاف الارشفة
.مسح الارشفة
.قائمة المسموحين""",

        "8": """👑 المطور والتشغيل

.الاوامر
.تنصيب
.تنصيب جلسة
.اعادة تشغيل
.تحديث
.اخر تحديث

ملاحظة:
الأوامر التي كانت تظهر كـ «قيد التطوير» أو لم يكن لها Handler
تم حذفها من القائمة حتى لا يظهر للسورس أمر وهمي.""",
    }

    await event.edit(
        "╭━━━『 𝑨𝑩𝑫𝑼𝑳𝑨𝑳𝑨𝑴 𝑼𝑳𝑻𝑹𝑨 』━━━╮\n"
        + pages.get(num, "❌ القسم غير موجود")
        + "\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    await event.answer("✅ هذه أوامر موجودة فعلياً في السورس", alert=True)


# =====================================================================
#                        أَوَامِرُ التَّنْصِيبِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.تنصيب جلسة$'))
async def install_session_command(event):
    if not await is_owner(event):
        return
    await event.reply("""
📥 أمر التنصيب بالجلسة

📌 أرسل جلسة تيليجرام المستخرجة في رسالة جديدة
⚠️ تأكد من نسخها كاملة

✧ سورس عبود ✧
""")
    global waiting_for_session, session_user_id
    waiting_for_session = True
    session_user_id = event.sender_id

@client.on(events.NewMessage())
async def handle_session_input(event):
    global waiting_for_session, session_user_id
    if not waiting_for_session or event.sender_id != session_user_id:
        return
    if event.text.startswith('.'):
        return
    session_str = event.text.strip()
    if len(session_str) < 20:
        await event.reply("❌ الجلسة غير صالحة! تأكد من نسخها كاملة")
        waiting_for_session = False
        return
    try:
        temp_client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await temp_client.connect()
        me = await temp_client.get_me()
        await temp_client.disconnect()
    except Exception as e:
        await event.reply(f"❌ الجلسة غير صالحة: {str(e)}")
        waiting_for_session = False
        return
    CONFIG["session_string"] = session_str
    save_config()
    os.environ["SESSION_STRING"] = session_str
    await event.reply(f"""
✅ تم التنصيب بنجاح!

👤 الحساب: {me.first_name}
🆔 الايدي: {me.id}
🔄 جاري إعادة التشغيل...

✧ سورس عبود ✧
""")
    waiting_for_session = False
    try:
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
    except:
        await event.reply("⚠️ أعد تشغيل البوت يدوياً")

@client.on(events.NewMessage(pattern=r'^\.تنصيب$'))
async def install_bot(event):
    if not await is_owner(event):
        return
    global install_waiting, install_user_id, install_step, install_client, install_phone, install_hash
    if install_client:
        try:
            await install_client.disconnect()
        except:
            pass
    install_waiting = True
    install_user_id = event.sender_id
    install_step = "phone"
    install_client = None
    install_phone = None
    install_hash = None
    await event.reply("""
📥 أمر التنصيب التلقائي

📌 الخطوات:
1️⃣ أرسل رقم هاتفك مع مفتاح الدولة (مثال: +9665XXXXXXXX)
2️⃣ انتظر رمز التحقق من تيليجرام
3️⃣ أرسل الرمز المكون من 5 أرقام هنا
4️⃣ إذا كان الحساب مفعل بخطوتين، أرسل كلمة المرور

💡 بديل: استخدم .تنصيب جلسة إذا كنت تملك جلسة مستخرجة

✧ سورس عبود ✧
""")

@client.on(events.NewMessage())
async def handle_install_input(event):
    global install_waiting, install_user_id, install_phone, install_client, install_step, install_hash, install_password
    if not install_waiting or event.sender_id != install_user_id or event.text.startswith('.'):
        return
    try:
        if install_step == "phone":
            phone = event.text.strip()
            install_phone = phone
            if install_client:
                try:
                    await install_client.disconnect()
                except:
                    pass
            install_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await install_client.connect()
            try:
                result = await install_client.send_code_request(phone)
                install_hash = result.phone_code_hash
                await event.reply(f"""
📱 تم استقبال الرقم: {phone}

⏳ جاري إرسال رمز التحقق...
📩 أرسل الرمز الذي وصل إلى تيليجرام

✧ سورس عبود ✧
""")
                install_step = "code"
            except PhoneNumberInvalidError:
                await event.reply("❌ رقم الهاتف غير صحيح! تأكد من كتابته مع مفتاح الدولة")
                install_waiting = False
                install_step = "phone"
                if install_client:
                    await install_client.disconnect()
                    install_client = None
            except FloodWaitError as e:
                await event.reply(f"⏳ انتظر {e.seconds} ثانية قبل المحاولة مرة أخرى")
                install_waiting = False
                install_step = "phone"
                if install_client:
                    await install_client.disconnect()
                    install_client = None
            except Exception as e:
                await event.reply(f"❌ خطأ في إرسال الرمز: {str(e)}")
                install_waiting = False
                install_step = "phone"
                if install_client:
                    await install_client.disconnect()
                    install_client = None
        elif install_step == "code":
            code = event.text.strip()
            try:
                await install_client.sign_in(phone=install_phone, code=code, phone_code_hash=install_hash)
                me_new = await install_client.get_me()
                new_session = install_client.session.save()
                CONFIG["session_string"] = new_session
                save_config()
                os.environ["SESSION_STRING"] = new_session
                await event.reply(f"""
✅ تم التنصيب بنجاح!

📋 المعرف: {me_new.id}
📛 الاسم: {me_new.first_name}
🆔 اليوزر: @{me_new.username if me_new.username else 'لا يوجد'}

🔄 جاري إعادة التشغيل...

✧ سورس عبود ✧
""")
                await install_client.disconnect()
                install_client = None
                install_waiting = False
                subprocess.Popen([sys.executable, __file__])
                sys.exit(0)
            except SessionPasswordNeededError:
                await event.reply("""
🔐 مطلوب كلمة مرور الخطوتين!

📌 أرسل الآن كلمة المرور الخاصة بحسابك

✧ سورس عبود ✧
""")
                install_step = "password"
            except PhoneCodeInvalidError:
                await event.reply("❌ رمز التحقق غير صحيح! أعد المحاولة")
            except FloodWaitError as e:
                await event.reply(f"⏳ انتظر {e.seconds} ثانية قبل المحاولة مرة أخرى")
            except Exception as e:
                await event.reply(f"❌ خطأ: {str(e)}\n\n📌 أعد المحاولة بـ .تنصيب")
                install_waiting = False
                install_step = "phone"
                if install_client:
                    await install_client.disconnect()
                    install_client = None
        elif install_step == "password":
            password = event.text.strip()
            try:
                await install_client.sign_in(password=password)
                me_new = await install_client.get_me()
                new_session = install_client.session.save()
                CONFIG["session_string"] = new_session
                save_config()
                os.environ["SESSION_STRING"] = new_session
                await event.reply(f"""
✅ تم التنصيب بنجاح!

📋 المعرف: {me_new.id}
📛 الاسم: {me_new.first_name}
🆔 اليوزر: @{me_new.username if me_new.username else 'لا يوجد'}

🔄 جاري إعادة التشغيل...

✧ سورس عبود ✧
""")
                await install_client.disconnect()
                install_client = None
                install_waiting = False
                subprocess.Popen([sys.executable, __file__])
                sys.exit(0)
            except Exception as e:
                await event.reply(f"❌ كلمة المرور غير صحيحة!\nالخطأ: {str(e)}")
                install_step = "password"
    except Exception as e:
        await event.reply(f"❌ خطأ عام: {str(e)}\n\n📌 أعد المحاولة بـ .تنصيب")
        install_waiting = False
        install_step = "phone"
        if install_client:
            await install_client.disconnect()
            install_client = None

# =====================================================================
#                        أَمْرُ إِعَادَةِ التَّشْغِيلِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.اعادة تشغيل$'))
async def restart_bot(event):
    if not await is_owner(event):
        return
    await event.reply("🔄 جاري إعادة تشغيل البوت...")
    try:
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
    except Exception as e:
        await event.reply(f"❌ خطأ في إعادة التشغيل: {str(e)}")

# =====================================================================
#                        أَمْرُ التَّحْدِيثِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.تحديث$'))
async def update_source(event):
    if not await is_owner(event):
        return
    zedevent = await edit_or_reply(event, "🔄 جاري التحقق من التحديثات...")
    try:
        import subprocess
        import requests
        
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            return await zedevent.edit("❌ Git غير مثبت على السيرفر!")
        
        repo_url = "https://api.github.com/repos/SSSTlF/SORCER/commits/main"
        try:
            response = requests.get(repo_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_commit = data.get("sha", "")[:7]
                latest_message = data.get("commit", {}).get("message", "تحديث جديد")
                latest_author = data.get("commit", {}).get("author", {}).get("name", "المطور")
            else:
                latest_commit = "غير معروف"
                latest_message = "تعذر جلب التحديثات"
                latest_author = "غير معروف"
        except:
            latest_commit = "غير معروف"
            latest_message = "تعذر جلب التحديثات"
            latest_author = "غير معروف"
        
        current_commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        
        if current_commit == latest_commit:
            await zedevent.edit(f"""
✅ السورس محدث بالفعل!

📌 الإصدار الحالي: {current_commit}
👤 آخر تحديث: {latest_author}
📝 الرسالة: {latest_message}

✧ سورس عبود ✧
""")
            return
        
        await zedevent.edit(f"""
🔄 جاري تحديث السورس...

📌 الإصدار الحالي: {current_commit}
📌 الإصدار الجديد: {latest_commit}
👤 المطور: {latest_author}
📝 التحديث: {latest_message}

⏳ جاري سحب التحديثات...
""")
        
        pull_result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        
        if pull_result.returncode != 0:
            return await zedevent.edit(f"""
❌ فشل التحديث!

📌 الخطأ:
{pull_result.stderr}

💡 الحل: تأكد من الاتصال بالإنترنت وصلاحية الوصول إلى GitHub
""")
        
        await zedevent.edit(f"""
✅ تم تحديث السورس بنجاح!

📌 الإصدار الجديد: {latest_commit}
📝 التحديث: {latest_message}
👤 المطور: {latest_author}

🔄 جاري إعادة تشغيل البوت...
✧ سورس عبود ✧
""")
        
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
        
    except Exception as e:
        await zedevent.edit(f"❌ خطأ في التحديث:\n{str(e)}")

@client.on(events.NewMessage(pattern=r'^\.اخر تحديث$'))
async def last_update(event):
    if not await is_owner(event):
        return
    try:
        import subprocess
        import requests
        
        repo_url = "https://api.github.com/repos/SSSTlF/SORCER/commits/main"
        try:
            response = requests.get(repo_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_commit = data.get("sha", "")[:7]
                latest_message = data.get("commit", {}).get("message", "تحديث جديد")
                latest_author = data.get("commit", {}).get("author", {}).get("name", "المطور")
            else:
                latest_commit = "غير معروف"
                latest_message = "تعذر جلب التحديثات"
                latest_author = "غير معروف"
        except:
            latest_commit = "غير معروف"
            latest_message = "تعذر جلب التحديثات"
            latest_author = "غير معروف"
        
        current_commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        log_result = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True).stdout.strip()
        
        await event.reply(f"""
📋 معلومات التحديثات

📌 الإصدار الحالي: {current_commit}
📌 آخر إصدار: {latest_commit}

👤 المطور: {latest_author}
📝 آخر تحديث: {latest_message}

📖 آخر 5 تغييرات:
{log_result}

✅ الحالة: {('محدث' if current_commit == latest_commit else 'يوجد تحديث جديد')}

✧ سورس عبود ✧
""")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# =====================================================================
#                        أَوَامِرُ الْمُتَغَيِّرَاتِ الْعَامَّةِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.اضف_فار (\w+) ([\s\S]+)$'))
async def add_gvar(event):
    if not await is_owner(event):
        return
    key = event.pattern_match.group(1)
    value = event.pattern_match.group(2).strip()
    addgvar(key, value)
    await event.reply(f"✅ تم إضافة المتغير {key} = {value}")

@client.on(events.NewMessage(pattern=r'^\.حذف_فار (\w+)$'))
async def del_gvar(event):
    if not await is_owner(event):
        return
    key = event.pattern_match.group(1)
    if gvarstatus(key) is not None:
        delgvar(key)
        await event.reply(f"✅ تم حذف المتغير {key}")
    else:
        await event.reply(f"❌ المتغير {key} غير موجود")

@client.on(events.NewMessage(pattern=r'^\.فار (\w+)$'))
async def get_gvar(event):
    if not await is_owner(event):
        return
    key = event.pattern_match.group(1)
    value = gvarstatus(key)
    if value is not None:
        await event.reply(f"📋 {key} = {value}")
    else:
        await event.reply(f"❌ المتغير {key} غير موجود")

@client.on(events.NewMessage(pattern=r'^\.كل_الفارات$'))
async def all_gvars(event):
    if not await is_owner(event):
        return
    data = load_globals()
    if not data:
        await event.reply("❌ لا توجد متغيرات عامة")
        return
    text = "📋 قائمة المتغيرات العامة:\n\n"
    for key, value in data.items():
        text += f"• {key} = {value}\n"
    await event.reply(text)

# =====================================================================
#                        أَوَامِرُ الْحَظْرِ الْعَامِّ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.غبان (\d+)(?: (.+))?$'))
async def gban_user_cmd(event):
    if not await is_owner(event):
        return
    user_id = int(event.pattern_match.group(1))
    reason = event.pattern_match.group(2) if event.pattern_match.group(2) else "لا يوجد سبب"
    if is_gbanned(user_id):
        await event.reply(f"⚠️ المستخدم {user_id} محظور عاماً بالفعل")
        return
    gban_user(user_id, reason)
    await event.reply(f"✅ تم حظر المستخدم {user_id} عاماً\n📝 السبب: {reason}")

@client.on(events.NewMessage(pattern=r'^\.الغاء غبان (\d+)$'))
async def ungban_user_cmd(event):
    if not await is_owner(event):
        return
    user_id = int(event.pattern_match.group(1))
    if not is_gbanned(user_id):
        await event.reply(f"⚠️ المستخدم {user_id} غير محظور عاماً")
        return
    ungban_user(user_id)
    await event.reply(f"✅ تم إلغاء الحظر العام للمستخدم {user_id}")

# =====================================================================
#                        أَوَامِرُ الْجَلْسَةِ وَالتَّنْظِيفِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.جلسة$'))
async def get_session(event):
    if not await is_owner(event):
        return
    if SESSION:
        session_preview = SESSION[:30] + "..." if len(SESSION) > 30 else SESSION
        await event.reply(f"📋 جلسة الحساب الحالية:\n\n{session_preview}\n\n⚠️ لا تشاركها مع أي شخص!")
    else:
        await event.reply("❌ لا توجد جلسة حالية")

@client.on(events.NewMessage(pattern=r'^\.تنظيف$'))
async def clean_files(event):
    if not await is_owner(event):
        return
    await event.reply("🔄 جاري تنظيف الملفات المؤقتة...")
    count = 0
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith((".mp4", ".m4a", ".mp3", ".jpg", ".png", ".webm", ".jpeg", ".gif")):
                try:
                    os.remove(os.path.join(root, file))
                    count += 1
                except:
                    pass
    await event.reply(f"✅ تم حذف {count} ملف مؤقت")

# =====================================================================
#                        أَمْرُ النَّسْخِ الاحْتِيَاطِيِّ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.نسخ احتياطي$'))
async def backup(event):
    if not await is_owner(event):
        return
    await event.reply("🔄 جاري إنشاء نسخ احتياطي...")
    try:
        files = [CONFIG_FILE, GLOBALS_FILE, LOCKS_FILE, MUTE_FILE, GBAN_FILE, NO_LOG_FILE, SUDOS_FILE, PMPERMIT_FILE]
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        for file in files:
            if os.path.exists(file):
                shutil.copy(file, os.path.join(backup_dir, file))
        if SESSION:
            with open(os.path.join(backup_dir, "session.txt"), "w") as f:
                f.write(SESSION)
        await event.reply(f"✅ تم إنشاء النسخ الاحتياطي في: {backup_dir}")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# =====================================================================
#                        أَوَامِرُ الْمُتَحَكِّمِينَ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.اضف متحكم( (.*)|$)'))
async def add_sudo_cmd(event):
    if not await is_owner(event):
        return
    inputs = event.pattern_match.group(1).strip()
    if event.reply_to_msg_id:
        replied_to = await event.get_reply_message()
        user_id = replied_to.sender_id
        try:
            user = await event.client.get_entity(user_id)
        except:
            user = None
    elif inputs:
        try:
            user = await event.client.get_entity(inputs)
            user_id = user.id
        except:
            return await event.reply("❌ المستخدم غير موجود!")
    elif event.is_private:
        user = await event.get_chat()
        user_id = user.id
    else:
        return await event.reply("**⎆ يجب عليك الرد على المستخدم أو وضع يوزره لإضافته في المتحكمين**")
    
    if user and isinstance(user, User) and (user.bot or user.verified):
        return await event.reply("**◙ لا يمكن إضافـة البوتات إلى قائمة المتحكميـن**")
    
    name = inline_mention(user) if user else f"`{user_id}`"
    if user_id == (await event.client.get_me()).id:
        return await event.reply("**⎆ لا يمكنك إضافـة نفسك إلى قائمة المتحكمين**")
    if is_sudo(user_id):
        return await event.reply(f"**⎆ المستخدم: {name}\n◙ في قائمة المتحكمين أصلا**...")
    
    add_sudo(user_id)
    await event.reply(f"**◙ المستخدم: {name}\n◙ تم بنجاح أضافته إلى قائمة المتحكمين**")

@client.on(events.NewMessage(pattern=r'^\.حذف متحكم( (.*)|$)'))
async def remove_sudo_cmd(event):
    if not await is_owner(event):
        return
    inputs = event.pattern_match.group(1).strip()
    if event.reply_to_msg_id:
        replied_to = await event.get_reply_message()
        user_id = replied_to.sender_id
        try:
            user = await event.client.get_entity(user_id)
        except:
            user = None
    elif inputs:
        try:
            user = await event.client.get_entity(inputs)
            user_id = user.id
        except:
            return await event.reply("❌ المستخدم غير موجود!")
    elif event.is_private:
        user = await event.get_chat()
        user_id = user.id
    else:
        return await event.reply("**يجب عليك الرد على المستخدم أو وضعه يوزره مع الأمر**")
    
    name = inline_mention(user) if user else f"`{user_id}`"
    if not is_sudo(user_id):
        return await event.reply(f"**⎆ المستخدم: {name}\n◙ ليس من ضمن المتحكمين أصـلًا..**...")
    
    remove_sudo(user_id)
    await event.reply(f"**◙ المستخدم: {name}\n◙ تم حذفه من قائمة المتحـكمين**")

@client.on(events.NewMessage(pattern=r'^\.المتحكمين$'))
async def list_sudo_cmd(event):
    if not await is_owner(event):
        return
    sudos = get_sudos()
    if not sudos:
        return await event.reply("**⎆ لا يوجد أي مستخدم مضاف إلى المتحكمين**")
    msg = ""
    for i in sudos:
        try:
            user = await event.client.get_entity(i)
        except:
            user = None
        if user:
            msg += f"◙ {inline_mention(user)} ( `{i}` )\n"
        else:
            msg += f"◙ `{i}` :  مستخدم غير صالح\n"
    await event.reply(f"**◙ قائمة المتحكمين :**\n{msg}", link_preview=False)

# =====================================================================
#                        أَوَامِرُ الْقَنَوَاتِ وَالْمَجْمُوعَاتِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.انشاء مجموعة تخزين$'))
async def create_storage_group(event):
    if not await is_owner(event):
        return
    await event.reply("🔄 جاري إنشاء مجموعة تخزين...")
    try:
        result = await client(CreateChannelRequest(
            title="مجموعة التخزين",
            about="مجموعة مخصصة لتخزين الملفات والوسائط",
            megagroup=True
        ))
        group_id = result.chats[0].id
        me = await client.get_me()
        try:
            await client(EditAdminRequest(
                group_id,
                me.id,
                ChatAdminRights(
                    add_admins=True,
                    invite_users=True,
                    change_info=True,
                    ban_users=True,
                    delete_messages=True,
                    pin_messages=True,
                    manage_call=True
                ),
                "المالك"
            ))
        except:
            pass
        await event.reply(f"""
✅ تم إنشاء مجموعة التخزين بنجاح!

📛 الاسم: مجموعة التخزين
🆔 الايدي: {group_id}

✧ سورس عبود ✧
""")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.انشاء مجموعة (.+)$'))
async def create_group(event):
    if not await is_owner(event):
        return
    name = event.pattern_match.group(1)
    await event.reply(f"🔄 جاري إنشاء مجموعة: {name}...")
    try:
        result = await client(CreateChannelRequest(
            title=name,
            about="تم إنشاؤها بواسطة سورس عبود",
            megagroup=True
        ))
        group_id = result.chats[0].id
        await event.reply(f"""
✅ تم إنشاء المجموعة بنجاح!

📛 الاسم: {name}
🆔 الايدي: {group_id}

✧ سورس عبود ✧
""")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.انشاء قناة (.+)$'))
async def create_channel(event):
    if not await is_owner(event):
        return
    name = event.pattern_match.group(1)
    await event.reply(f"🔄 جاري إنشاء قناة: {name}...")
    try:
        result = await client(CreateChannelRequest(
            title=name,
            about="تم إنشاؤها بواسطة سورس عبود",
            broadcast=True
        ))
        channel_id = result.chats[0].id
        await event.reply(f"""
✅ تم إنشاء القناة بنجاح!

📛 الاسم: {name}
🆔 الايدي: {channel_id}

✧ سورس عبود ✧
""")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.المجموعات$'))
async def list_groups(event):
    if not await is_owner(event):
        return
    await event.reply("🔄 جاري جلب قائمة المجموعات...")
    try:
        groups = []
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(f"• {dialog.name} ({dialog.id})")
        if groups:
            text = "📋 قائمة المجموعات:\n\n" + "\n".join(groups[:20])
            if len(groups) > 20:
                text += f"\n\n... و {len(groups) - 20} مجموعة أخرى"
            await event.reply(text)
        else:
            await event.reply("❌ لا توجد مجموعات")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.القنوات$'))
async def list_channels(event):
    if not await is_owner(event):
        return
    await event.reply("🔄 جاري جلب قائمة القنوات...")
    try:
        channels = []
        async for dialog in client.iter_dialogs():
            if dialog.is_channel:
                channels.append(f"• {dialog.name} ({dialog.id})")
        if channels:
            text = "📋 قائمة القنوات:\n\n" + "\n".join(channels[:20])
            if len(channels) > 20:
                text += f"\n\n... و {len(channels) - 20} قناة أخرى"
            await event.reply(text)
        else:
            await event.reply("❌ لا توجد قنوات")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# =====================================================================
#                        أَوَامِرُ الْبْرُوفَايْلِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.تغيير اسمي (.+)$'))
async def change_name(event):
    if not await is_owner(event):
        return
    new_name = event.pattern_match.group(1)
    try:
        await client(UpdateProfileRequest(first_name=new_name))
        await event.reply(f"✅ تم تغيير الاسم إلى: {new_name}")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.تغيير بايو (.+)$'))
async def change_bio(event):
    if not await is_owner(event):
        return
    new_bio = event.pattern_match.group(1)
    try:
        await client(UpdateProfileRequest(about=new_bio))
        await event.reply(f"✅ تم تغيير البايو إلى: {new_bio}")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.تغيير صورتي$'))
async def change_profile_pic(event):
    if not await is_owner(event):
        return
    if not event.is_reply:
        return await event.reply("❌ بالرد على صورة لتغيير بروفايلك")
    reply = await event.get_reply_message()
    if not reply.photo:
        return await event.reply("❌ هذا ليس صورة")
    try:
        pic = await reply.download_media()
        if pic:
            file = await client.upload_file(pic)
            await client(UploadProfilePhotoRequest(file))
            os.remove(pic)
            await event.reply("✅ تم تغيير صورة البروفايل بنجاح")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.حذف صورتي$'))
async def delete_profile_pics(event):
    if not await is_owner(event):
        return
    try:
        photos = await client.get_profile_photos("me")
        if not photos:
            return await event.reply("❌ لا توجد صور بروفايل")
        await client(DeletePhotosRequest(photos))
        await event.reply(f"✅ تم حذف {len(photos)} صورة بروفايل")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# =====================================================================
#                        أَوَامِرُ الْوَقْتِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.تفعيل الوقت$'))
async def enable_time(event):
    global time_enabled
    if not await is_owner(event):
        return
    try:
        time_enabled = True
        CONFIG["time_enabled"] = True
        save_config()
        now = get_saudi_time()
        time_str = now.strftime("%I:%M %p")
        me = await client.get_me()
        first_name = me.first_name or ""
        last_name = me.last_name or ""
        name_parts = first_name.split(' ⌚')
        clean_name = name_parts[0]
        new_name = f"{clean_name} ⌚ {time_str}"
        await update_name(new_name, last_name)
        await event.reply(f"✅ تم تفعيل عرض الوقت\n🕐 الوقت الحالي: {time_str}")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.تعطيل الوقت$'))
async def disable_time(event):
    global time_enabled
    if not await is_owner(event):
        return
    try:
        time_enabled = False
        CONFIG["time_enabled"] = False
        save_config()
        me = await client.get_me()
        first_name = me.first_name or ""
        last_name = me.last_name or ""
        name_parts = first_name.split(' ⌚')
        clean_name = name_parts[0]
        await update_name(clean_name, last_name)
        await event.reply("✅ تم تعطيل عرض الوقت")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# =====================================================================
#                        أَوَامِرُ الْوَقْتِيَّةِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.صوره وقتيه$'))
async def start_digitalpic(event):
    global digitalpic_running
    if not await is_owner(event):
        return
    if digitalpic_running:
        await event.reply("❌ الصورة الوقتية مفعلة بالفعل")
        return
    digitalpic_running = True
    await event.reply("✅ تم تفعيل الصورة الوقتية")
    asyncio.create_task(digitalpic_loop())

async def digitalpic_loop():
    global digitalpic_running
    if Image is None:
        print("Pillow غير مثبت - تعطيل الصورة الوقتية")
        digitalpic_running = False
        return
    i = 0
    while digitalpic_running:
        digitalpic_path = gvarstatus("DIGITAL_PIC_PATH") or "digital_pic.png"
        if not os.path.exists(digitalpic_path):
            await asyncio.sleep(CHANGE_TIME)
            continue
        autophoto_path = "photo_pfp.png"
        shutil.copy(digitalpic_path, autophoto_path)
        current_time = datetime.now().strftime("%I:%M")
        try:
            img = Image.open(autophoto_path)
            drawn_text = ImageDraw.Draw(img)
            fnt = ImageFont.truetype("DejaVuSansMono.ttf", 35)
            drawn_text.text((140, 70), current_time, font=fnt, fill=(255, 255, 255))
            img.save(autophoto_path)
            file = await client.upload_file(autophoto_path)
            if i > 0:
                await client(DeletePhotosRequest(await client.get_profile_photos("me", limit=1)))
            i += 1
            await client(UploadProfilePhotoRequest(file))
            os.remove(autophoto_path)
        except Exception as e:
            print(f"خطأ في الصورة الوقتية: {e}")
        await asyncio.sleep(CHANGE_TIME)

@client.on(events.NewMessage(pattern=r'^\.اسم وقتي$'))
async def start_autoname(event):
    global autoname_running
    if not await is_owner(event):
        return
    if autoname_running:
        await event.reply("❌ الاسم الوقتي مفعل بالفعل")
        return
    autoname_running = True
    await event.reply("✅ تم تفعيل الاسم الوقتي")
    asyncio.create_task(autoname_loop())

async def autoname_loop():
    global autoname_running
    while autoname_running:
        HM = time.strftime("%I:%M")
        name = f"⏰ {HM}"
        try:
            await client(UpdateProfileRequest(last_name=name))
        except FloodWaitError as ex:
            await asyncio.sleep(ex.seconds)
        except Exception as e:
            print(f"خطأ في الاسم الوقتي: {e}")
        await asyncio.sleep(CHANGE_TIME)

@client.on(events.NewMessage(pattern=r'^\.بايو وقتي$'))
async def start_autobio(event):
    global autobio_running
    if not await is_owner(event):
        return
    if autobio_running:
        await event.reply("❌ البايو الوقتي مفعل بالفعل")
        return
    autobio_running = True
    await event.reply("✅ تم تفعيل البايو الوقتي")
    asyncio.create_task(autobio_loop())

async def autobio_loop():
    global autobio_running
    while autobio_running:
        HM = time.strftime("%I:%M")
        bio = f"الحمد لله ⏐ {HM}"
        try:
            await client(UpdateProfileRequest(about=bio))
        except FloodWaitError as ex:
            await asyncio.sleep(ex.seconds)
        except Exception as e:
            print(f"خطأ في البايو الوقتي: {e}")
        await asyncio.sleep(CHANGE_TIME)

@client.on(events.NewMessage(pattern=r'^\.ايقاف (.*)$'))
async def stop_auto(event):
    global digitalpic_running, autoname_running, autobio_running
    if not await is_owner(event):
        return
    option = event.pattern_match.group(1)
    if option == "صوره وقتيه" or option == "البروفايل":
        digitalpic_running = False
        await event.reply("✅ تم إيقاف الصورة الوقتية")
    elif option == "اسم وقتي" or option == "الاسم":
        autoname_running = False
        await event.reply("✅ تم إيقاف الاسم الوقتي")
    elif option == "بايو وقتي" or option == "البايو":
        autobio_running = False
        await event.reply("✅ تم إيقاف البايو الوقتي")
    else:
        await event.reply("❌ خيار غير معروف\nالخيارات: صوره وقتيه, اسم وقتي, بايو وقتي")

# =====================================================================
#                        أَوَامِرُ الْحِمَايَةِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.قفل (.+)$'))
async def lock_command(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    lock_type = event.pattern_match.group(1).strip()
    chat_id = event.chat_id
    locks = {
        "البوتات": "bots",
        "المعرفات": "mentions",
        "الدخول": "join",
        "الاضافه": "add",
        "التوجيه": "forward",
        "الميديا": "media",
        "الانلاين": "inline",
        "الفشار": "badwords",
        "الروابط": "links",
        "الفارسيه": "persian"
    }
    if lock_type == "الكل":
        for key in locks.values():
            update_lock(chat_id, key, True)
        await event.reply("✅ تم قفل جميع الخيارات")
        return
    if lock_type in locks:
        update_lock(chat_id, locks[lock_type], True)
        await event.reply(f"✅ تم قفل {lock_type}")
    else:
        await event.reply(f"❌ نوع القفل {lock_type} غير معروف")

@client.on(events.NewMessage(pattern=r'^\.فتح (.+)$'))
async def unlock_command(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    lock_type = event.pattern_match.group(1).strip()
    chat_id = event.chat_id
    locks = {
        "البوتات": "bots",
        "المعرفات": "mentions",
        "الدخول": "join",
        "الاضافه": "add",
        "التوجيه": "forward",
        "الميديا": "media",
        "الانلاين": "inline",
        "الفشار": "badwords",
        "الروابط": "links",
        "الفارسيه": "persian"
    }
    if lock_type == "الكل":
        for key in locks.values():
            update_lock(chat_id, key, False)
        await event.reply("✅ تم فتح جميع الخيارات")
        return
    if lock_type in locks:
        update_lock(chat_id, locks[lock_type], False)
        await event.reply(f"✅ تم فتح {lock_type}")
    else:
        await event.reply(f"❌ نوع القفل {lock_type} غير معروف")

@client.on(events.NewMessage(pattern=r'^\.الحاله$'))
async def locks_status(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    chat_id = event.chat_id
    locks_status = {
        "البوتات": is_locked(chat_id, "bots"),
        "المعرفات": is_locked(chat_id, "mentions"),
        "الدخول": is_locked(chat_id, "join"),
        "الاضافه": is_locked(chat_id, "add"),
        "التوجيه": is_locked(chat_id, "forward"),
        "الميديا": is_locked(chat_id, "media"),
        "الانلاين": is_locked(chat_id, "inline"),
        "الفشار": is_locked(chat_id, "badwords"),
        "الروابط": is_locked(chat_id, "links"),
        "الفارسيه": is_locked(chat_id, "persian")
    }
    text = "✧ حالة الحماية في هذه الدردشة ✧\n\n"
    for name, status in locks_status.items():
        icon = "🔒" if status else "🔓"
        text += f"{icon} {name} : {'مقفل' if status else 'مفتوح'}\n"
    text += "\n✧ سورس عبود ✧"
    await event.reply(text)

@client.on(events.NewMessage(pattern=r'^\.البوتات(?: (.+))?$'))
async def bots_command(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    action = event.pattern_match.group(1) if event.pattern_match.group(1) else "كشف"
    if action == "طرد":
        await event.reply("🔄 جاري طرد البوتات...")
        count = 0
        async for user in client.iter_participants(event.chat_id):
            if user.bot:
                try:
                    await client.kick_participant(event.chat_id, user.id)
                    count += 1
                    await asyncio.sleep(0.5)
                except:
                    pass
        await event.reply(f"✅ تم طرد {count} بوت")
    else:
        await event.reply("🔄 جاري البحث عن البوتات...")
        bots = []
        async for user in client.iter_participants(event.chat_id):
            if user.bot:
                bots.append(f"• {user.first_name} ({user.id})")
        if bots:
            text = f"🤖 تم العثور على {len(bots)} بوت:\n\n" + "\n".join(bots)
            await event.reply(text)
        else:
            await event.reply("✅ لا يوجد بوتات في هذه المجموعة")

# =====================================================================
#                        أَوَامِرُ الْمَجْمُوعَةِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.تفليش$'))
async def ban_all(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    zedevent = await edit_or_reply(event, "🔄 جاري تفليش المجموعة...")
    admins = await client.get_participants(event.chat_id, filter=ChannelParticipantsAdmins)
    admins_id = [i.id for i in admins]
    total = 0
    success = 0
    async for user in client.iter_participants(event.chat_id):
        total += 1
        if user.id not in admins_id:
            try:
                await client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
                success += 1
                await asyncio.sleep(0.5)
            except:
                pass
    await zedevent.edit(f"✅ تم تفليش {success} من {total} عضو")

@client.on(events.NewMessage(pattern=r'^\.تصفير$'))
async def kick_all(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    zedevent = await edit_or_reply(event, "🔄 جاري تصفير المجموعة...")
    admins = await client.get_participants(event.chat_id, filter=ChannelParticipantsAdmins)
    admins_id = [i.id for i in admins]
    total = 0
    success = 0
    async for user in client.iter_participants(event.chat_id):
        total += 1
        if user.id not in admins_id:
            try:
                await client.kick_participant(event.chat_id, user.id)
                success += 1
                await asyncio.sleep(0.5)
            except:
                pass
    await zedevent.edit(f"✅ تم تصفير {success} من {total} عضو")

@client.on(events.NewMessage(pattern=r'^\.الاعضاء$'))
async def get_users_list(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    zedevent = await edit_or_reply(event, "🔄 جاري جلب قائمة الأعضاء...")
    mentions = "✧ قائمة الأعضاء ✧\n\n"
    count = 0
    async for user in client.iter_participants(event.chat_id):
        count += 1
        if user.deleted:
            mentions += f"• حساب محذوف ({user.id})\n"
        else:
            mentions += f"• [{user.first_name}](tg://user?id={user.id})\n"
        if count % 50 == 0:
            await zedevent.edit(f"🔄 تم جلب {count} عضو...")
    await zedevent.edit(mentions)

@client.on(events.NewMessage(pattern=r'^\.المشرفين$'))
async def get_admins_list(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    zedevent = await edit_or_reply(event, "🔄 جاري جلب قائمة المشرفين...")
    mentions = "✧ قائمة المشرفين ✧\n\n"
    async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantsAdmins):
        if isinstance(user.participant, ChannelParticipantCreator):
            mentions += f"👑 المالك: [{user.first_name}](tg://user?id={user.id})\n"
        else:
            mentions += f"🛡️ مشرف: [{user.first_name}](tg://user?id={user.id})\n"
    await zedevent.edit(mentions)

@client.on(events.NewMessage(pattern=r'^\.المعلومات$'))
async def chat_info(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    zedevent = await edit_or_reply(event, "🔄 جاري جلب معلومات المجموعة...")
    chat = await event.get_chat()
    full_chat = await client(GetFullChannelRequest(event.chat_id))
    info_text = f"""
✧ معلومات المجموعة ✧

📛 الاسم: {chat.title}
🆔 الايدي: {event.chat_id}
👥 الأعضاء: {full_chat.full_chat.participants_count}
🛡️ المشرفين: {full_chat.full_chat.admins_count if hasattr(full_chat.full_chat, 'admins_count') else 'غير معروف'}
🚫 المحظورين: {full_chat.full_chat.kicked_count if hasattr(full_chat.full_chat, 'kicked_count') else 'غير معروف'}
📝 الوصف: {full_chat.full_chat.about if full_chat.full_chat.about else 'لا يوجد'}

✧ سورس عبود ✧
"""
    await zedevent.edit(info_text)

@client.on(events.NewMessage(pattern=r'^\.مسح المحظورين$'))
async def unban_all(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    zedevent = await edit_or_reply(event, "🔄 جاري مسح المحظورين...")
    succ = 0
    total = 0
    async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantsKicked):
        total += 1
        try:
            await client(EditBannedRequest(event.chat_id, user, UNBAN_RIGHTS))
            succ += 1
            await asyncio.sleep(0.5)
        except:
            pass
    await zedevent.edit(f"✅ تم مسح {succ} من {total} محظور")

@client.on(events.NewMessage(pattern=r'^\.المحذوفين(?: (.+))?$'))
async def deleted_accounts(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    action = event.pattern_match.group(1) if event.pattern_match.group(1) else "عرض"
    zedevent = await edit_or_reply(event, "🔄 جاري البحث عن الحسابات المحذوفة...")
    deleted = []
    async for user in client.iter_participants(event.chat_id):
        if user.deleted:
            deleted.append(user.id)
    if not deleted:
        await zedevent.edit("✅ لا يوجد حسابات محذوفة في هذه المجموعة")
        return
    if action == "تنظيف":
        count = 0
        for user_id in deleted:
            try:
                await client(EditBannedRequest(event.chat_id, user_id, BANNED_RIGHTS))
                count += 1
                await asyncio.sleep(0.5)
            except:
                pass
        await zedevent.edit(f"✅ تم حظر {count} حساب محذوف")
    else:
        text = f"⚠️ تم العثور على {len(deleted)} حساب محذوف:\n\n"
        for idx, user_id in enumerate(deleted[:20], 1):
            text += f"{idx}. {user_id}\n"
        if len(deleted) > 20:
            text += f"\n... و {len(deleted) - 20} آخرين"
        text += f"\n\nلحظرهم استخدم: .المحذوفين تنظيف"
        await zedevent.edit(text)

@client.on(events.NewMessage(pattern=r'^\.غادر$'))
async def leave_group(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    await event.reply("🚶 جاري مغادرة المجموعة...")
    await client.kick_participant(event.chat_id, "me")

@client.on(events.NewMessage(pattern=r'^\.تاك(?: (.+))?$'))
async def tag_all(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        await event.reply("❌ هذا الأمر فقط للمجموعات")
        return
    msg = event.pattern_match.group(1) if event.pattern_match.group(1) else ""
    if not msg and not event.reply_to_msg_id:
        await event.reply("❌ اكتب نص مع الأمر أو رد على رسالة")
        return
    zedevent = await edit_or_reply(event, "🔄 جاري تاك جميع الأعضاء...")
    count = 0
    text = ""
    reply_to = event.reply_to_msg_id
    async for user in client.iter_participants(event.chat_id):
        if not user.deleted:
            count += 1
            text += f"[{user.first_name}](tg://user?id={user.id}) "
            if count % 5 == 0:
                if reply_to:
                    await client.send_message(event.chat_id, f"{text}\n\n{msg}", reply_to=reply_to)
                else:
                    await client.send_message(event.chat_id, f"{text}\n\n{msg}")
                text = ""
                await asyncio.sleep(2)
    await zedevent.delete()

# =====================================================================
#                        أَوَامِرُ الْأَحْدَاثِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.الاحداث( م)?(?: |$)(\d*)?$'))
async def _iundlt(event):
    if not await is_owner(event):
        return
    if not event.is_group:
        return await event.reply("❌ هذا الأمر فقط للمجموعات")
    zedevent = await edit_or_reply(event, "جاري البحث عن آخر الاحداث انتظر ...")
    lim = int(event.pattern_match.group(2)) if event.pattern_match.group(2) else 5
    lim = min(lim, 15) if lim > 0 else 1
    try:
        adminlog = await event.client.get_admin_log(event.chat_id, limit=lim, edit=False, delete=True)
    except Exception as e:
        return await zedevent.edit(f"❌ لا يمكن جلب الاحداث: {str(e)}")
    deleted_msg = f"اليك آخر {lim} رسائل محذوفة لهذا الكروب:\n\n"
    count = 0
    for msg in adminlog:
        try:
            ruser = await event.client.get_entity(msg.old.from_id)
        except:
            ruser = None
        _media_type = media_type(msg.old)
        if _media_type is None:
            deleted_msg += f"🖇 {msg.old.message[:50] if msg.old.message else 'رسالة'}\n"
        else:
            deleted_msg += f"🖇 {_media_type}\n"
        if ruser:
            deleted_msg += f"🛂 تم ارسالها بواسطة [{ruser.first_name}](tg://user?id={ruser.id})\n\n"
        else:
            deleted_msg += f"🛂 تم ارسالها بواسطة مستخدم غير معروف\n\n"
        count += 1
        if count >= lim:
            break
    await edit_or_reply(zedevent, deleted_msg)

# =====================================================================
#                        أَوَامِرُ الْمُشْرِفِينَ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.رفع مشرف(?:\s|$)([\s\S]*)'))
async def promote(event):
    if not await is_owner(event):
        return
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "أحتاج الى صلاحيات المشرف هنا!!")
        return
    new_rights = ChatAdminRights(add_admins=False, invite_users=True, change_info=False, ban_users=False, delete_messages=True, pin_messages=True)
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "جاري رفعه مشرف ...")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("ليست لدي صلاحيات كافية في هذه المجموعة")
    await zzevent.edit("تم ترقيته مشرف .. بنجاح")

@client.on(events.NewMessage(pattern=r'^\.رفع مالك(?:\s|$)([\s\S]*)'))
async def promote_full(event):
    if not await is_owner(event):
        return
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "أحتاج الى صلاحيات المشرف هنا!!")
        return
    new_rights = ChatAdminRights(add_admins=True, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True, manage_call=True)
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "جاري رفعه مشرف بكل الصلاحيات")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("ليست لدي صلاحيات كافية في هذه المجموعة")
    await zzevent.edit("تم ترقيته مشرف عام بكل الصلاحيات ...")

@client.on(events.NewMessage(pattern=r'^\.اخفاء(?:\s|$)([\s\S]*)'))
async def promote_anonymous(event):
    if not await is_owner(event):
        return
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "أحتاج الى صلاحيات المشرف هنا!!")
        return
    new_rights = ChatAdminRights(add_admins=True, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True, manage_call=True, anonymous=True)
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "جاري التعديل")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("ليست لدي صلاحيات كافية في هذه المجموعة")
    await zzevent.edit("تم التعديل بنجاح")

@client.on(events.NewMessage(pattern=r'^\.تنزيل مشرف(?:\s|$)([\s\S]*)'))
async def demote(event):
    if not await is_owner(event):
        return
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "أحتاج الى صلاحيات المشرف هنا!!")
        return
    user, _ = await get_user_from_event(event)
    if not user:
        return
    zzevent = await edit_or_reply(event, "جاري التنزيل")
    newrights = ChatAdminRights(add_admins=None, invite_users=None, change_info=None, ban_users=None, delete_messages=None, pin_messages=None)
    rank = "مشرف"
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, newrights, rank))
    except BadRequestError:
        return await zzevent.edit("ليست لدي صلاحيات كافية في هذه المجموعة")
    await zzevent.edit("تم تنزيله من الاشراف بنجاح")

@client.on(events.NewMessage(pattern=r'^\.حظر(?:\s|$)([\s\S]*)'))
async def _ban_person(event):
    if not await is_owner(event):
        return
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if user.id == event.client.uid:
        return await edit_delete(event, "عذراً ..لا استطيع حظر نفسي")
    zedevent = await edit_or_reply(event, "جاري الحظر ...")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await zedevent.edit("ليست لدي صلاحيات كافية في هذه المجموعة")
    if reason:
        await zedevent.edit(f"المستخدم : [{user.first_name}](tg://user?id={user.id}) \nتم حظره بنجاح\n\nالسبب : {reason}")
    else:
        await zedevent.edit(f"المستخدم : [{user.first_name}](tg://user?id={user.id}) \nتم حظره بنجاح")

@client.on(events.NewMessage(pattern=r'^\.الغاء حظر(?:\s|$)([\s\S]*)'))
async def nothanos(event):
    if not await is_owner(event):
        return
    user, _ = await get_user_from_event(event)
    if not user:
        return
    zedevent = await edit_or_reply(event, "جاري الغاء حظره ..")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await zedevent.edit(f"المستخدم : [{user.first_name}](tg://user?id={user.id}) \nتم الغاء حظره بنجاح")
    except UserIdInvalidError:
        await zedevent.edit("حدث خطأ في الغاء الحظر!")
    except Exception as e:
        await zedevent.edit(f"خطأ :\n{e}")

@client.on(events.NewMessage(pattern=r'^\.كتم(?:\s|$)([\s\S]*)'))
async def startmute(event):
    if not await is_owner(event):
        return
    if event.is_private:
        if is_muted(event.chat_id, event.chat_id):
            return await event.edit("هذا المستخدم مكتوم .. سابقاً")
        if event.chat_id == client.uid:
            return await edit_delete(event, "لا تستطع كتم نفسي")
        try:
            mute_user(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"خطأ \n{e}")
        else:
            await event.edit("تم كتم المستخدم .. بنجاح")
    else:
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        if not admin and not creator:
            return await edit_or_reply(event, "أنا لست مشرف هنا ؟!!")
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == client.uid:
            return await edit_or_reply(event, "عذراً .. لا استطيع كتم نفسي")
        if is_muted(event.chat_id, user.id):
            return await edit_or_reply(event, "عذراً .. هذا الشخص مكتوم سابقاً هنا")
        try:
            mute_user(event.chat_id, user.id)
        except Exception as e:
            return await edit_or_reply(event, f"خطأ : {e}")
        if reason:
            await edit_or_reply(event, f"المستخدم : [{user.first_name}](tg://user?id={user.id}) \nتم كتمه بنجاح\n\nالسبب : {reason}")
        else:
            await edit_or_reply(event, f"المستخدم : [{user.first_name}](tg://user?id={user.id}) \nتم كتمه بنجاح")

@client.on(events.NewMessage(pattern=r'^\.الغاء كتم(?:\s|$)([\s\S]*)'))
async def endmute(event):
    if not await is_owner(event):
        return
    if event.is_private:
        if not is_muted(event.chat_id, event.chat_id):
            return await event.edit("عذراً .. هذا الشخص غير مكتوم هنا")
        try:
            unmute_user(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"خطأ \n{e}")
        else:
            await event.edit("تم الغاء كتم الشخص هنا .. بنجاح")
    else:
        user, _ = await get_user_from_event(event)
        if not user:
            return
        try:
            if is_muted(event.chat_id, user.id):
                unmute_user(event.chat_id, user.id)
            else:
                result = await event.client.get_permissions(event.chat_id, user.id)
                if result.participant.banned_rights.send_messages:
                    await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        except AttributeError:
            return await edit_or_reply(event, "الشخص غير مكتوم")
        except Exception as e:
            return await edit_or_reply(event, f"خطأ : {e}")
        await edit_or_reply(event, f"المستخدم : [{user.first_name}](tg://user?id={user.id}) \nتم الغاء كتمه بنجاح")

@client.on(events.NewMessage(pattern=r'^\.طرد(?:\s|$)([\s\S]*)'))
async def kick(event):
    if not await is_owner(event):
        return
    user, reason = await get_user_from_event(event)
    if not user:
        return
    zedevent = await edit_or_reply(event, "جاري الطرد ...")
    try:
        await event.client.kick_participant(event.chat_id, user.id)
    except Exception as e:
        return await zedevent.edit(f"ليست لدي صلاحيات كافية في هذه المجموعة\n{e}")
    if reason:
        await zedevent.edit(f"تم طرد [{user.first_name}](tg://user?id={user.id}) بنجاح\n\nالسبب : {reason}")
    else:
        await zedevent.edit(f"تم طرد [{user.first_name}](tg://user?id={user.id}) بنجاح")

# =====================================================================
#                        أَوَامِرُ الصَّيْدِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.الصيد$'))
async def hunt_help(event):
    if not await is_owner(event):
        return
    await event.edit("""
أوامر الصيد الخاصة بسورس عبود:

النوع :( سداسي حرفين/ ثلاثي/ سداسي/ بوتات/ خماسي حرفين/خماسي /سباعي )

الامر: .صيد + النوع
- يقوم بصيد معرفات عشوائية حسب النوع

الامر: تثبيت معرف + معرف
- وظيفة الامر : يقوم بالتثبيت على المعرف عندما يصبح متاح يأخذه

الامر: .حالة الصيد
- لمعرفة عدد المحاولات للصيد

الامر: .حالة التثبيت
- لمعرفة عدد المحاولات للصيد

سورس عبود - @SSSTlF
""")

@client.on(events.NewMessage(pattern=r'^\.صيد (.*)$'))
async def hunterusername(event):
    if not await is_owner(event):
        return
    choice = str(event.pattern_match.group(1))
    await event.edit("تم تفعيل الصيد بنجاح الان")
    try:
        ch = await client(CreateChannelRequest(title="ABOOD HUNTER - صيد عبود", about="This channel to hunt username by - @SSSTlF"))
        channel_id = ch.chats[0].id
    except Exception as e:
        await client.send_message(event.chat_id, f"خطأ في انشاء القناة , الخطأ : {str(e)}")
        return
    isclaim.clear()
    isclaim.append("on")
    sedmod = True
    while sedmod:
        username = gen_user(choice)
        if username == "error":
            await event.edit("يرجى وضع النوع بشكل صحيح")
            break
        isav = check_user(username)
        if isav == True:
            try:
                await client(UpdateUsernameRequest(channel=channel_id, username=username))
                await event.client.send_file(event.chat_id, "https://t.me/Repthongif/2", caption=f"🐊 سورس عبود 🐊\n- - - - - - - - - - - - - - - - - - - - - - - -\n- UserName: @{username}\n- ClickS: {trys[0]}\n- Type: {choice}\n- Save: Channel\n- - - - - - - - - - - - - - - - - - - - - - - -\nسورس عبود @SSSTlF")
                sedmod = False
                break
            except Exception as eee:
                pass
        else:
            pass
        trys[0] += 1
    isclaim.clear()
    isclaim.append("off")

@client.on(events.NewMessage(pattern=r'^\.تثبيت معرف (.*)$'))
async def fix_username(event):
    if not await is_owner(event):
        return
    msg = event.text.split()
    try:
        ch = str(msg[2])
        ch = ch.replace("@", "")
        await event.edit(f"حسناً سيتم بدء التثبيت في @{ch} .")
    except:
        try:
            ch = await client(CreateChannelRequest(title="ABOOD HUNTER - تثبيت عبود", about="This channel to hunt username by - @SSSTlF"))
            channel_id = ch.chats[0].id
            await event.edit("تم بنجاح بدأ التثبيت")
        except Exception as e:
            await client.send_message(event.chat_id, f"خطأ في انشاء القناة , الخطأ : {str(e)}")
            return
    isauto.clear()
    isauto.append("on")
    username = str(msg[1]).replace("@", "")
    swapmod = True
    while swapmod:
        isav = check_user(username)
        if isav == True:
            try:
                await client(UpdateUsernameRequest(channel=channel_id, username=username))
                await event.client.send_file(event.chat_id, "https://t.me/Repthongif/2", caption=f"🐊 سورس عبود 🐊\n- - - - - - - - - - - - - - - - - - - - - - - -\n- UserName: @{username}\n- ClickS: {trys2[0]}\n- Save: Channel\n- - - - - - - - - - - - - - - - - - - - - - - -\nسورس عبود @SSSTlF")
                swapmod = False
                break
            except Exception as eee:
                await client.send_message(event.chat_id, f"خطأ مع {username} , الخطأ :{str(eee)}")
                swapmod = False
                break
        else:
            pass
        trys2[0] += 1
    isauto.clear()
    isauto.append("off")

@client.on(events.NewMessage(pattern=r'^\.ايقاف الصيد$'))
async def stop_hunt(event):
    if not await is_owner(event):
        return
    if "on" in isclaim:
        isclaim.clear()
        isclaim.append("off")
        return await event.edit("تم بنجاح ايقاف عملية الصيد")
    elif "off" in isclaim:
        return await event.edit("لم يتم تفعيل الصيد بالأصل لأيقافه")
    else:
        return await event.edit("لقد حدث خطأ ما وتوقف الامر لديك")

@client.on(events.NewMessage(pattern=r'^\.ايقاف التثبيت$'))
async def stop_fix(event):
    if not await is_owner(event):
        return
    if "on" in isauto:
        isauto.clear()
        isauto.append("off")
        return await event.edit("تم بنجاح ايقاف عملية التثبيت")
    elif "off" in isauto:
        return await event.edit("لم يتم تفعيل التثبيت بالأصل لأيقافه")
    else:
        return await event.edit("لقد حدث خطأ ما وتوقف الامر لديك")

@client.on(events.NewMessage(pattern=r'^\.حالة الصيد$'))
async def hunt_status(event):
    if not await is_owner(event):
        return
    if "on" in isclaim:
        await event.edit(f"الصيد وصل لـ({trys[0]}) من المحاولات")
    elif "off" in isclaim:
        await event.edit("الصيد بالاصل لا يعمل .")
    else:
        await event.edit("لقد حدث خطأ ما وتوقف الامر لديك")

@client.on(events.NewMessage(pattern=r'^\.حالة التثبيت$'))
async def fix_status(event):
    if not await is_owner(event):
        return
    if "on" in isauto:
        await event.edit(f"التثبيت وصل لـ({trys2[0]}) من المحاولات")
    elif "off" in isauto:
        await event.edit("التثبيت بالاصل لا يعمل .")
    else:
        await event.edit("لقد حدث خطأ ما وتوقف الامر لديك")

# =====================================================================
#                        أَوَامِرُ الذَّاتِيَّةِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.الذاتيه$'))
async def cmd(baqir):
    if not await is_owner(baqir):
        return
    await edit_or_reply(baqir, """
سورس عبود @SSSTlF - حفظ الذاتيه

.تفعيل الذاتيه
لتفعيل الحفظ التلقائي للذاتيه

.تعطيل الذاتيه
لتعطيل الحفظ التلقائي للذاتيه

.ذاتيه
بالرد على صورة ذاتيه لحفظها

سورس عبود @SSSTlF
""")

@client.on(events.NewMessage(pattern=r'^\.تفعيل الذاتيه$'))
async def start_datea(event):
    if not await is_owner(event):
        return
    global repself
    if repself:
        return await edit_or_reply(event, "حفظ الذاتية التلقائي .. مفعله مسبقاً")
    repself = True
    await edit_or_reply(event, "تم تفعيل حفظ الذاتية التلقائي .. بنجاح")

@client.on(events.NewMessage(pattern=r'^\.تعطيل الذاتيه$'))
async def stop_datea(event):
    if not await is_owner(event):
        return
    global repself
    if not repself:
        return await edit_or_reply(event, "حفظ الذاتية التلقائي .. معطله مسبقاً")
    repself = False
    await edit_or_reply(event, "تم تعطيل حفظ الذاتية التلقائي .. بنجاح")

@client.on(events.NewMessage(pattern=r'^\.ذاتيه(?: |$)(.*)'))
async def oho(event):
    if not await is_owner(event):
        return
    if not event.is_reply:
        return await event.edit("بالرد على صورة ذاتية التدمير...")
    reply = await event.get_reply_message()
    if not reply.photo and not reply.video and not reply.document:
        return await event.edit("الرجاء الرد على صورة او فيديو ذاتية التدمير")
    pic = await reply.download_media()
    if pic:
        await client.send_file("me", pic, caption="تم حفظ الصورة الذاتيه .. بنجاح")
        os.remove(pic) if os.path.exists(pic) else None
    await event.delete()

@client.on(events.NewMessage(func=lambda e: e.is_private and (e.photo or e.video) and e.media_unread))
async def sddm(event):
    global repself
    if not repself:
        return
    sender = await event.get_sender()
    if sender.id == client.uid:
        return
    try:
        pic = await event.download_media()
        if pic:
            await client.send_file("me", pic, caption=f"سورس عبود @SSSTlF - حفظ الذاتيه\n\nتم حفظ الذاتية تلقائياً .. بنجاح\nالمرسل: {sender.first_name}")
            os.remove(pic)
    except Exception as e:
        print(f"خطأ في حفظ الذاتية: {e}")

# =====================================================================
#                        أَوَامِرُ الإِعْلَانِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.اعلان (\d+) ([\s\S]+)$'))
async def selfdestruct(destroy):
    if not await is_owner(destroy):
        return
    ttl = int(destroy.pattern_match.group(1))
    message = destroy.pattern_match.group(2)
    baqir = ttl * 60
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, message)
    await asyncio.sleep(baqir)
    await smsg.delete()

@client.on(events.NewMessage(pattern=r'^\.إعلان (\d+) ([\s\S]+)$'))
async def selfdestruct2(destroy):
    if not await is_owner(destroy):
        return
    ttl = int(destroy.pattern_match.group(1))
    message = destroy.pattern_match.group(2)
    baqir = ttl * 60
    text = message + f"\n\nهذا الاعلان سيتم حذفه تلقائياً بعد {ttl} دقائق"
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, text)
    await asyncio.sleep(baqir)
    await smsg.delete()

# =====================================================================
#                        أَوَامِرُ الْمَعْلُومَاتِ
# =====================================================================

async def fetch_info(replied_user, event):
    FullUser = (await event.client(GetFullUserRequest(replied_user.id))).full_user
    replied_user_profile_photos = await event.client(GetUserPhotosRequest(user_id=replied_user.id, offset=42, max_id=0, limit=80))
    replied_user_profile_photos_count = "لايوجد بروفايل"
    dc_id = "Can't get dc id"
    try:
        replied_user_profile_photos_count = replied_user_profile_photos.count
        dc_id = replied_user.photo.dc_id
    except AttributeError:
        pass
    user_id = replied_user.id
    first_name = replied_user.first_name
    full_name = FullUser.private_forward_name
    common_chat = FullUser.common_chats_count
    username = replied_user.username
    user_bio = FullUser.about
    photo = await event.client.download_profile_photo(user_id, os.path.join("downloads", str(user_id) + ".jpg"), download_big=True)
    first_name = first_name.replace("\u2060", "") if first_name else "هذا المستخدم ليس له اسم أول"
    full_name = full_name or first_name
    username = f"@{username}" if username else "لايوجد معرف"
    user_bio = "لاتوجد نبذة" if not user_bio else user_bio
    rotbat = "من مطورين السورس" if user_id == 5502537272 else "العضو"
    if user_id == (await event.client.get_me()).id and user_id != 5502537272:
        rotbat = "مالك الحساب"
    caption = "✛━━━━━━━━━━━━━✛\n"
    caption += f"<b>الاسم    ⇠ </b> {full_name}\n"
    caption += f"<b>المعرف  ⇠ </b> {username}\n"
    caption += f"<b>الايدي   ⇠ </b> <code>{user_id}</code>\n"
    caption += f"<b>الرتبة  ⇠ {rotbat} </b>\n"
    caption += f"<b>الصور   ⇠ </b> {replied_user_profile_photos_count}\n"
    caption += f"<b>الحساب ⇠ </b> "
    caption += f'<a href="tg://user?id={user_id}">{first_name}</a>'
    caption += f"\n<b>البايو    ⇠ </b> {user_bio} \n"
    caption += f"✛━━━━━━━━━━━━━✛"
    return photo, caption

@client.on(events.NewMessage(pattern=r'^\.ايدي(?: |$)(.*)'))
async def who(event):
    if not await is_owner(event):
        return
    cat = await edit_or_reply(event, "جاري جلب المعلومات...")
    if not os.path.isdir("downloads"):
        os.makedirs("downloads")
    replied_user = await get_user_from_event(event)
    if not replied_user:
        return await edit_or_reply(cat, "لم استطع العثور على الشخص")
    try:
        photo, caption = await fetch_info(replied_user, event)
    except AttributeError:
        return await edit_or_reply(cat, "لم استطع العثور على الشخص")
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    try:
        if photo:
            await event.client.send_file(event.chat_id, photo, caption=caption, link_preview=False, force_document=False, reply_to=message_id_to_reply, parse_mode="html")
            if os.path.exists(photo):
                os.remove(photo)
            await cat.delete()
        else:
            await cat.edit(caption, parse_mode="html")
    except Exception as e:
        await cat.edit(caption, parse_mode="html")

@client.on(events.NewMessage(pattern=r'^\.كشف(?:\s|$)([\s\S]*)'))
async def userinfo(event):
    if not await is_owner(event):
        return
    replied_user = await get_user_from_event(event)
    if not replied_user:
        return
    catevent = await edit_or_reply(event, "جاري إحضار معلومات المستخدم")
    replied_user = await event.client(GetFullUserRequest(replied_user.id))
    user_id = replied_user.users[0].id
    first_name = html.escape(replied_user.users[0].first_name or "مستخدم").replace("\u2060", "")
    common_chats = 1
    try:
        dc_id, location = get_input_location(replied_user.profile_photo)
    except Exception:
        dc_id = "Couldn't fetch DC ID!"
    try:
        casurl = f"https://api.cas.chat/check?user_id={user_id}"
        data = get(casurl).json()
        cas = "Antispam(CAS) محظور: True" if data and data.get("ok") else "Antispam(CAS) محظور: False"
    except:
        cas = "Antispam(CAS) محظور: تعذر الجلب"
    caption = f"""معلومات المستخدم [{first_name}](tg://user?id={user_id}):
   • الايدي: {user_id}
   • المجموعات المشتركة: {common_chats}
   • رقم قاعدة البيانات: {dc_id}
   • حساب موثق: {replied_user.users[0].restricted}
   • {cas}
"""
    await edit_or_reply(catevent, caption)

@client.on(events.NewMessage(pattern=r'^\.id(?:\s|$)(.*)'))
async def get_id_command(event):
    if not await is_owner(event):
        return
    input_str = event.pattern_match.group(1)
    if input_str:
        try:
            p = await event.client.get_entity(input_str)
            if hasattr(p, 'first_name'):
                return await edit_or_reply(event, f"ايدي المستخدم {input_str} هو {p.id}")
            elif hasattr(p, 'title'):
                return await edit_or_reply(event, f"ايدي الدردشة/القناة {p.title} هو {p.id}")
        except Exception as e:
            return await edit_delete(event, f"{str(e)}", 5)
    elif event.reply_to_msg_id:
        r_msg = await event.get_reply_message()
        if r_msg.media:
            await edit_or_reply(event, f"ايدي الدردشه: {str(event.chat_id)} \nايدي المستخدم: {str(r_msg.sender_id)}")
        else:
            await edit_or_reply(event, f"ايدي الدردشه: {str(event.chat_id)} \nايدي المستخدم: {str(r_msg.sender_id)}")
    else:
        await edit_or_reply(event, f"الدردشة الحالية: {str(event.chat_id)}")

@client.on(events.NewMessage(pattern=r'^\.ايديي$'))
async def my_id_command(event):
    if not await is_owner(event):
        return
    me = await client.get_me()
    await event.reply(f"ايديك: {me.id}")

@client.on(events.NewMessage(pattern=r'^\.اسمي$'))
async def my_name_command(event):
    if not await is_owner(event):
        return
    me = await client.get_me()
    await event.reply(f"اسمك: {me.first_name} {me.last_name or ''}")

@client.on(events.NewMessage(pattern=r'^\.رابط الحساب(?:\s|$)([\s\S]*)'))
async def permalink(event):
    if not await is_owner(event):
        return
    user = await get_user_from_event(event)
    if not user:
        return
    custom = event.pattern_match.group(1)
    if custom:
        return await edit_or_reply(event, f"[{custom}](tg://user?id={user.id})")
    tag = user.first_name.replace("\u2060", "") if user.first_name else user.username or "مستخدم"
    await edit_or_reply(event, f"[{tag}](tg://user?id={user.id})")

@client.on(events.NewMessage(pattern=r'^\.ا$'))
async def my_info(event):
    if not await is_owner(event):
        return
    try:
        me = await client.get_me()
        user_id = me.id
        first_name = me.first_name or "لا يوجد"
        last_name = me.last_name or ""
        username = f"@{me.username}" if me.username else "لا يوجد يوزر"
        now = get_saudi_time()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        text = f"""
✧ معلومات الحساب ✧

📋 المعرف : {user_id}
📛 الاسم : {first_name} {last_name}
🆔 اليوزر : {username}

📅 التاريخ : {date_str}
📍 المنطقة : السعودية - الرياض
👨‍💻 المطور : @SSSTlF

✧ سورس عبود ✧"""
        photos = await client.get_profile_photos(me)
        if photos:
            await event.reply(text, file=photos[0])
        else:
            await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.المطور$'))
async def developer_info(event):
    if not await is_owner(event):
        return
    try:
        me = await client.get_me()
        user_id = me.id
        first_name = me.first_name or "المطور"
        text = f"""
✧ مطور السورس ✧

👨‍💻 الاسم : عبود
🆔 الايدي : {user_id}
🏷️ اللقب : {first_name}

📢 القناة : @SSSTlF
💎 المنصب : مطور السورس

✧ سورس عبود ✧"""
        photos = await client.get_profile_photos(me)
        if photos:
            await event.reply(text, file=photos[0])
        else:
            await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.stat$'))
async def statistics(event):
    if not await is_owner(event):
        return
    zedevent = await edit_or_reply(event, "🔄 جاري جلب الإحصائيات...")
    start_time = time.time()
    private_chats = 0
    bots = 0
    groups = 0
    channels = 0
    admin_in_groups = 0
    creator_in_groups = 0
    admin_in_channels = 0
    creator_in_channels = 0
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if hasattr(entity, 'broadcast') and entity.broadcast:
            channels += 1
            if entity.creator or entity.admin_rights:
                admin_in_channels += 1
            if entity.creator:
                creator_in_channels += 1
        elif hasattr(entity, 'megagroup') and entity.megagroup:
            groups += 1
            if entity.creator or entity.admin_rights:
                admin_in_groups += 1
            if entity.creator:
                creator_in_groups += 1
        elif hasattr(entity, 'id') and not hasattr(entity, 'broadcast'):
            private_chats += 1
            if entity.bot:
                bots += 1
    stop_time = time.time() - start_time
    me = await client.get_me()
    text = f"""
✧ إحصائيات الحساب ✧

👤 الاسم: {me.first_name}
🆔 الايدي: {me.id}

💬 الخاص: {private_chats}
   • اشخاص: {private_chats - bots}
   • بوتات: {bots}

👥 المجموعات: {groups}
   • مالك: {creator_in_groups}
   • مشرف: {admin_in_groups - creator_in_groups}

📢 القنوات: {channels}
   • مالك: {creator_in_channels}
   • مشرف: {admin_in_channels - creator_in_channels}

⏱️ الوقت المستغرق: {stop_time:.2f} ثانية

✧ سورس عبود ✧
"""
    await zedevent.edit(text)

# =====================================================================
#                        أَوَامِرُ الْبَحْثِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.بحث (.+)'))
async def search_command(event):
    if not await is_owner(event):
        return
    try:
        query = event.pattern_match.group(1)
        if not query.strip():
            await event.reply("❌ الرجاء كتابة نص للبحث")
            return
        await event.reply(f"🔍 جاري البحث عن: {query}...")
        await asyncio.sleep(1)
        text = f"""
✧ نتيجة البحث ✧

📝 البحث : {query}
✅ النتيجة : تم العثور
🔗 الرابط : [اضغط هنا](https://www.google.com/search?q={query.replace(' ', '+')})

✧ سورس عبود ✧"""
        await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.فيديو (.+)'))
async def video_command(event):
    if not await is_owner(event):
        return
    try:
        query = event.pattern_match.group(1)
        if not query.strip():
            await event.reply("❌ الرجاء كتابة اسم الفيديو")
            return
        await event.reply(f"🎬 جاري البحث عن فيديو: {query}...")
        await asyncio.sleep(1)
        text = f"""
✧ نتيجة الفيديو ✧

🎥 اسم الفيديو : {query}
🔗 رابط المشاهدة : [اضغط هنا](https://www.youtube.com/results?search_query={query.replace(' ', '+')})

✧ سورس عبود ✧"""
        await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.اغنية (.+)'))
async def audio_command(event):
    if not await is_owner(event):
        return
    try:
        query = event.pattern_match.group(1)
        if not query.strip():
            await event.reply("❌ الرجاء كتابة اسم الأغنية")
            return
        await event.reply(f"🎵 جاري البحث عن أغنية: {query}...")
        await asyncio.sleep(1)
        text = f"""
✧ نتيجة الاغنية ✧

🎵 اسم الاغنية : {query}
🔗 رابط الاستماع : [اضغط هنا](https://www.youtube.com/results?search_query={query.replace(' ', '+')}+song)

✧ سورس عبود ✧"""
        await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# =====================================================================
#                        أَوَامِرُ التَّسْلِيَةِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.كت$'))
async def quote_command(event):
    if not await is_owner(event):
        return
    try:
        quote = random.choice(QUOTES)
        text = f"""
✧ حكمة ✧

{quote}

✧ سورس عبود ✧"""
        await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.نسبه الحب(?: (.+))?$'))
async def love_percent(event):
    if not await is_owner(event):
        return
    text = event.pattern_match.group(1) if event.pattern_match.group(1) else ""
    if not text:
        await event.reply("❌ اكتب اسمين مفصولين بفاصلة\nمثال: .نسبه الحب احمد, سارة")
        return
    names = [name.strip() for name in text.split(',')]
    if len(names) < 2:
        await event.reply("❌ اكتب اسمين مفصولين بفاصلة")
        return
    percent = random.randint(0, 100)
    heart = "❤️" * (percent // 10) + "🖤" * (10 - percent // 10)
    await event.reply(f"""
✧ نسبة الحب ✧

💑 {names[0]} 🤝 {names[1]}

💕 النسبة: {percent}%
{heart}

✧ سورس عبود ✧
""")

# =====================================================================
#                        أَوَامِرُ التَّحْمِيلِ
# =====================================================================

async def download_audio(event, url):
    ytd_copy = ytd.copy()
    ytd_copy["format"] = "bestaudio"
    ytd_copy["outtmpl"] = "%(id)s.m4a"
    ytd_copy["postprocessors"] = [
        {"key": "FFmpegExtractAudio", "preferredcodec": "m4a", "preferredquality": "128"},
        {"key": "FFmpegMetadata"}
    ]
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ytd_copy) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.m4a').replace('.m4a', '.m4a')
            await event.client.send_file(event.chat_id, filename, caption="🎵 تم التحميل")
            os.remove(filename)
    except Exception as e:
        await event.reply(f"❌ خطأ في التحميل: {str(e)}")

async def download_video(event, url):
    ytd_copy = ytd.copy()
    ytd_copy["format"] = "best"
    ytd_copy["outtmpl"] = "%(id)s.mp4"
    ytd_copy["postprocessors"] = [
        {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        {"key": "FFmpegMetadata"}
    ]
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ytd_copy) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp4')
            await event.client.send_file(event.chat_id, filename, caption="🎬 تم التحميل")
            os.remove(filename)
    except Exception as e:
        await event.reply(f"❌ خطأ في التحميل: {str(e)}")

async def search_and_download_audio(event, query):
    ytd_copy = ytd.copy()
    ytd_copy["format"] = "bestaudio"
    ytd_copy["outtmpl"] = "%(id)s.m4a"
    ytd_copy["postprocessors"] = [
        {"key": "FFmpegExtractAudio", "preferredcodec": "m4a", "preferredquality": "128"},
        {"key": "FFmpegMetadata"}
    ]
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ytd_copy) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            if info and 'entries' in info:
                entry = info['entries'][0]
                filename = ydl.prepare_filename(entry).replace('.webm', '.m4a')
                await event.client.send_file(event.chat_id, filename, caption=f"🎵 {query}")
                os.remove(filename)
            else:
                await event.reply("❌ لم يتم العثور على نتيجة")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.تحميل صوتي (.+)$'))
async def download_audio_command(event):
    if not await is_owner(event):
        return
    url = event.pattern_match.group(1).strip()
    if not url:
        await event.reply("❌ يجب عليك وضع رابط للتحميل الصوتي")
        return
    await event.reply("🎵 جاري تحميل الملف الصوتي...")
    await download_audio(event, url)

@client.on(events.NewMessage(pattern=r'^\.تحميل فيد (.+)$'))
async def download_video_command(event):
    if not await is_owner(event):
        return
    url = event.pattern_match.group(1).strip()
    if not url:
        await event.reply("❌ يجب عليك وضع رابط لتحميل الفيديو")
        return
    await event.reply("🎬 جاري تحميل الفيديو...")
    await download_video(event, url)

@client.on(events.NewMessage(pattern=r'^\.صوتي(?: (.+))?$'))
async def search_audio_command(event):
    if not await is_owner(event):
        return
    query = event.pattern_match.group(1) if event.pattern_match.group(1) else None
    if not query:
        await event.reply("❌ يجب عليك تحديد ما تريد تحميله، اكتب عنوان مع الأمر")
        return
    await event.reply(f"🎵 جاري البحث عن: {query}...")
    await search_and_download_audio(event, query)

# =====================================================================
#                        أَمْرُ الْكَاشِفِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.الكاشف$'))
async def cmd(event):
    if not await is_owner(event):
        return
    await edit_or_reply(event, """
سورس عبود @SSSTlF - كاشف الارقام العربية

الامر :
.كاشف + اسم الدولة + الرقم بدون مفتاح الدولة

الوصف :
- لجلب معلومات عن رقم هاتف معين

مثال :
.كاشف اليمن 777887798
.كاشف السعوديه 555542317
.كاشف الامارات 43171234

الامر يدعم الدول التالية : 🇾🇪🇸🇦🇦🇪🇰🇼🇶🇦🇧🇭🇴🇲

سورس عبود @SSSTlF
""")

@client.on(events.NewMessage(pattern=r'^\.كاشف ?(.*)'))
async def phone_info(event):
    if not await is_owner(event):
        return
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id and not event.pattern_match.group(1):
        reply_to_id = await event.get_reply_message()
        reply_to_id = str(reply_to_id.message)
    else:
        reply_to_id = str(event.pattern_match.group(1))
    if not reply_to_id:
        return await edit_or_reply(event, "كاشف الارقام العربية .. ارسل .الكاشف للتعليمات")
    chat = "@Zelzalybot"
    zzzzl1l = await edit_or_reply(event, "جاري الكشف عن الرقم ...")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(events.NewMessage(incoming=True, from_users=1194140165))
            await event.client.send_message(chat, "{}".format(input_str))
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await zzzzl1l.edit("تحقق من انك لم تقم بحظر البوت @Zelzalybot .. ثم اعيد استخدام الامر")
            return
        if response.text.startswith("I can't find that"):
            await zzzzl1l.edit("عذراً .. لم استطع ايجاد المطلوب")
        else:
            await zzzzl1l.delete()
            await event.client.send_message(event.chat_id, response.message)

# =====================================================================
#                        أَوَامِرُ حِمَايَةِ الْخَاصِّ
# =====================================================================

# تفعيل حماية الخاص إذا كان PMSETTING مفعل
if PMSETTING:
    if AUTOAPPROVE:
        @client.on(events.NewMessage(
            outgoing=True,
            func=lambda e: e.is_private and e.out and not e.text.startswith('.'),
        ))
        async def autoappr(e):
            miss = await e.get_chat()
            if miss.bot or miss.is_self or miss.verified:
                return
            if is_approved(miss.id):
                return
            approve_user(miss.id)
            await delete_pm_warn_msgs(miss.id)
            try:
                await client.edit_folder(miss.id, folder=0)
            except BaseException:
                pass

    @client.on(events.NewMessage(
        incoming=True,
        func=lambda e: e.is_private
        and e.sender_id not in [client.uid]
        and not e.out
    ))
    async def permitpm(event):
        sender = await event.get_sender()
        if (sender.bot or sender.verified or sender.is_self):
            return
        user = event.sender
        if not is_approved(user.id):
            if MOVE_ARCHIVE:
                try:
                    await client.edit_folder(user.id, folder=1)
                except BaseException:
                    pass
            if event.media:
                try:
                    await event.delete()
                except:
                    pass
            name = user.first_name
            fullname = get_display_name(user)
            username = f"@{user.username}"
            mention = inline_mention(user)
            try:
                wrn = COUNT_PM[user.id] + 1
            except:
                wrn = 1
            if user.id in LASTMSG:
                prevmsg = LASTMSG[user.id]
                if event.text != prevmsg:
                    if "نظام حماية تيبثون" in event.text or "**نظام حماية تيبثون" in event.text:
                        return
                    await delete_pm_warn_msgs(user.id)
                    message_ = UNAPPROVED_MSG.format(
                        ON=(await client.get_me()).first_name,
                        warn=wrn,
                        twarn=PMWARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        mention=mention,
                    )
                    update_pm(user.id, message_, wrn)
                    if PMPIC:
                        _to_delete[user.id] = await client.send_file(
                            user.id,
                            PMPIC,
                            caption=message_,
                        )
                    else:
                        _to_delete[user.id] = await client.send_message(
                            user.id, message_
                        )
                else:
                    await delete_pm_warn_msgs(user.id)
                    message_ = UNAPPROVED_MSG.format(
                        ON=(await client.get_me()).first_name,
                        warn=wrn,
                        twarn=PMWARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        mention=mention,
                    )
                    update_pm(user.id, message_, wrn)
                    if PMPIC:
                        _to_delete[user.id] = await client.send_file(
                            user.id,
                            PMPIC,
                            caption=message_,
                        )
                    else:
                        _to_delete[user.id] = await client.send_message(
                            user.id, message_
                        )
                LASTMSG.update({user.id: event.text})
            else:
                await delete_pm_warn_msgs(user.id)
                message_ = UNAPPROVED_MSG.format(
                    ON=(await client.get_me()).first_name,
                    warn=wrn,
                    twarn=PMWARNS,
                    UND=UND,
                    name=name,
                    fullname=fullname,
                    username=username,
                    mention=mention,
                )
                update_pm(user.id, message_, wrn)
                if PMPIC:
                    _to_delete[user.id] = await client.send_file(
                        user.id,
                        PMPIC,
                        caption=message_,
                    )
                else:
                    _to_delete[user.id] = await client.send_message(
                        user.id, message_
                    )
                LASTMSG.update({user.id: event.text})
            if user.id not in COUNT_PM:
                COUNT_PM.update({user.id: 1})
            else:
                COUNT_PM[user.id] = COUNT_PM[user.id] + 1
            if COUNT_PM[user.id] >= PMWARNS:
                await delete_pm_warn_msgs(user.id)
                _to_delete[user.id] = await event.respond(UNS)
                try:
                    del COUNT_PM[user.id]
                    del LASTMSG[user.id]
                except KeyError:
                    pass
                await client(BlockRequest(user.id))

@client.on(events.NewMessage(pattern=r'^\.(تشغيل|ايقاف|مسح) الارشفة$'))
async def archive_cmd(event):
    if not await is_owner(event):
        return
    x = event.pattern_match.group(1).strip()
    if x == "تشغيل":
        addgvar("MOVE_ARCHIVE", "True")
        await event.reply("**⎆ من الآن سيتم نقل المستخدم الغير مسموح له إلى الأرشيف**")
    elif x == "ايقاف":
        addgvar("MOVE_ARCHIVE", "False")
        await event.reply("**⎆ من الآن سيتم إلغاء النقل عن المستخدم الغير مسموح له إلى الأرشيف**")
    elif x == "مسح":
        try:
            await client.edit_folder(unpack=1)
            await event.reply("**✦ تم إلغاء أرشيـف جميع المحادثات بنجاح ✓**")
        except Exception as mm:
            await event.reply(str(mm))

@client.on(events.NewMessage(pattern=r'^\.(س|سماح)(?: |$)'))
async def approvepm(event):
    if not await is_owner(event):
        return
    if event.reply_to_msg_id:
        user = (await event.get_reply_message()).sender
    elif event.is_private:
        user = await event.get_chat()
    else:
        return await event.reply(NO_REPLY)
    
    if is_approved(user.id):
        return await event.reply("**⎆ هذا المستخدم مسموح بالدردشة معك بالأصـل 🔔**")
    
    approve_user(user.id)
    try:
        await delete_pm_warn_msgs(user.id)
        await client.edit_folder(user.id, folder=0)
    except BaseException:
        pass
    await event.reply(f"<b>{inline_mention(user, html=True)}</b> <code>تم السماح له بالدردشة معك</code>", parse_mode="html")

@client.on(events.NewMessage(pattern=r'^\.(ر|رفض)(?: |$)'))
async def disapprovepm(event):
    if not await is_owner(event):
        return
    if event.reply_to_msg_id:
        user = (await event.get_reply_message()).sender
    elif event.is_private:
        user = await event.get_chat()
    else:
        return await event.reply(NO_REPLY)
    
    if not is_approved(user.id):
        return await event.reply(f"<b>{inline_mention(user, html=True)}</b> <code>المستخدم مرفوض بالأصل</code>", parse_mode="html")
    
    disapprove_user(user.id)
    await event.reply(f"<b>{inline_mention(user, html=True)}</b> <code>تم رفضه من الدردشة معك</code>", parse_mode="html")

@client.on(events.NewMessage(pattern=r'^\.بلوك( (.*)|$)'))
async def blockpm(event):
    if not await is_owner(event):
        return
    match = event.pattern_match.group(1).strip()
    if event.reply_to_msg_id:
        user_id = (await event.get_reply_message()).sender_id
    elif match:
        try:
            user = await event.client.get_entity(match)
            user_id = user.id
        except:
            return await event.reply("❌ المستخدم غير موجود!")
    elif event.is_private:
        user_id = event.chat_id
    else:
        return await event.reply(NO_REPLY)
    
    try:
        user = await event.client.get_entity(user_id)
    except:
        user = None
    
    await event.client(BlockRequest(user_id))
    if is_approved(user_id):
        disapprove_user(user_id)
    await event.reply(f"**⌔∮ المستخدم: {inline_mention(user) if user else user_id}** [`{user_id}`]\n**❃ تم حظره من الدردشة معك في الخاص**")

@client.on(events.NewMessage(pattern=r'^\.الغاء البلوك( (.*)|$)'))
async def unblockpm(event):
    if not await is_owner(event):
        return
    match = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    
    if reply:
        user_id = reply.sender_id
    elif match:
        if match == "للكل":
            msg = await event.reply("**⎆ جـاري إلغـاء حظر المستخدم من الخاص...**")
            u_s = await event.client(GetBlockedRequest(0, 0))
            count = len(u_s.users)
            if not count:
                return await msg.edit("**⎆ كـم أنـت حنون 😍، لا يوجد محظورين لفك الحظر عنهم**")
            for user in u_s.users:
                await asyncio.sleep(1)
                await event.client(UnblockRequest(user.id))
            return await msg.edit(f"**⌔∮ تم بنجاح الغاء حظر {count} من المستخدمين من الخاص**")
        try:
            user = await event.client.get_entity(match)
            user_id = user.id
        except:
            return await event.reply("❌ المستخدم غير موجود!")
    elif event.is_private:
        user_id = event.chat_id
    else:
        return await event.reply(NO_REPLY)
    
    try:
        user = await event.client.get_entity(user_id)
    except:
        user = None
    
    try:
        await event.client(UnblockRequest(user_id))
        await event.reply(f"**⌔∮ المستخدم:{inline_mention(user) if user else user_id}** [`{user_id}`]\n**❃ تم إلغـاء حظره من الخاص بنجاح**")
    except Exception as et:
        await event.reply(f"ERROR - {et}")

@client.on(events.NewMessage(pattern=r'^\.قائمة المسموحين$'))
async def list_approved(event):
    if not await is_owner(event):
        return
    approved = get_approved()
    if not approved:
        return await event.reply("**هممممم، لا يوجد مستخدمين مسموحين لديك 💔**")
    users = []
    for i in approved:
        try:
            name = get_display_name(await client.get_entity(i))
        except BaseException:
            name = "غير معروف"
        users.append(f"• {name} (`{i}`)")
    text = "**⌔∮ قائمة المستخدمين المسموح لهم بالدردشة:**\n\n" + "\n".join(users)
    await event.reply(text)

# =====================================================================
#                        فِلْتَرُ الرَّسَائِلِ
# =====================================================================

@client.on(events.NewMessage())
async def protection_filter(event):
    if event.is_private:
        return
    chat_id = event.chat_id
    sender = await event.get_sender()
    try:
        me = await client.get_me()
        if sender.id == me.id:
            return
    except:
        pass
    try:
        permissions = await client.get_permissions(chat_id, sender.id)
        if permissions.is_admin or permissions.is_creator:
            return
    except:
        pass
    text = event.raw_text
    if is_locked(chat_id, "badwords"):
        bad_words = ["خرا", "كسها", "كسمك", "كسختك", "عيري", "طيز", "سكس", "نيك", "زب", "اير", "خول", "عرص"]
        if any(word in text for word in bad_words):
            try:
                await event.delete()
                await event.reply(f"⚠️ @{sender.username or sender.id} ممنوع الألفاظ البذيئة!")
            except:
                pass
    if is_locked(chat_id, "links"):
        if "http" in text or "www." in text:
            try:
                await event.delete()
                await event.reply(f"⚠️ @{sender.username or sender.id} ممنوع إرسال الروابط!")
            except:
                pass

# =====================================================================
#                        مُعَالِجُ الْوَقْتِ
# =====================================================================

@client.on(events.NewMessage(outgoing=True))
async def add_time_to_message(event):
    global time_enabled
    if not event.out or not time_enabled:
        return
    try:
        now = get_saudi_time()
        time_str = now.strftime("%I:%M %p")
        me = await client.get_me()
        first_name = me.first_name or ""
        last_name = me.last_name or ""
        name_parts = first_name.split(' ⌚')
        clean_name = name_parts[0]
        new_name = f"{clean_name} ⌚ {time_str}"
        await update_name(new_name, last_name)
    except Exception as e:
        print(f"خطأ في تحديث الاسم: {e}")

# =====================================================================
#                        خَادِمُ الْوَيْبِ
# =====================================================================

async def run_web_server():
    try:
        from aiohttp import web
        async def handle(request):
            return web.Response(text="✅ سورس عبود - البوت يعمل!")
        app = web.Application()
        app.router.add_get('/', handle)
        app.router.add_get('/health', handle)
        port = int(os.environ.get("PORT", 10000))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        print(f"✅ خادم الويب يعمل على المنفذ {port}")
        await asyncio.Event().wait()
    except ImportError:
        print("aiohttp غير مثبت - خادم الويب معطل")
    except Exception as e:
        print(f"خطأ في تشغيل خادم الويب: {e}")

# =====================================================================
#                        حَلْقَةُ الْإِبْقَاءِ
# =====================================================================

async def keep_alive():
    """مراقبة اتصال العميل بدون إرسال رسائل مزعجة للحساب."""
    while True:
        try:
            if not client.is_connected():
                await client.connect()
            print(f"✅ الاتصال سليم — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"⚠️ مشكلة اتصال: {e}")
        await asyncio.sleep(600)

# =====================================================================
#                        التَّشْغِيلُ الرَّئِيسِيُّ
# =====================================================================

async def main():
    try:
        print("🚀 جاري تشغيل البوت...")
        print("✧ سورس عبود ✧ @SSSTlF")
        if not SESSION:
            print("⏳ انتظر إرسال الجلسة...")
            await client.run_until_disconnected()
            return
        await client.start()
        me = await client.get_me()
        print(f"✅ البوت يعمل كـ: {me.first_name} (ID: {me.id})")
        
        # تشغيل البوت المساعد
        if BOT_TOKEN:
            await start_bot()
        
        asyncio.create_task(keep_alive())
        asyncio.create_task(run_web_server())
        print("✅ البوت جاهز لاستقبال الأوامر")
        print("✧ سورس عبود ✧ @SSSTlF")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)
