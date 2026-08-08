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
    InputChatPhotoEmpty
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
    WebpageMediaEmptyError
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
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.utils import get_input_location, get_display_name
from telethon.events import CallbackQuery

# ========== مكتبات خاصة ==========
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None
    print("⚠️ Pillow غير مثبت - سيتم تعطيل ميزات الصور")

try:
    from pySmartDL import SmartDL
except ImportError:
    SmartDL = None
    print("⚠️ pySmartDL غير مثبت")

try:
    from requests import get
except ImportError:
    get = None
    print("⚠️ requests غير مثبت")

try:
    from fake_useragent import UserAgent
except ImportError:
    UserAgent = None
    print("⚠️ fake_useragent غير مثبت")

# ========== خادم ويب ==========
try:
    from aiohttp import web
except ImportError:
    web = None
    print("⚠️ aiohttp غير مثبت - سيتم تعطيل خادم الويب")

# ========== heroku3 ==========
try:
    import heroku3
except ImportError:
    heroku3 = None
    print("⚠️ heroku3 غير مثبت - سيتم تعطيل أوامر هيروكو")

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

# ========== تحميل الإعدادات ==========
def load_config():
    """تحميل الإعدادات من ملف JSON"""
    default_config = {
        "api_id": 0,
        "api_hash": "",
        "session_string": "",
        "time_enabled": False,
        "saudi_offset_hours": 3,
        "quotes": [
            "★ النجاح ليس نهائياً، والفشل ليس قاتلاً: الشجاعة للاستمرار هي ما يهم.",
            "★ كن التغيير الذي تريد رؤيته في العالم.",
            "★ الحياة ليست عن إيجاد الذات، الحياة عن خلق الذات.",
            "★ المستقبل لأولئك الذين يؤمنون بجمال أحلامهم.",
            "★ لا تخف من الفشل، اخشَ عدم المحاولة.",
            "★ أفضل طريقة لبدء المستقبل هي صنعه.",
            "★ الطريقة الوحيدة للقيام بعمل عظيم هي أن تحب ما تفعله.",
            "★ لا تضيع وقتك في الحلم بالنجاح، اعمل من أجله.",
            "★ الصبر مفتاح الفرج، والمثابرة طريق النجاح.",
            "★ كل يوم هو فرصة جديدة لتغيير حياتك.",
            "★ العلم نور والجهل ظلام.",
            "★ من جد وجد، ومن زرع حصد.",
            "★ خير الناس أنفعهم للناس.",
            "★ السعادة ليست في المال، بل في القناعة.",
            "★ التواضع من أخلاق النبلاء.",
            "★ ابتسم فأنت جميل بابتسامتك.",
            "★ لا تيأس فالحياة جميلة.",
            "★ كن كالنحلة تأكل طيباً وتصنع طيباً.",
            "★ الصديق وقت الضيق.",
            "★ الوفاء من شيم الكرام.",
            "★ الحياة مثل الدراجة، لتحافظ على توازنك يجب أن تستمر في الحركة.",
            "★ النجاح ليس مفتاح السعادة، السعادة هي مفتاح النجاح.",
            "★ أحب الناس كما تحب أن يحبوك.",
            "★ خير الكلام ما قل ودل.",
            "★ العلم بلا عمل كالشجر بلا ثمر."
        ],
        "download_settings": {
            "prefer_ffmpeg": True,
            "addmetadata": True,
            "geo-bypass": True,
            "nocheckcertificate": True
        },
        "commands": {
            "time_enable": ".تفعيل الوقت",
            "time_disable": ".تعطيل الوقت",
            "install": ".تنصيب",
            "install_session": ".تنصيب جلسة",
            "my_info": ".ا",
            "developer": ".المطور",
            "get_id": ".ايدي",
            "search": ".بحث",
            "video": ".فيديو",
            "audio": ".اغنية",
            "quote": ".كت",
            "download_audio": ".تحميل صوتي",
            "download_video": ".تحميل فيد",
            "search_audio": ".صوتي",
            "help": ".الاوامر"
        },
        "locks": {}
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
            print(f"❌ خطأ في تحميل الإعدادات: {e}")
            return default_config
    else:
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            print("✅ تم إنشاء ملف الإعدادات config.json")
        except Exception as e:
            print(f"❌ خطأ في حفظ الإعدادات: {e}")
        return default_config

CONFIG = load_config()

# ========== دوال المتغيرات العامة (Globals) ==========
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

# ========== دوال الأقفال (Locks) ==========
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

# ========== دوال الكتم (Mute) ==========
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

# ========== دوال No Log PM ==========
def load_no_log():
    if os.path.exists(NO_LOG_FILE):
        try:
            with open(NO_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_no_log(data):
    with open(NO_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_no_log(chat_id):
    data = load_no_log()
    return data.get(str(chat_id), False)

def set_no_log(chat_id, value):
    data = load_no_log()
    data[str(chat_id)] = value
    save_no_log(data)

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

# ========== SQL helper محاكاة ==========
class SQLMock:
    def __init__(self):
        self.data = {}
    
    def get_collection(self, name):
        class Collection:
            def __init__(self, data):
                self.json = data
        return Collection(self.data.get(name, {}))
    
    def del_collection(self, name):
        if name in self.data:
            del self.data[name]
    
    def add_collection(self, name, data, extra):
        self.data[name] = data

sql = SQLMock()

class PMPermitMock:
    def __init__(self):
        self.approved = {}
    
    def is_approved(self, user_id):
        return str(user_id) in self.approved
    
    def approve(self, user_id, first_name, date, username, reason):
        self.approved[str(user_id)] = {"first_name": first_name, "date": date, "username": username, "reason": reason}
    
    def disapprove(self, user_id):
        if str(user_id) in self.approved:
            del self.approved[str(user_id)]
    
    def disapprove_all(self):
        self.approved = {}
    
    def get_all_approved(self):
        class User:
            def __init__(self, user_id, data):
                self.user_id = user_id
                self.first_name = data["first_name"]
                self.date = data["date"]
                self.username = data["username"]
                self.reason = data["reason"]
        return [User(int(uid), data) for uid, data in self.approved.items()]

pmpermit_sql = PMPermitMock()

class GlobalList:
    def __init__(self):
        self.lists = {}
    
    def get_collection_list(self, name):
        return self.lists.get(name, [])
    
    def add_to_list(self, name, item):
        if name not in self.lists:
            self.lists[name] = []
        if item not in self.lists[name]:
            self.lists[name].append(item)
    
    def rm_from_list(self, name, item):
        if name in self.lists and item in self.lists[name]:
            self.lists[name].remove(item)

sqllist = GlobalList()

class NoLogPMSQL:
    def is_approved(self, chat_id):
        return False

no_log_pms_sql = NoLogPMSQL()

class GlobalCollectionJSON:
    def get_collection(self, name):
        class Collection:
            def __init__(self, data):
                self.json = data
        return Collection(sql.data.get(name, {}))

sqljson = GlobalCollectionJSON()

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", CONFIG.get("api_id", 0)))
API_HASH = os.environ.get("API_HASH", CONFIG.get("api_hash", ""))
SESSION = os.environ.get("SESSION_STRING", CONFIG.get("session_string", ""))

if not API_ID or not API_HASH:
    print("❌ تأكد من تعيين API_ID و API_HASH في المتغيرات أو ملف config.json")
    print("⚠️ سيتم استخدام القيم الافتراضية للتجربة")
    API_ID = 2040
    API_HASH = "b18441a1ff607e10a989891a5462e627"

# ========== متغيرات هيروكو ==========
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY")
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
Heroku = heroku3.from_key(HEROKU_API_KEY) if HEROKU_API_KEY and heroku3 else None
heroku_api = "https://api.heroku.com"

# ========== متغيرات عامة ==========
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

# ========== متغيرات التنصيب المصنع ==========
factory_active = False
factory_user_id = None
factory_step = "waiting"

# ========== متغيرات الوقتية ==========
digitalpic_running = False
autoname_running = False
autobio_running = False

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
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

# ========== إنشاء عميل ==========
if SESSION:
    print("✅ جاري استخدام الجلسة المخزنة...")
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
else:
    print("❌ لا توجد جلسة! استخدم أمر التنصيب.")
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
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_object = await event.client.get_entity(previous_message.sender_id)
    else:
        user = event.pattern_match.group(1) if hasattr(event.pattern_match, 'group') and event.pattern_match.group(1) else None
        if user and user.isnumeric():
            user = int(user)
        if not user:
            self_user = await event.client.get_me()
            user = self_user.id
        if event.message.entities:
            probable_user_mention_entity = event.message.entities[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        if isinstance(user, int) or (user and user.startswith("@")):
            user_obj = await event.client.get_entity(user)
            return user_obj
        try:
            user_object = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None
    return user_object

def get_saudi_time():
    utc_now = datetime.utcnow()
    saudi_time = utc_now + SAUDI_OFFSET
    return saudi_time

async def is_owner(event):
    if event.raw_text and any(cmd in event.raw_text for cmd in OWNER_ONLY_COMMANDS):
        return True
    try:
        me = await event.client.get_me()
        sender = await event.get_sender()
        return sender.id == me.id
    except:
        return False

OWNER_ONLY_COMMANDS = ['.تنصيب', '.تنصيب جلسة', '.تنصيب مصنع']

async def update_name(first_name, last_name=None):
    try:
        request = UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name or ""
        )
        await client(request)
        return True
    except Exception as e:
        print(f"❌ خطأ في تحديث الاسم: {e}")
        return False

def save_config():
    try:
        CONFIG["time_enabled"] = time_enabled
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(CONFIG, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"❌ خطأ في حفظ الإعدادات: {e}")
        return False

async def reply_id(event):
    if event.reply_to_msg_id:
        return event.reply_to_msg_id
    return None

def mention(user):
    if hasattr(user, 'first_name'):
        return f"[{user.first_name}](tg://user?id={user.id})"
    return f"[مستخدم](tg://user?id={user.id})"

async def get_readable_time(seconds):
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["ثانية", "دقيقة", "ساعة", "يوم"]
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
    return "✅", "تعمل بنجاح ✓"

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

# =====================================================================
#                        الكود المتبقي مع إصلاح الخطأ
# =====================================================================

# هنا سيتم وضع جميع الأوامر المطلوبة بنفس الترتيب السابق
# ولكن مع إصلاح خطأ def tgbot

# =====================================================================
#                        فئة الديكورات (المعدلة)
# =====================================================================

class jmthon:
    @staticmethod
    def ar_cmd(pattern=None, command=None, info=None, disable_errors=False):
        def decorator(func):
            return func
        return decorator
    
    @staticmethod
    def on(event):
        def decorator(func):
            return func
        return decorator
    
    @staticmethod
    def tgbot():
        def decorator(func):
            return func
        return decorator

# =====================================================================
#                        أَمْرُ فَحْص (ALIVE)
# =====================================================================

ALIVE_ET = Config.ALIVE_ET or "فحص"

@jmthon.ar_cmd(pattern=f"{ALIVE_ET}(?:\s|$)([\s\S]*)")
async def amireallyalive(event):
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time.time() - StartTime))
    start = datetime.now()
    await edit_or_reply(event, "** ⌯︙يتـم التـأكـد انتـظر قليلا رجاءا**")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    _, check_sgnirts = check_data_base_heal_th()
    EMOJI = gvarstatus("ALIVE_EMOJI") or "✇ ◅"
    ALIVE_TEXT = gvarstatus("ALIVE_TEXT") or "**[ سورس عبود يعمل ✓ ](t.me/SSSTlF)**"
    RR7_IMG = gvarstatus("ALIVE_PIC") or Config.A_PIC
    temp = """{ALIVE_TEXT}
**{EMOJI} قاعدة البيانات ↜ ** تعمل بنجاح ✓
**{EMOJI} إصدار التيليثون ↜ :** `{telever}`
**{EMOJI} إصدار سورس عبود ↜ :** `{jmver}`
**{EMOJI} إصدار البايثون ↜ :** `{pyver}`
**{EMOJI} الوقت ↜ :** `{uptime}`
**{EMOJI} البنك ↜ :** `{ping}`
**{EMOJI} المستخدم ↜:** {mention}"""
    jmthon_caption = gvarstatus("ALIVE_TEMPLATE") or temp
    caption = jmthon_caption.format(
        ALIVE_TEXT=ALIVE_TEXT,
        EMOJI=EMOJI,
        mention=mention(await event.client.get_me()),
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
        except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
            return await edit_or_reply(
                event,
                f"**الميديا خطأ **\nغير الرابط باستخدام الأمر \n `.اضف_فار ALIVE_PIC رابط صورتك`\n\n**لا يمكن الحصول على صورة من الرابط :-** `{PIC}`",
            )
    else:
        await edit_or_reply(event, caption)

# =====================================================================
#                        أَمْرُ إِعَادَةِ التَّشْغِيلِ
# =====================================================================

@jmthon.ar_cmd(pattern="اعادة تشغيل$")
async def restart_bot(event):
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "**⌯︙إعادة التشغيل ↻** \n**⌯︙تم إعادة تشغيل البوت ↻**")
    RR7PP = await edit_or_reply(event, "**⌯︙جاري إعادة التشغيل، قد يستغرق الأمر 2-3 دقائق لا تقم بإعادة التشغيل مرة أخرى انتظر ⏱**")
    try:
        await client.disconnect()
    except:
        pass
    try:
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
    except:
        await RR7PP.edit("⚠️ أعد تشغيل البوت يدوياً")

@jmthon.ar_cmd(pattern="اطفاء$")
async def shutdown_bot(event):
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "**⌯︙إيقاف التشغيل ✕ **\n**⌯︙تم إيقاف تشغيل البوت بنجاح ✓**")
    await edit_or_reply(event, "**⌯︙جاري إيقاف تشغيل البوت الآن ..**\n⌯︙ **أعد تشغيل يدوياً لاحقاً عبر هيروكو ..**\n⌯︙**سيبقى البوت متوقفاً عن العمل**")
    if HEROKU_APP_NAME and HEROKU_API_KEY and Heroku:
        app = Heroku.app(HEROKU_APP_NAME)
        app.process_formation()["worker"].scale(0)
    else:
        sys.exit(0)

@jmthon.ar_cmd(pattern="التحديثات (تشغيل|ايقاف)$")
async def set_pmlog(event):
    input_str = event.pattern_match.group(1)
    if input_str == "ايقاف":
        if gvarstatus("restartupdate") is None:
            return await edit_delete(event, "**⌯︙تم تعطيل التحديثات بالفعل ❗️**")
        delgvar("restartupdate")
        return await edit_or_reply(event, "**⌯︙تم تعطيل التحديثات بنجاح ✓**")
    if gvarstatus("restartupdate") is None:
        addgvar("restartupdate", "turn-oned")
        return await edit_or_reply(event, "**⌯︙تم تشغيل التحديثات بنجاح ✓**")
    await edit_delete(event, "**⌯︙تم تشغيل التحديثات بالفعل ❗️**")

# =====================================================================
#                        أَمْرُ الِانْتِحَالِ
# =====================================================================

@jmthon.ar_cmd(pattern="انتحال(?:\s|$)([\s\S]*)")
async def clone_account(event):
    replied_user, error_i_a = await get_user_from_event(event)
    if replied_user is None:
        return
    user_id = replied_user.id
    profile_pic = await event.client.download_profile_photo(user_id, "downloads")
    first_name = html.escape(replied_user.first_name or "مستخدم")
    first_name = first_name.replace("\u2060", "")
    last_name = replied_user.last_name
    if last_name:
        last_name = html.escape(last_name).replace("\u2060", "")
    else:
        last_name = " "
    replied_user_full = await event.client(GetFullUserRequest(replied_user.id))
    user_bio = replied_user_full.about or ""
    await event.client(UpdateProfileRequest(first_name=first_name))
    await event.client(UpdateProfileRequest(last_name=last_name))
    await event.client(UpdateProfileRequest(about=user_bio))
    if profile_pic:
        pfile = await event.client.upload_file(profile_pic)
        await event.client(UploadProfilePhotoRequest(pfile))
        os.remove(profile_pic)
    await edit_delete(event, "⌯︙تم نسخ الحساب بنجاح ✅")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, f"#CLONED\nsuccessfully cloned [{first_name}](tg://user?id={user_id})")

@jmthon.ar_cmd(pattern="اعادة$")
async def revert_account(event):
    name = f"{DEFAULTUSER}"
    bio = gvarstatus("DEFAULT_BIO") or "سورس عبود @SSSTlF"
    await event.client(DeletePhotosRequest(await event.client.get_profile_photos("me", limit=1)))
    await event.client(UpdateProfileRequest(about=bio))
    await event.client(UpdateProfileRequest(first_name=name))
    await event.client(UpdateProfileRequest(last_name=""))
    await edit_delete(event, "⌯︙تم إعادة الحساب إلى وضعه الأصلي ✅")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, f"⌯︙تم إعادة الحساب الى وضعه الأصلي ✅")

# =====================================================================
#                        أَوَامِرُ الْفَارَاتِ (HEROKU VARS)
# =====================================================================

@jmthon.ar_cmd(pattern="وضع (.*)")
async def set_var(var):
    if not HEROKU_API_KEY or not HEROKU_APP_NAME:
        return await edit_delete(var, "عزيزي المستخدم يجب تعيين `HEROKU_API_KEY` و `HEROKU_APP_NAME`.")
    app = Heroku.app(HEROKU_APP_NAME)
    rep = await var.get_reply_message()
    vra = rep.text if rep else var.pattern_match.group(1)
    if not vra:
        return await edit_delete(var, "**⌯︙يجب عليك الرد على النص أو الرابط حسب الفار الذي تضيفه**")
    exe = var.pattern_match.group(1)
    await edit_or_reply(var, "**⌯︙جاري وضع الفار انتظر قليلا**")
    heroku_var = app.config()
    var_map = {
        "توقيت": "TZ",
        "رمز الاسم": "TIME_JEP",
        "البايو": "DEFAULT_BIO",
        "النبذة": "DEFAULT_BIO",
        "الصورة": "DIGITAL_PIC",
        "الصوره": "DIGITAL_PIC",
        "زخرفة الارقام": "JP_FN",
        "زخرفه الارقام": "JP_FN",
        "اسم": "ALIVE_NAME",
        "الاسم": "ALIVE_NAME",
        "كروب التخزين": "PM_LOGGER_GROUP_ID",
        "كروب الحفظ": "PRIVATE_GROUP_BOT_API_ID"
    }
    if exe in var_map:
        heroku_var[var_map[exe]] = vra
        await edit_or_reply(var, f"**⌯︙تم بنجاح تغيير فار {exe}\n\n❃ جار إعادة تشغيل السورس انتظر من 2-5 دقائق ليتشغل مرة أخرى**")

@jmthon.ar_cmd(pattern="ازالة (.*)")
async def del_var(event):
    if not HEROKU_API_KEY or not HEROKU_APP_NAME:
        return await edit_delete(event, "عزيزي المستخدم يجب تعيين `HEROKU_API_KEY` و `HEROKU_APP_NAME`.")
    app = Heroku.app(HEROKU_APP_NAME)
    exe = event.pattern_match.group(1)
    heroku_var = app.config()
    await edit_or_reply(event, "**⌯︙جاري حذف الفار انتظر قليلا**")
    var_map = {
        "رمز الاسم": "TIME_JEP",
        "البايو": "DEFAULT_BIO",
        "النبذة": "DEFAULT_BIO",
        "الصورة": "DIGITAL_PIC",
        "الصوره": "DIGITAL_PIC",
        "زخرفة الارقام": "JP_FN",
        "زخرفه الارقام": "JP_FN",
        "اسم": "ALIVE_NAME",
        "الاسم": "ALIVE_NAME",
        "كروب التخزين": "PM_LOGGER_GROUP_ID",
        "كروب الحفظ": "PRIVATE_GROUP_BOT_API_ID"
    }
    if exe in var_map and var_map[exe] in heroku_var:
        del heroku_var[var_map[exe]]
        await edit_or_reply(event, f"**⌯︙تم بنجاح حذف فار {exe}\n\n❃ جار إعادة تشغيل السورس انتظر من 2-5 دقائق ليتشغل مرة أخرى**")
    else:
        await edit_or_reply(event, f"**⌯︙لم تتم إضافة فار {exe} بالأصل.**")

@jmthon.ar_cmd(pattern="وقت(?:\s|$)([\s\S]*)")
async def set_time_zone(event):
    if not HEROKU_API_KEY or not HEROKU_APP_NAME:
        return await edit_delete(event, "عزيزي المستخدم يجب تعيين `HEROKU_API_KEY` و `HEROKU_APP_NAME`.")
    app = Heroku.app(HEROKU_APP_NAME)
    exe = event.pattern_match.group(1)
    heroku_var = app.config()
    time_zones = {
        "العراق": "Asia/Baghdad",
        "عراق": "Asia/Baghdad",
        "السعودية": "Asia/Riyadh",
        "السعوديه": "Asia/Riyadh",
        "مصر": "Africa/Cairo",
        "الاردن": "Asia/Amman",
        "اليمن": "Asia/Aden",
        "سوريا": "Asia/Damascus"
    }
    if exe in time_zones:
        heroku_var["TZ"] = time_zones[exe]
        await edit_or_reply(event, f"**⌯︙تم بنجاح تغيير الوقت إلى {exe}\n\n❃ جار إعادة تشغيل السورس انتظر من 2-5 دقائق**")

@jmthon.ar_cmd(pattern="استخدامي$")
async def dyno_usage(dyno):
    if not HEROKU_API_KEY or not HEROKU_APP_NAME:
        return await edit_delete(dyno, "عزيزي المستخدم يجب تعيين `HEROKU_API_KEY` و `HEROKU_APP_NAME`.")
    dyno = await edit_or_reply(dyno, "**- يتم جلب المعلومات انتظر قليلا**")
    useragent = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36"
    user_id = Heroku.account().id
    headers = {"User-Agent": useragent, "Authorization": f"Bearer {HEROKU_API_KEY}", "Accept": "application/vnd.heroku+json; version=3.account-quotas"}
    r = get(heroku_api + f"/accounts/{user_id}/actions/get-quota", headers=headers)
    if r.status_code != 200:
        return await dyno.edit(f"**خطأ: {r.reason}**")
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = int(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = int(minutes_remaining // 60)
    minutes = int(minutes_remaining % 60)
    App = result["apps"]
    try:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = int(App[0]["quota_used"] * 100 / quota)
    except (IndexError, KeyError):
        AppQuotaUsed = 0
        AppPercentage = 0
    AppHours = int(AppQuotaUsed // 60)
    AppMinutes = int(AppQuotaUsed % 60)
    await asyncio.sleep(1.5)
    return await dyno.edit(f"**استخدام الدينو**:\n\n"
        f" -> استخدام الدينو لتطبيق **{HEROKU_APP_NAME}**:\n"
        f"     • `{AppHours}` ساعات `{AppMinutes}` دقائق **|** [`{AppPercentage}`%]\n\n"
        f" -> الساعات المتبقية لهذا الشهر:\n"
        f"     • `{hours}` ساعات `{minutes}` دقائق **|** [`{percentage}`%]")

@jmthon.ar_cmd(pattern="لوك$")
async def heroku_logs(dyno):
    if not HEROKU_API_KEY or not HEROKU_APP_NAME:
        return await edit_delete(dyno, "عزيزي المستخدم يجب تعيين `HEROKU_API_KEY` و `HEROKU_APP_NAME`.")
    try:
        app = Heroku.app(HEROKU_APP_NAME)
        data = app.get_log()
        await edit_or_reply(dyno, data, deflink=True, linktext="**آخر 100 سطر في لوك هيروكو:**")
    except Exception as e:
        await edit_or_reply(dyno, f"**خطأ:** `{str(e)}`")

# =====================================================================
#                        أَوَامِرُ الْفَارَاتِ فِي قَاعِدَةِ الْبَيَانَاتِ
# =====================================================================

vlist = [
    "ALIVE_PIC", "ALIVE_EMOJI", "ALIVE_TEMPLATE", "ALIVE_TEXT",
    "SC_TEXT", "PM_PIC", "PM_TEXT", "PM_BLOCK", "MAX_FLOOD_IN_PMS",
    "START_TEXT", "TIME_JM", "CUSTOM_STICKER_PACKNAME", "ALIVE_NAME", "ID_ET"
]

oldvars = {"PM_PIC": "pmpermit_pic", "PM_TEXT": "pmpermit_txt", "PM_BLOCK": "pmblock"}

@jmthon.ar_cmd(pattern="(اضف_|معلومات_|حذف_)فار(?: |$)([\s\S]*)")
async def db_var(event):
    cmd = event.pattern_match.group(1).lower()
    vname = event.pattern_match.group(2)
    vnlist = "".join(f"{i+1}. `{each}`\n" for i, each in enumerate(vlist))
    if not vname:
        return await edit_delete(event, f"**📑 يجب وضع المتغير الصحيح من هنا:\n\n{vnlist}**", time=60)
    vinfo = None
    if " " in vname:
        vname, vinfo = vname.split(" ", 1)
    reply = await event.get_reply_message()
    if not vinfo and reply:
        vinfo = reply.text
    if vname in vlist:
        if vname in oldvars:
            vname = oldvars[vname]
        if cmd == "اضف_":
            if not vinfo:
                return await edit_delete(event, "**⌯︙يجب وضع القيمة الصحيحة أولاً**")
            check = vinfo.split(" ")
            for i in check:
                if (("PIC" in vname) or ("pic" in vname)) and url and not url(i):
                    return await edit_delete(event, "**⌯︙يجب وضع رابط صحيح أولاً**")
            addgvar(vname, vinfo)
            await edit_delete(event, f"📑 القيمة **{vname}**\nتم تغييرها لـ: `{vinfo}`", time=20)
        elif cmd == "معلومات_":
            var_data = gvarstatus(vname)
            await edit_delete(event, f"📑 القيمة لـ **{vname}** هي `{var_data}`", time=20)
        elif cmd == "حذف_":
            delgvar(vname)
            await edit_delete(event, f"📑 القيمة لـ **{vname}**\nتم حذفها ووضع القيمة الأصلية لها", time=20)
    else:
        await edit_delete(event, f"**📑 يجب وضع المتغير الصحيح من هذه القائمة:\n\n{vnlist}**", time=60)

# =====================================================================
#                        أَمْرُ ضِيفْ (إضافة الأعضاء)
# =====================================================================

async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except:
            await event.reply("**⌯︙لم يتم العثور على المجموعة أو القناة**")
            return None
    return chat_info

@jmthon.ar_cmd(pattern=r"ضيف ?(.*)")
async def add_users(event):
    sender = await event.get_sender()
    me = await event.client.get_me()
    if sender.id != me.id:
        roz = await event.reply("**⌯︙تتم العملية انتظر قليلا 🧸♥ ...**")
    else:
        roz = await event.edit("**⌯︙تتم العملية انتظر قليلا 🧸♥ ...**")
    JepThon = await get_chatinfo(event)
    chat = await event.get_chat()
    if event.is_private:
        return await roz.edit("**⌯︙لا يمكنني إضافة المستخدمين هنا**")
    s = 0
    f = 0
    error = 'None'
    await roz.edit("**⌯︙حالة الإضافة:**\n\n**⌯︙يتم جمع معلومات المستخدمين 🔄 ...⌣**")
    async for user in event.client.iter_participants(JepThon.full_chat.id):
        try:
            if error.startswith("Too"):
                return await roz.edit(f"**حالة الإضافة انتهت مع الأخطاء**\n(**ربما هناك ضغط على الأمر حاول مجددا لاحقا 🧸**)\n**الخطأ:**\n`{error}`\n\n• أضيف `{s}`\n• خطأ بإضافة `{f}`")
            await event.client(InviteToChannelRequest(channel=chat, users=[user.id]))
            s += 1
            await roz.edit(f"**⌯︿ تتم الإضافة 🧸♥**\n\n• أضيف `{s}`\n• خطأ بإضافة `{f}`\n\n**× آخر خطأ:** `{error}`")
        except Exception as e:
            error = str(e)
            f += 1
    return await roz.edit(f"**⌯︿ اكتملت الإضافة ✅**\n\n• تم بنجاح إضافة `{s}`\n• خطأ بإضافة `{f}`")

# =====================================================================
#                        أَمْرُ تَخْزِينِ الْخَاصِّ وَالْكُرُوبَاتِ
# =====================================================================

class LOG_CHATS:
    def __init__(self):
        self.RECENT_USER = None
        self.NEWPM = None
        self.COUNT = 0

LOG_CHATS_ = LOG_CHATS()

@jmthon.ar_cmd(incoming=True, func=lambda e: e.is_private, edited=False)
async def monitor_pms(event):
    if Config.PM_LOGGER_GROUP_ID == -100:
        return
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") == "false":
        return
    sender = await event.get_sender()
    if not sender.bot:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id) and chat.id != 777000:
            if LOG_CHATS_.RECENT_USER != chat.id:
                LOG_CHATS_.RECENT_USER = chat.id
                if LOG_CHATS_.NEWPM:
                    if LOG_CHATS_.COUNT > 1:
                        await LOG_CHATS_.NEWPM.edit(LOG_CHATS_.NEWPM.text.replace("رسالة جديدة", f"{LOG_CHATS_.COUNT} "))
                    else:
                        await LOG_CHATS_.NEWPM.edit(LOG_CHATS_.NEWPM.text.replace("رسالة جديدة", f"{LOG_CHATS_.COUNT} "))
                    LOG_CHATS_.COUNT = 0
                LOG_CHATS_.NEWPM = await event.client.send_message(
                    Config.PM_LOGGER_GROUP_ID,
                    f"👤{mention(sender)}\n**قام بإرسال رسالة جديدة**\nايدي الشخص: `{chat.id}`",
                )
            try:
                if event.message:
                    await event.client.forward_messages(Config.PM_LOGGER_GROUP_ID, event.message, silent=True)
                LOG_CHATS_.COUNT += 1
            except Exception as e:
                pass

@jmthon.ar_cmd(pattern="تخزين الخاص (تشغيل|ايقاف)$")
async def set_pmlog(event):
    input_str = event.pattern_match.group(1)
    h_type = True if input_str == "تشغيل" else False
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") == "false":
        PMLOG = False
    else:
        PMLOG = True
    if PMLOG:
        if h_type:
            await event.edit("**⌯︙تخزين رسائل الخاص بالفعل ممكنة ✅**")
        else:
            addgvar("PMLOG", False)
            await event.edit("**⌯︙تم تعطيل تخزين رسائل الخاص بنجاح ✅**")
    elif h_type:
        addgvar("PMLOG", True)
        await event.edit("**⌯︙تم تفعيل تخزين رسائل الخاص بنجاح ✅**")
    else:
        await event.edit("**⌯︙تخزين رسائل الخاص بالفعل معطلة ✅**")

@jmthon.ar_cmd(pattern="تخزين الكروبات (تشغيل|ايقاف)$")
async def set_grplog(event):
    input_str = event.pattern_match.group(1)
    h_type = True if input_str == "تشغيل" else False
    if gvarstatus("GRPLOG") and gvarstatus("GRPLOG") == "false":
        GRPLOG = False
    else:
        GRPLOG = True
    if GRPLOG:
        if h_type:
            await event.edit("**⌯︙تخزين رسائل الكروبات بالفعل ممكنة ✅**")
        else:
            addgvar("GRPLOG", False)
            await event.edit("**⌯︙تم تعطيل تخزين رسائل الكروبات بنجاح ✅**")
    elif h_type:
        addgvar("GRPLOG", True)
        await event.edit("**⌯︙تم تفعيل تخزين رسائل الكروبات بنجاح ✅**")
    else:
        await event.edit("**⌯︙تخزين رسائل الكروبات بالفعل معطلة ✅**")

# =====================================================================
#                        أَمْرُ حِمَايَةِ الْخَاصِّ (PM PERMIT)
# =====================================================================

async def do_pm_permit_action(event, chat):
    reply_to_id = await reply_id(event)
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError:
        PM_WARNS = {}
    try:
        PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
    except AttributeError:
        PMMESSAGE_CACHE = {}
    me = await event.client.get_me()
    mention_user = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    first = chat.first_name
    last = chat.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{chat.username}" if chat.username else mention_user
    userid = chat.id
    my_first = me.first_name
    my_last = me.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{me.username}" if me.username else my_mention
    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0
    try:
        MAX_FLOOD_IN_PMS = int(gvarstatus("MAX_FLOOD_IN_PMS") or 6)
    except (ValueError, TypeError):
        MAX_FLOOD_IN_PMS = 6
    totalwarns = MAX_FLOOD_IN_PMS + 1
    warns = PM_WARNS[str(chat.id)] + 1
    remwarns = totalwarns - warns
    if PM_WARNS[str(chat.id)] >= MAX_FLOOD_IN_PMS:
        try:
            if str(chat.id) in PMMESSAGE_CACHE:
                await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
                del PMMESSAGE_CACHE[str(chat.id)]
        except Exception as e:
            pass
        custompmblock = gvarstatus("pmblock") or None
        if custompmblock is not None:
            USER_BOT_WARN_ZERO = custompmblock.format(mention=mention_user, first=first, last=last, fullname=fullname, username=username, userid=userid, my_first=my_first, my_last=my_last, my_fullname=my_fullname, my_username=my_username, my_mention=my_mention, totalwarns=totalwarns, warns=warns, remwarns=remwarns)
        else:
            USER_BOT_WARN_ZERO = "⌯︙حذرك وكتلك لا تكرر تم حظرك بنجاح ما أكدر اخليك تزعج المالك \n- ⌯︙بباي 🙁🤍"
        msg = await event.reply(USER_BOT_WARN_ZERO)
        await event.client(BlockRequest(chat.id))
        the_message = f"#المحظورين_الحمايه\n[{get_display_name(chat)}](tg://user?id={chat.id}) تم حظره\n⌯︙عدد الرسائل: {PM_WARNS[str(chat.id)]}"
        del PM_WARNS[str(chat.id)]
        sql.del_collection("pmwarns")
        sql.del_collection("pmmessagecache")
        sql.add_collection("pmwarns", PM_WARNS, {})
        sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
        try:
            return await event.client.send_message(BOTLOG_CHATID, the_message)
        except BaseException:
            return
    custompmpermit = gvarstatus("pmpermit_txt") or None
    if custompmpermit is not None:
        USER_BOT_NO_WARN = custompmpermit.format(mention=mention_user, first=first, last=last, fullname=fullname, username=username, userid=userid, my_first=my_first, my_last=my_last, my_fullname=my_fullname, my_username=my_username, my_mention=my_mention, totalwarns=totalwarns, warns=warns, remwarns=remwarns)
    elif gvarstatus("pmmenu") is None:
        USER_BOT_NO_WARN = f"""ههلا بيك {mention_user} \n مالك الحساب غير موجود حاليا الرجاء الانتظار وعدم تكرار الرسائل. 
لديك {warns}/{totalwarns} من التحذيرات لا تكرر حتى ما تنحظر من البوت.
اختر احد الخيارات في الاسفل وانتظر الى ان اصبح متصلا بالانترنت ليتم الرد عليك ⬇️⬇️"""
    else:
        USER_BOT_NO_WARN = f"""ههلا بيك {mention_user} \n مالك الحساب غير موجود حاليا الرجاء الانتظار وعدم تكرار الرسائل. 
لديك {warns}/{totalwarns} من التحذيرات لا تكرر حتى ما تنحظر من البوت.
لا تكرر اذكر سبب مجيئك فقط"""
    addgvar("pmpermit_text", USER_BOT_NO_WARN)
    PM_WARNS[str(chat.id)] += 1
    try:
        if gvarstatus("pmmenu") is None:
            results = await event.client.inline_query(Config.TG_BOT_USERNAME, "pmpermit")
            msg = await results[0].click(chat.id, reply_to=reply_to_id, hide_via=True)
        else:
            PM_PIC = gvarstatus("pmpermit_pic")
            if PM_PIC:
                CAT = [x for x in PM_PIC.split()]
                PIC = list(CAT)
                CAT_IMG = random.choice(PIC)
            else:
                CAT_IMG = None
            if CAT_IMG is not None:
                msg = await event.client.send_file(chat.id, CAT_IMG, caption=USER_BOT_NO_WARN, reply_to=reply_to_id)
            else:
                msg = await event.client.send_message(chat.id, USER_BOT_NO_WARN, reply_to=reply_to_id)
    except Exception as e:
        msg = await event.reply(USER_BOT_NO_WARN)
    try:
        if str(chat.id) in PMMESSAGE_CACHE:
            await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            del PMMESSAGE_CACHE[str(chat.id)]
    except Exception as e:
        pass
    PMMESSAGE_CACHE[str(chat.id)] = msg.id
    sql.del_collection("pmwarns")
    sql.del_collection("pmmessagecache")
    sql.add_collection("pmwarns", PM_WARNS, {})
    sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})

@jmthon.ar_cmd(incoming=True, func=lambda e: e.is_private, edited=False)
async def on_new_private_message(event):
    if gvarstatus("pmpermit") is None:
        return
    chat = await event.get_chat()
    if chat.bot or chat.verified:
        return
    if pmpermit_sql.is_approved(chat.id):
        return
    if str(chat.id) in sqllist.get_collection_list("pmspam"):
        return
    if str(chat.id) in sqllist.get_collection_list("pmchat"):
        return
    if str(chat.id) in sqllist.get_collection_list("pmrequest"):
        return
    if str(chat.id) in sqllist.get_collection_list("pmenquire"):
        return
    if str(chat.id) in sqllist.get_collection_list("pmoptions"):
        return
    await do_pm_permit_action(event, chat)

@jmthon.ar_cmd(pattern="الحماية (تشغيل|تعطيل)$")
async def pmpermit_on(event):
    input_str = event.pattern_match.group(1)
    if input_str == "تشغيل":
        if gvarstatus("pmpermit") is None:
            addgvar("pmpermit", "true")
            await edit_delete(event, "⌯︙تم تفعيل أمر الحماية لحسابك بنجاح ✅")
        else:
            await edit_delete(event, "⌯︙أمر الحماية بالفعل ممكن لحسابك 🌿")
    elif gvarstatus("pmpermit") is not None:
        delgvar("pmpermit")
        await edit_delete(event, "⌯︙تم تعطيل أمر الحماية لحسابك بنجاح ✅")
    else:
        await edit_delete(event, "⌯︙أمر الحماية بالفعل معطل لحسابك 🌿")

@jmthon.ar_cmd(pattern="(س|سماح)(?:\s|$)([\s\S]*)")
async def approve_pm(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, "⌯︙يجب تفعيل أمر الحماية أولاً بإرسال `.الحماية تشغيل`")
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        user, reason = await get_user_from_event(event, secondgroup=True)
        if not user:
            return
    if not reason:
        reason = "لم يذكر"
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError:
        PM_WARNS = {}
    if not pmpermit_sql.is_approved(user.id):
        if str(user.id) in PM_WARNS:
            del PM_WARNS[str(user.id)]
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        pmpermit_sql.approve(user.id, get_display_name(user), start_date, user.username, reason)
        for list_name in ["pmspam", "pmchat", "pmrequest", "pmenquire", "pmoptions"]:
            if str(user.id) in sqllist.get_collection_list(list_name):
                sqllist.rm_from_list(list_name, user.id)
        await edit_delete(event, f"⌯︙[{user.first_name}](tg://user?id={user.id})\n⌯︙تم السماح له بإرسال الرسائل \nالسبب: {reason}")
        try:
            PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
        except AttributeError:
            PMMESSAGE_CACHE = {}
        if str(user.id) in PMMESSAGE_CACHE:
            try:
                await event.client.delete_messages(user.id, PMMESSAGE_CACHE[str(user.id)])
            except Exception:
                pass
            del PMMESSAGE_CACHE[str(user.id)]
        sql.del_collection("pmwarns")
        sql.del_collection("pmmessagecache")
        sql.add_collection("pmwarns", PM_WARNS, {})
        sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
    else:
        await edit_delete(event, f"[{user.first_name}](tg://user?id={user.id})\n⌯︙هو بالفعل في قائمة السماح")

@jmthon.ar_cmd(pattern="(ر|رفض)(?:\s|$)([\s\S]*)")
async def disapprove_pm(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, "⌯︙يجب تفعيل أمر الحماية أولاً")
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        reason = event.pattern_match.group(2)
        if reason != "الكل":
            user, reason = await get_user_from_event(event, secondgroup=True)
            if not user:
                return
    if reason == "الكل":
        pmpermit_sql.disapprove_all()
        return await edit_delete(event, "⌯︙حسنا تم رفض الجميع بنجاح 🧸♥")
    if not reason:
        reason = "لم يذكر"
    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)
        await edit_or_reply(event, f"[{user.first_name}](tg://user?id={user.id})\n⌯︙تم رفضه من إرسال الرسائل\nالسبب: {reason}")
    else:
        await edit_delete(event, f"[{user.first_name}](tg://user?id={user.id})\n⌯︙لم يتم الموافقة عليه بالأصل")

@jmthon.ar_cmd(pattern="بلوك(?:\s|$)([\s\S]*)")
async def block_pm(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, "⌯︙يجب تفعيل أمر الحماية أولاً")
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user:
            return
    if not reason:
        reason = "لم يتم ذكره"
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError:
        PM_WARNS = {}
    try:
        PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
    except AttributeError:
        PMMESSAGE_CACHE = {}
    if str(user.id) in PM_WARNS:
        del PM_WARNS[str(user.id)]
    if str(user.id) in PMMESSAGE_CACHE:
        try:
            await event.client.delete_messages(user.id, PMMESSAGE_CACHE[str(user.id)])
        except Exception:
            pass
        del PMMESSAGE_CACHE[str(user.id)]
    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)
    sql.del_collection("pmwarns")
    sql.del_collection("pmmessagecache")
    sql.add_collection("pmwarns", PM_WARNS, {})
    sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
    await event.client(BlockRequest(user.id))
    await edit_delete(event, f"[{user.first_name}](tg://user?id={user.id})\n تم حظره بنجاح لا يمكنه مراسلتك بعد الآن 🧸♥\nالسبب: {reason}")

@jmthon.ar_cmd(pattern="انبلوك(?:\s|$)([\s\S]*)")
async def unblock_pm(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, "⌯︙يجب تفعيل أمر الحماية أولاً")
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user:
            return
    if not reason:
        reason = "لم يتم ذكر السبب"
    await event.client(UnblockRequest(user.id))
    await event.edit(f"[{user.first_name}](tg://user?id={user.id})\nتم الغاء حظره بنجاح يمكنه التكلم معك الآن 🧸♥\nالسبب: {reason}")

@jmthon.ar_cmd(pattern="المسموح لهم$")
async def list_approved(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, "⌯︙يجب تفعيل أمر الحماية أولاً")
    approved_users = pmpermit_sql.get_all_approved()
    APPROVED_PMs = "⌯︙قائمة المسموح لهم الحالية\n\n"
    if len(approved_users) > 0:
        for user in approved_users:
            APPROVED_PMs += f"• 👤 {mention(user)}\n⌯︙الأيدي: `{user.user_id}`\n⌯︙المعرف: @{user.username}\n⌯︙التاريخ: {user.date}\n⌯︙السبب: {user.reason}\n\n"
    else:
        APPROVED_PMs = "انت لم توافق على أي شخص بالأصل 🧸♥️"
    await edit_or_reply(event, APPROVED_PMs, caption="قائمة المسموح لهم الحالية\n سورس عبود \n @SSSTlF")

# =====================================================================
#                        أَمْرُ النَّوْمِ (AFK)
# =====================================================================

class AFK:
    def __init__(self):
        self.USERAFK_ON = {}
        self.afk_time = None
        self.last_afk_message = {}
        self.afk_star = {}
        self.afk_end = {}
        self.reason = None
        self.msg_link = False
        self.afk_type = None
        self.media_afk = None
        self.afk_on = False

AFK_ = AFK()

@jmthon.ar_cmd(outgoing=True, edited=False)
async def set_not_afk(event):
    if AFK_.afk_on is False:
        return
    back_alive = datetime.now()
    AFK_.afk_end = back_alive.replace(microsecond=0)
    if AFK_.afk_star != {}:
        total_afk_time = AFK_.afk_end - AFK_.afk_star
        time_seconds = int(total_afk_time.seconds)
        d = time_seconds // (24 * 3600)
        time_seconds %= 24 * 3600
        h = time_seconds // 3600
        time_seconds %= 3600
        m = time_seconds // 60
        time_seconds %= 60
        s = time_seconds
        endtime = ""
        if d > 0:
            endtime += f"{d} الأيام {h} الساعات {m} الدقائق {s} الثواني"
        elif h > 0:
            endtime += f"{h} الساعات {m} الدقائق {s} الثواني"
        else:
            endtime += f"{m} الدقائق {s} الثواني" if m > 0 else f"{s} الثواني"
    current_message = event.message.message
    if (("afk" not in current_message) or ("#afk" not in current_message)) and ("on" in AFK_.USERAFK_ON):
        shite = await event.client.send_message(event.chat_id, "⌯︙**تم تعطيل أمر النوم والرجوع إلى الوضع الطبيعي**")
        AFK_.USERAFK_ON = {}
        AFK_.afk_time = None
        await asyncio.sleep(5)
        await shite.delete()
        AFK_.afk_on = False
        if BOTLOG:
            await event.client.send_message(BOTLOG_CHATID, f"⌯︙انتهاء أمر النوم\n⌯︙تم تعطيله والرجوع للوضع الطبيعي كان مفعل لـ {endtime}")

@jmthon.ar_cmd(incoming=True, func=lambda e: bool(e.mentioned or e.is_private), edited=False)
async def on_afk(event):
    if AFK_.afk_on is False:
        return
    back_alivee = datetime.now()
    AFK_.afk_end = back_alivee.replace(microsecond=0)
    if AFK_.afk_star != {}:
        total_afk_time = AFK_.afk_end - AFK_.afk_star
        time_seconds = int(total_afk_time.seconds)
        d = time_seconds // (24 * 3600)
        time_seconds %= 24 * 3600
        h = time_seconds // 3600
        time_seconds %= 3600
        m = time_seconds // 60
        time_seconds %= 60
        s = time_seconds
        endtime = ""
        if d > 0:
            endtime += f"{d} الأيام {h} الساعات {m} الدقائق {s} الثواني"
        elif h > 0:
            endtime += f"{h} الساعات {m} الدقائق {s} الثواني"
        else:
            endtime += f"{m} الدقائق {s} الثواني" if m > 0 else f"{s} الثواني"
    current_message_text = event.message.message.lower()
    if "afk" in current_message_text or "#afk" in current_message_text:
        return False
    if not await event.get_sender():
        return
    if AFK_.USERAFK_ON and not (await event.get_sender()).bot:
        msg = None
        if AFK_.afk_type == "media":
            message_to_reply = f"- **عمري أني هسة نايم** \n- **مدة النوم:** {endtime}"
            if event.chat_id:
                msg = await event.reply(message_to_reply, file=AFK_.media_afk.media)
        elif AFK_.afk_type == "text":
            message_to_reply = f"- **عمري أني هسة نايم** \n- **مدة النوم:** {endtime}"
            if event.chat_id:
                msg = await event.reply(message_to_reply)
        if event.chat_id in AFK_.last_afk_message:
            await AFK_.last_afk_message[event.chat_id].delete()
        AFK_.last_afk_message[event.chat_id] = msg

@jmthon.ar_cmd(pattern="نوم(?:\s|$)([\s\S]*)")
async def set_afk_media(event):
    reply = await event.get_reply_message()
    media_t = media_type(reply)
    if media_t == "Sticker" or not media_t:
        return await edit_or_reply(event, "⌯︙أمر النوم: المرجو قم بالرد على الصورة بالأمر")
    if not BOTLOG:
        return await edit_or_reply(event, "⌯︙لاستخدام هذا الأمر يجب إضافة متغير PRIVATE_GROUP_BOT_API_ID")
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = {}
    AFK_.media_afk = None
    AFK_.afk_type = "media"
    start_1 = datetime.now()
    AFK_.afk_on = True
    AFK_.afk_star = start_1.replace(microsecond=0)
    if not AFK_.USERAFK_ON:
        input_str = event.pattern_match.group(1)
        AFK_.reason = input_str
        last_seen_status = await event.client(GetPrivacyRequest(types.InputPrivacyKeyStatusTimestamp()))
        if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
            AFK_.afk_time = datetime.now()
        AFK_.USERAFK_ON = f"on: {AFK_.reason}"
        await edit_delete(event, "⌯︙انا الان في وضعية النوم يرجى المراسلة لاحقاً", 5)
        AFK_.media_afk = await reply.forward_to(BOTLOG_CHATID)
        await event.client.send_message(BOTLOG_CHATID, f"**⌯︙أمر النوم 💤:**\n**تم تشغيل الأمر ❕**")

# =====================================================================
#                        جَمِيعُ أَوَامِرِ الشَّرْحِ
# =====================================================================

@jmthon.ar_cmd(pattern="اوامر الحظر$")
async def ban_commands(event):
    await event.edit(
        "شرح عن أوامر الحظر \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n( `.حظر` ) \n- تقوم بالرد على شخص او وضع معرفه مع الامر وسيحظره من المجموعة\n\n( `.الغاء حظر` )\n- بالرد على الشخص او كتابة معرفه مع الامر لالغاء حظره\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الكتم$")
async def mute_commands(event):
    await event.edit(
        "شرح عن أوامر الكتم \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n( `.كتم` ) \n- تقوم بالرد على شخص او وضع معرفه مع الامر وسيكتمه من المجموعة\n\n( `.الغاء كتم` )\n- بالرد على الشخص او كتابة معرفه مع الامر لالغاء كتمه\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التثبيت$")
async def pin_commands(event):
    await event.edit(
        "شرح عن أوامر التثبيت \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n( `.تثبيت` ) \n- تقوم بالرد على الرسالة مع الامر وستثبت في المجموعة\n\n( `.الغاء التثبيت` )\n- بالرد على الرسالة مع الامر لإلغاء تثبيتها\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الاشراف$")
async def admin_commands(event):
    await event.edit(
        "شرح عن أوامر الاشراف \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n( `.رفع مشرف` ) \n- تقوم بالرد على الشخص مع الامر و سيرفع مشرفا في المجموعة\n\n( `.تنزيل مشرف` )\n- بالرد على الشخص مع الامر لإنزاله من الاشراف في المجموعة\n\n( `.اخفاء` ) \n- لرفع المستخدم في جميع المجموعات مع كافة الصلاحيات مع لقب مخفي\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التفليش$")
async def flush_commands(event):
    await event.edit(
        "شرح عن أوامر التفليش \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.تفليش` ) \n ارسل الامر لحظر جميع الاعضاء من المجموعه\n\n- ( `.تصفير` ) \n كتابة الامر فقط في المجموعه لطرد جميع الاعضاء\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر المحذوفين$")
async def deleted_commands(event):
    await event.edit(
        "شرح عن أوامر المحذوفين \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.مسح المحظورين` ) \n كتابة الامر في الكروب لالغاء حظر جميع الاعضاء \n\n- ( `.غادر` ) \n فقط ارسل الامر في المجموعة لمغادرة المجموعه التي تم ارسال الامر فيها\n\n- ( `.المحذوفين` ) \n لعرض الحسابات المحذوفة في مجموعة معينة ولحذفهم ارسل .المحذوفين تنظيف\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الكروب$")
async def group_commands(event):
    await event.edit(
        "شرح عن أوامر الكروب \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.الاحداث` ) \n كتابة الامر في الكروب لعرض احداث الكروب\n\n- ( `.الاعضاء` ) \n فقط ارسل الامر في المجموعة لعرض اعضاء المجموعة\n\n- ( `.المشرفين` ) \n ارسل الامر في المجموعه لعرض حسابات المشرفين\n\n- ( `.البوتات` )\n ارسل الامر في المجموعه لعرض البوتات\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الترحيب$")
async def welcome_commands(event):
    await event.edit(
        "شرح عن أوامر الترحيب \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.ترحيب + ترحيبك` )\n اكتب الامر مع ترحيب في المجموعه ليرحب بالاعضاء الجدد\n\n- ( `.حذف الترحيبات` ) \n فقط ارسل الامر في المجموعة لحذف الترحيبات\n\n- ( `.الترحيبات` )\n ارسل الامر في المجموعه لعرض ترحيبات المجموعة\n\n- ( `.الترحيب السابق ايقاف/تشغيل` )\n لتعطيل اخر ترحيب وضعته في المجموعة او تشغيل\n\n- ( `.رحب + ترحيبك` )\n لوضع ترحيب في عند دخول الاعضاء للمجموعة سوف يرحب بهم في الخاص\n\n- ( `.حذف رحب` )\n لحذف الترحيب في الخاص\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الردود$")
async def reply_commands(event):
    await event.edit(
        "شرح عن أوامر الردود \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.اضف رد + ردك` ) \n لوضع رد معين في المجموعة اكتب الامر وردك\n\n- ( `.حذف الردود` ) \n فقط ارسل الامر في المجموعة لحذف الردود المضافة\n\n- ( `.الردود` ) \n ارسل الامر في المجموعه لعرض ردود المجموعة\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الحماية$")
async def pm_commands(event):
    await event.edit(
        "شرح عن أوامر الخاص \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.الحماية تشغيل/تعطيل` ) \n لتشغيل امر الحمايه او تعطيله في الخاص \n\n- ( `.سماح` ) \n بالرد على الشخص للسماح له بالتكلم في الخاص\n\n- ( `.رفض` ) \n بالرد على الشخص لرفضه من الخاص \n\n- ( `.المسموح لهم` )\n فقط ارسل الامر لاظهار الاشخاص المسموح لهم والمرفوضين\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التلكراف$")
async def telegraph_commands(event):
    await event.edit(
        "شرح عن أوامر التلكراف \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.تلكراف ميديا` ) \n لاستخراج رابط من الصورة على شكل رابط تلكراف\n\n- ( `.تلكراف نص` ) \n بالرد على النص او المقالة لصنع رابط تلكراف للنص\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الانتحال$")
async def clone_commands(event):
    await event.edit(
        "شرح عن أوامر الانتحال \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.انتحال` ) \n بالرد على الشخص لنسخ حسابه بالكامل من صورة واسم وبايو\n\n- ( `.اعادة` ) \n لارجاع الحساب الى وضعه الطبيعي لما كان سابقا\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التقليد$")
async def mimic_commands(event):
    await event.edit(
        "شرح عن أوامر التقليد \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.تقليد` ) \n بالرد على الشخص لتقليد جميع رسائله في الدردشه\n\n- ( `.الغاء التقليد` ) \n بالرد على الشخص لايقاف التقليد\n\n- ( `.المقلدهم` ) \nلاظهار قائمه الاشخاص الذي فعلت عليهم امر التقليد ولمسحهم ارسل (`.مسح المقلدهم`)\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر المنشن$")
async def mention_commands(event):
    await event.edit(
        "شرح عن أوامر المنشن \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.تاك + معرف + نص` ) \n لعمل تاك لشخص في الكروب و وضع التاك في النص \n- مثال | .تاك @SSSTlF ههلا\n\n- ( `.للكل + نص` ) \n لعمل تاك للكل مع النص اكتب الامر مع النص وارسله فقط\n\n- ( `.ابلاغ` )\n بالرد على الشخص لعمل ابلاغ لمشرفين المجموعة\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التحميل$")
async def download_commands(event):
    await event.edit(
        "شرح عن أمر التحميل\n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر\n\n- (`.بحث + اسم الاغنية`)\nبكتابة اسم الاغنية مع الامر لارسال الاغنيه مباشرا واذا ما اشتغل جرب اوامر التحميل الاخرى\n- مثال : `.بحث ماهر زين`\n\n- (`.يوت + اسم الفيديو او الاغنية`)\nكتابة الامر مع اسم الفيديو او الاغنية ليعطيك نتائج البحث وروابط من يوتيوب تستخدم مع اوامر التحميل\n- مثال : `.يوت ماهر زين`\n\n- (`.تحميل ص + رابط الاغنية`)\nلتحميل اغنيه من خلال وضع الرابط مع الامر\n- مثال : `.تحميل ص https://youtube.com/...`\n\n- (`.تحميل ف + رابط الفيديو`)\nكتابة الامر مع رابط المقطع لتحميله وارساله\n- مثال : `.تحميل ف https://youtube.com/...`\n\n- (`.انستا + الرابط `)\nيستخدم هذا الامر لتحميل من الانستا فقط اكتب الامر مع رابط الفيديو ليحمله\n- مثال : `.انستا https://instagram.com/jdisjejjd...`\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الترجمة$")
async def translate_commands(event):
    await event.edit(
        "شرح عن أوامر الترجمة \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.ترجمة ar` ) \n بالرد على النص لترجمته للغه العربية\n\n- ( `.ترجمة en` ) \n بالرد على النص لترجمته للغه الانكليزية\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر النطق$")
async def speech_commands(event):
    await event.edit(
        "شرح عن أوامر النطق \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.تكلم ar` ) \n بالرد على النص لتحويله الى مقطع صوتي للغة العربيه\n\n- ( `.تكلم en` ) \n بالرد على النص لتحوليه الى مقطع صوتي للغه الانكليزية\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر القفل$")
async def lock_commands(event):
    await event.edit(
        "شرح عن أوامر القفل \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.قفل + الاضافة` ) \n تكتب الامر مع الاضافة لقفل شي معين في المجموعة \n\nالاضافات : \n - الدردشه : لقفل ارسال الرسائل \n- الوسائط : لقفل ارسال الوسائط\n- الملصقات : لقفل ارسال الملصقات\n- الروابط : لقفل ارسال الروابط\n- المتحركه : لقفل ارسال المتحركه\n- الالعاب : لقفل ارسال الالعاب الانلاين\n- الانلاين : لقفل ارسال البوتات الانلاين\n- التصويت : لقفل ارسال التوصيتات\n- الكل : لقفل ارسال كل شي\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الفتح$")
async def unlock_commands(event):
    await event.edit(
        "شرح عن أوامر الفتح \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.فتح + الاضافة` ) \n تكتب الامر مع الاضافة لفتح شي معين في المجموعة \n\nالاضافات : \n - الدردشه : لفتح ارسال الرسائل\n- الوسائط : لفتح ارسال الوسائط\n- الملصقات : لفتح ارسال الملصقات\n- الروابط : لفتح ارسال الروابط\n- المتحركه : لفتح ارسال المتحركه\n- الالعاب : لفتح ارسال الالعاب الانلاين\n- الانلاين : لفتح ارسال البوتات الانلاين\n- التصويت : لفتح ارسال التوصيتات\n- الكل : لفتح ارسال كل شي\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر المنع$")
async def blockword_commands(event):
    await event.edit(
        "شرح عن أوامر المنع \n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر \n\n- ( `.منع + الكلمة` ) \n لمنع الكلمة في الدردشة وسيتم حذفها عند ارسالها من اي شخص\n\n- ( `.الغاء منع + الكلمة` ) \n لالغاء منع الكلمة والسماح للجميع بأرسالها في الدردشة\n\n- ( `.قائمة المنع` ) \nلاظهار قائمه الكلمات التي منعتها في الدردشه\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="تسلية 1$")
async def fun1_commands(event):
    await event.edit(
        "قائمة اوامر التسلية 1 :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.غبي` )\n- ( `.القنابل` )\n- ( `.اتصل` )\n- ( `.قتل` )\n- ( `.شنو` )\n- ( `.طوبة` )\n- ( `.مربعات` )\n- ( `.حلويات` )\n- ( `.نار` )\n- ( `.شحن` )\n\nتحذير : لا تكثر من استخدام هذه الاوامر لانها قد تسبب ضغط على حسابك او تعليقه من ارسال الرسائل لفترة وجيزة.\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="تسلية 2$")
async def fun2_commands(event):
    await event.edit(
        "قائمة اوامر التسلية 2 :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.افكر` )\n- ( `.متت` )\n- ( `.ضايج` )\n- ( `.ساعه` )\n- ( `.مح` )\n- ( `.قلب` )\n- ( `.جيم` )\n- ( `.الارض` )\n- ( `.قمر` )\n- ( `.اقمار` )\n- ( `.قمور` )\n\nتحذير : لا تكثر من استخدام هذه الاوامر لانها قد تسبب ضغط على حسابك او تعليقه من ارسال الرسائل لفترة وجيزة.\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="تسلية 3$")
async def fun3_commands(event):
    await event.edit(
        "قائمة اوامر التسلية 3 :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.نجمه` )\n- ( `.مكعبات` )\n- ( `.مطر` )\n- ( `.تفريغ` )\n- ( `.فليم` )\n- ( `.احبك` )\n- ( `.طائره` )\n- ( `.شرطه` )\n- ( `.النضام الشمسي` )\n\nتحذير : لا تكثر من استخدام هذه الاوامر لانها قد تسبب ضغط على حسابك او تعليقه من ارسال الرسائل لفترة وجيزة.\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="تسلية 4$")
async def fun4_commands(event):
    await event.edit(
        "قائمة اوامر التسلية 4 :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.قاتل` )\n- ( `.عين` )\n- ( `.افكرر` )\n- ( `.افعى` )\n- ( `.رجل` )\n- ( `.مايكرو` )\n- ( `.فايروس` )\n- ( `.قطار` )\n- ( `.نيكول` )\n- ( `.موسيقى` )\n- ( `.رسم` )\n\nتحذير : لا تكثر من استخدام هذه الاوامر لانها قد تسبب ضغط على حسابك او تعليقه من ارسال الرسائل لفترة وجيزة.\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="تسلية 5$")
async def fun5_commands(event):
    await event.edit(
        "قائمة اوامر التسلية 5 :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.تحميل` )\n- ( `.مربع` )\n- ( `.دائره` )\n- ( `.انيم` )\n- ( `.بشره` )\n- ( `.قرد` )\n- ( `.يد` )\n- ( `.العد التنازلي` )\n- ( `.قلوب` )\n\nتحذير : لا تكثر من استخدام هذه الاوامر لانها قد تسبب ضغط على حسابك او تعليقه من ارسال الرسائل لفترة وجيزة.\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="تسلية 6$")
async def fun6_commands(event):
    await event.edit(
        "قائمة اوامر التسلية 6 :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.ترامب` + النص )\n- ( `.مودي` + النص )\n- ( `.بنر` + النص )\n- ( `.كانا` + النص )\n- ( `.تويت` + المعرف ; النص )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="تسلية 7$")
async def fun7_commands(event):
    await event.edit(
        "قائمة اوامر التسلية 7 :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.تراش` بالرد على ملصق/صورة )\n- ( `.تهديد` بالرد على ملصق/صورة )\n- ( `.فخ` بالرد على ملصق/صورة + الاسم1 ; الاسم2 )\n- ( `.بورن` بالرد على ملصق/صورة + المعرف ; النص )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="تسلية 8$")
async def fun8_commands(event):
    await event.edit(
        "قائمة اوامر التسلية 8 :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.نص` + النص )\n- ( `.ستيكر` + النص )\n- ( `.هونك` + النص )\n- ( `.تغريد` + النص )\n- ( `.غلاكس` + النص )\n- ( `.دوغي` + النص )\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الملصقات$")
async def sticker_commands(event):
    await event.edit(
        "شرح عن أوامر الملصقات\n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر\n\n- ( `.ملصق` )\nبالرد على الملصق لأخذه و عمل حزمه خاصة بك و اضافته بها\n\n- ( `.حزمة` )\nبالرد على الملصق لنسخ الحزمة كاملة بداخل حزمة ملصقاتك الخاصة\n\n- (`.معلومات_الملصق` )\nبالرد على الملصق لعرض معلومات الحزمة\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التكرار$")
async def repeat_commands(event):
    await event.edit(
        "شرح عن أوامر التكرار\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.كرر + عدد التكرار + بالرد على الرسالة` )\n يقوم بتكرار النصوص والوسائط بالرد على الرسالة او الصورة \nمثال : ( بالرد على صورة `.كرر 10` )\n\n- ( `.تكرار الملصق + بالرد على ملصق` )\n بالرد على الملصق ليقوم باستخراج جميع ملصقات الحزمه وارسالها\n\n- (`.مكرر + وقت بالثواني + عدد + بالرد` )\n بالرد على نص او صورة او اي شي يقوم بالتكرار مع وقت معين .\nمثال : بالرد على نص ( `.مكرر 10 2` ) عندها سترسل 10 رسائل نصية ( النص الي رديت عليه ) بفاصل ثانيتين بين كل رسالة\n\n- ( `.ضع تكرار` + العدد )\nلمنع التكرار بالمجموعة الخاصة بك بالعدد الذي وضعته للعودة للوضع الطبيعي ضع 999999.\nمثال : ( `.ضع تكرار 10` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر السبام$")
async def spam_commands(event):
    await event.edit(
        "شرح عن أوامر السبام\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.سبام + كلمة` )\nيقوم بتفصيخ احرف الكلمه وارسالها جربه بنفسك\n\n- ( `.وسبام + كلمة` )\nكتابة الامر مع نص معين يقوم بتفصيخ الجمله كلمه كلمه وارسالها\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التنظيف$")
async def clean_commands(event):
    await event.edit(
        "شرح عن أوامر التنظيف\n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر\n\n- ( `.تنظيف + عدد الرسائل` )\nيقوم بحذف الرسائل اكتب الامر وعدد معين من الرسائل سيقوم بحذفها\n\n- ( `.تنظيف + الاضافة` )\n يجب وضع الشارحة مع الاضافة (-)\nمثال : ( `.تنظيف -ح` ) <سيقوم بحذف المتحركات في الدردشة>\nالاضافات : \n (-ب) : لحذف الرسائل الصوتية\n (-م): لحذف الملفات\n (-ح): لحذف المتحركة\n (-ص): لحذف الصور\n (-غ): لحذف الاغاني\n (-ق): لحذف الملصقات\n (-ر): لحذف الروابط\n (-ف): لحذف الفيديوهات\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر المسح$")
async def delete_commands(event):
    await event.edit(
        "شرح عن أوامر المسح\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.مسح + بالرد على النص` )\nفقط اكتب الامر بالرد على الرسالة ليقوم بحذفها\n\n- ( `.حذف رسائلي` )\nاكتب الامر في اي مكان وسيقوم بحذف جميع رسائلك في الدردشه حتى لو لم يكن لديك صلاحيات\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الوقت والتاريخ$")
async def time_commands(event):
    await event.edit(
        "شرح اوامر الوقت والتاريخ :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.تاريخ` )\nبالرد على الشخص او كتابة معرفه مع الامر لعرض سجل اسماء حسابه.\n\n- ( `.الوقت` )\nلعرض الوقت على شكل ملصق\n\n- ( `.وقت` )\nلعرض الوقت على شكل كتابة\n\n- ( `.مؤقت` + الوقت + النص )\nيقوم بإرسال رسالة مؤقتة و حذفها بعد وقت معين\n- مثال : `.مؤقت 5 سورس عبود`\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر كورونا$")
async def corona_commands(event):
    await event.edit(
        "شرح اوامر كورونا :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر\n\n- ( `.كورونا` + الدولة )\nللحصول على احصائيات فايروس كورونا\n- مثال : `.كورونا Morocco`\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الصلاة$")
async def prayer_commands(event):
    await event.edit(
        "شرح اوامر الصلاة :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.صلاة` )\nاكتب الامر مع اسم محافظتك باللغه الانكليزية للحصول على اوقات الصلاة\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر مساعدة$")
async def help_commands(event):
    await event.edit(
        "شرح اوامر المساعدة :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.موقع` + المكان )\nللحصول على مكان في الخريطه و ارساله لك\n\n- ( `.صورة` )\nبالرد على الشخص للحصول على صورة حسابه الشخصية.\n\n- ( `.صوره كلها` )\nللرد على الشخص للحصول على صور حسابه الشخصية كلها.\n\n- ( `.سرعة الانترنت` )\nارسل الامر لقياس سرعة الانترنت\n\n- ( `.حساب` )\nكتابة الامر مع معادلة رياضية و سيقوم بحلها و ارسالها لك\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="فارغ $")
async def empty_commands(event):
    await event.edit(
        "شرح اوامر :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.معلومات` )\nارسل الامر في المجموعة لرؤية معلومات المجموعة او اكتب الامر مع معرف المجموعة\n\n- ( `.البوتات` )\nارسل الامر في المجموعة لرؤية البوتات الموجودة في المجموعة او اكتب الامر مع معرف المجموعة\n\n- ( `.المشرفين` )\nارسل الامر في المجموعة لرؤية مشرفين المجموعة او اكتب الامر مع معرف المجموعة\n\n- ( `.الاعضاء` )\nارسل الامر في المجموعة لرؤية اعضاء المجموعة او اكتب الامر مع معرف المجموعة\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الروابط$")
async def link_commands(event):
    await event.edit(
        "شرح اوامر الروابط :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.دنس` + الرابط )\nلكشف نظام دومين موقع معين اكتب الامر مع الرابط\n\n- ( `.مصغر` )\nبالرد على الرابط او وضع الرابط مع الامر ليقوم بتصغيره\n\n- ( `.رابط_مخفي` )\nبالرد على الرابط لاخفاء الرابط و جعله في مسافه معينة جرب الامر بنفسك\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التحذيرات$")
async def warn_commands(event):
    await event.edit(
        "شرح اوامر التحذيرات :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.تحذير + السبب` )\nبالرد على الشخص ليقوم بتحذيره يمكنك وضع سبب كذلك\n\n- ( `.التحذيرات` )\nبالرد على الشخص ليقوم باظهار تحذيراته.\n\n- ( `.حذف التحذيرات` )\nبالرد على الشخص لحذف تحذيراته.\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر اللستة$")
async def list_commands(event):
    await event.edit(
        "شرح اوامر اللستة :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.لستة` )\nيقوم بصنع لستة شفافة لمنشور معين\nشرح الامر : \n https://t.me/SSSTlF\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الملكية$")
async def ownership_commands(event):
    await event.edit(
        "شرح اوامر الملكية :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.ملكية` )\nيقوم بكتابة التمر في القناة التي تريد تحويلها لشخص و بكتابة الامر مع معرف الشخص\n\nلاستخدام امر نقل الملكية تحتاج لوضع TG_2STEP_VERIFICATION_CODE و معه رمز حسابك في الفارات\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر السليب$")
async def sleep_commands(event):
    await event.edit(
        "شرح اوامر السليب :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.سليب` + السبب)\nيقوم بادخالك في وضع غير المتصل يقوم بالرد على اي شخص برسالة يقول فيها انك غير متواجد.\n- مثال : `.سليب نايم`\n\n- ( `.سليب_ميديا` + السبب )\nيقوم بنفس وظيفة الامر العادي غير انه يمكنك ارفاق صورة او متحركة بالرد عليها مع الامر.\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الاسم$")
async def name_commands(event):
    await event.edit(
        "شرح اوامر الاسم الوقتي :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.اسم وقتي` )\nبكتابة الامر لاضافة اسم وقتي حسب منطقة التي وضعتها .\n\n- ( `.ايقاف اسم وقتي` )\nلانهاء الاسم الوقتي و ارجاع الاسم الطبيعي .\n\n- ( `.صوره وقتيه` )\nلوضع صورة تتغير مع الوقت\n\n- ( `.ايقاف صوره وقتيه` )\nلانهاء الصورة واسترجاع الصورة الاصلية\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر البايو$")
async def bio_commands(event):
    await event.edit(
        "شرح اوامر البايو الوقتي :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.بايو وقتي` )\nبكتابة الامر لاضافة بايو وقتي حسب منطقة التي وضعتها .\n\n- ( `.ايقاف بايو وقتي` )\nلانهاء البايو الوقتي و ارجاع البايو الطبيعي .\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التشغيل$")
async def run_commands(event):
    await event.edit(
        "شرح اوامر التشغيل :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.اعادة تشغيل` )\nلاعادة تشغيل البوت و ارجاعة الى شكله الطبيعي كما كان في الاول فقط ارسل الامر .\n\n- ( `.تحديث` )\nفقط ارسل الامر للتاكد اذا كان هناك تحديثات من مطورين السورس .\n\n- ( `.التحديثات تشغيل` )\nيستخدم هذا الامر لارسال رسالة تجريبية تلقائية لرؤية البوت اذا ما كان شغال بعد اعادة التشغيل او التحديث سيرس امر `.بنك` ولايقافه ارسل `.التحديثات ايقاف` .\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الاطفاء$")
async def shutdown_commands(event):
    await event.edit(
        "شرح اوامر الاطفاء :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.اطفاء` )\nلالغاء تشغيل البوت و يجب اعادة تشغيله من هيروكو .\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الكشف$")
async def info_commands(event):
    await event.edit(
        "شرح اوامر الكشف :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.ايدي` )\nبالرد على الشخص او كتابة معرفه مع الامر لعرض معلوماته.\n\n- ( `.ايدي` )\nبالرد على الشخص لعرض معلوماته\n\n- ( `.كشف` )\nبالرد على الشخص لعرض معلوماته بشكل مبسط\n\n- ( `.رابط الحساب` )\nبالرد على الشخص للحصول على رابط حساب الشخص\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر كوكل$")
async def google_commands(event):
    await event.edit(
        "شرح اوامر كوكل :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.صور + عدد الصور + نص` )\nللحصول على صور من متصفح كوكل بكتابة الامر وعدد الصور الحد 10 واسم النص\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الاذاعه$")
async def broadcast_commands(event):
    await event.edit(
        "شرح اوامر التوجيه والاذاعة :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.وجه + نص` )\nلعمل اذاعة للنص في المجموعات اكتب الامر ونصك\n\n- ( `.حول + نص` )\nلعمل اذاعة للنص للدردشات الخاصة اكتب الامر ونصك\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="امر الصورة الذاتية$")
async def selfpic_commands(event):
    await event.edit(
        "شرح امر الصورة الذاتية :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.ذاتيه` )\n بالرد على الصورة الذاتية التدمير ليقوم بحفظها وارسالها لك في الرسائل المحفوظة بسرية وبدون علم الطرف الآخر\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التسلية$")
async def all_fun_commands(event):
    await event.edit(
        "قائمة اوامر التسلية :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n- ( `.تسلية 1` )\n- ( `.تسلية 2` )\n- ( `.تسلية 3` )\n- ( `.تسلية 4` )\n- ( `.تسلية 5` )\n- ( `.تسلية 6` )\n- ( `.تسلية 7` )\n- ( `.تسلية 8` )\n- ( `.فيك typing 300` )\n- ( `.رفع ادمن` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التحشيش$")
async def joke_commands(event):
    await event.edit(
        "قائمة اوامر التحشيش :\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه القوائم\n\n**جميع اوامر التحشيش تستخدم بالرد على الشخص**\n\n- ( `.رفع تاج` )\n- ( `.رفع بكلبي` )\n- ( `.رفع مطي` )\n- ( `.رفع جلب` )\n- ( `.رفع قرد` )\n- ( `.رفع مرتي` )\n- ( `.رفع زوجي` )\n- ( `.نسبة الانوثة` )\n- ( `.نسبة الحب` )\n- ( `.نسبة الغباء` )\n- ( `.رفع زاحف` )\n- ( `.رفع كحبة` )\n- ( `.رفع فرخ` )\n- ( `.رزله` )\n- ( `.رفع صاك` )\n- ( `.رفع حاته` )\n- ( `.رفع بقره` )\n- ( `.رفع ايجة` )\n- ( `.رفع زبال` )\n- ( `.رفع كواد` )\n- ( `.رفع ديوث` )\n- ( `.رفع مجنب` )\n- ( `.رفع مميز` )\n- ( `.رفع ادمن` )\n- ( `.رفع منشئ` )\n- ( `.رفع مالك` )\n- ( `.رفع وصخ` )\n- ( `.نسبة الكذب` )\n- ( `.نسبة الدياثه` )\n- ( `.نسبة الشذوذ` )\n- ( `.نسبة الجمال` )\n- ( `.نسبة الخيانه` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر التحويل$")
async def convert_commands(event):
    await event.edit(
        "شرح عن أوامر تحويل الصيغ :\n➖➖➖➖➖➖➖➖➖➖➖➖\n ⌯︙اختر احدى هذه الاوامر\n\n- ( `.تحويل صورة` )\n بالرد على الملصق لتحويله الى صورة\n\n- ( `.تحويل ملصق` )\n بالرد على الصورة لتحويلها الى الملصق\n\n- ( `.تحويل voice` )\nبالرد على مقطع اغنية لتحويله على شكل بصمة صوتية\n\n- ( `.تحويل mp3` )\nبالرد على البصمة الصوتية لتحويلها على شكل مقطع mp3\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الجهات$")
async def add_commands(event):
    await event.edit(
        "قائمة اوامر الجهات والاضافة\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.ضيف + رابط مجموعة` )\n يستخدم الامر لاخذ اعضاء من مجموعة ثانية واضافتهم في مجموعتك ترسل الامر مع رابط قروب عام في مجموعتك للاضافة\n مثال : .ضيف https://t.me/SSSTlF\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الحساب$")
async def account_commands(event):
    await event.edit(
        "قائمة اوامر الحساب والقنوات والمجموعات التي تديرها\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.معلوماتي` )\n- ( `.قائمه قنواتي` )\n- ( `.قائمه كروباتي` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الالعاب$")
async def game_commands(event):
    await event.edit(
        "قائمة اوامر الالعاب\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.بلي` )\n- ( `.كت` )\n- ( `.خيروك` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="بصمات ميمز$")
async def meme1_commands(event):
    await event.edit(
        "قائمة بصمات الميمز\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.تخوني` )\n- ( `.مستمرة الكلاوات` )\n- ( `.احب العراق` )\n- ( `.احبك` )\n- ( `.اخت التنيج` )\n- ( `.اذا اكمشك` )\n- ( `.اسكت` )\n- ( `.افتهمنا` )\n- ( `.اكل خرا` )\n- ( `.العراق` )\n- ( `.الكعده وياكم` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="بصمات ميمز2$")
async def meme2_commands(event):
    await event.edit(
        "قائمة بصمات الميمز\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.الكمر اني` )\n- ( `.اللهم لا شماته` )\n- ( `.اني مااكدر` )\n- ( `.بقولك ايه` )\n- ( `.تف على شرفك` )\n- ( `.شجلبت` )\n- ( `.شكد شفت ناس` )\n- ( `.صباح القنادر` )\n- ( `.ضحكة فيطية` )\n- ( `.طار القلب` )\n- ( `.غطيلي` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="بصمات ميمز3$")
async def meme3_commands(event):
    await event.edit(
        "قائمة اوامر بصمات الميمز\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.في منتصف الجبهة` )\n- ( `.لاتقتل المتعه` )\n- ( `.لا لتغلط` )\n- ( `.لا يمه لا` )\n- ( `.لحد يحجي وياي` )\n- ( `.ماادري يعني` )\n- ( `.منو انت` )\n- ( `.مو صوجكم` )\n- ( `.خوش تسولف` )\n- ( `.يع` )\n- ( `.زيج` )\n- ( `.زيج2` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="بصمات ميمز4$")
async def meme4_commands(event):
    await event.edit(
        "قائمة اوامر بصمات الميمز\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.يعني مااعرف` )\n- ( `.يامرحبا` )\n- ( `.منو انتة` )\n- ( `.ماتستحي` )\n- ( `.كعدت الديوث` )\n- ( `.عيب` )\n- ( `.عنعانم` )\n- ( `.طبك مرض` )\n- ( `.سييي` )\n- ( `.سبيدر مان` )\n- ( `.خاف حرام` )\n- ( `.تحيه لاختك` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="بصمات ميمز5$")
async def meme5_commands(event):
    await event.edit(
        "قائمة اوامر بصمات الميمز\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.امشي كحبة` )\n- ( `.امداك` )\n- ( `.الحس` )\n- ( `.افتهمنا` )\n- ( `.اطلع برا` )\n- ( `.اخت التنيج` )\n- ( `.اوني تشان` )\n- ( `.اوني تشان2` )\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="م21")
async def var_commands(event):
    await event.edit(
        "قائمة اوامر الفارات\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.وضع توقيت` )\n-بالرد على المنطقة الزمنية\n- ( `.وضع رمز الاسم` )\n- بالرد على الرمز المراد وضعه\n- ( `.وضع البايو` )\n- بالرد على النبذا المراد وضعها\n- ( `.وضع الصورة` )\n- بالرد على الصورة المراد وضعها وكتابة الامر\n- ( `.وضع زخرفة الارقام` )\n- بالرد على الارقام المراد وضعها وكتابة الامر\n- ( `.وضع اسم` )\n- بالرد على الاسم المراد وضعه وكتابة الامر\n- ( `.وضع كروب التخزين` )\n- بالرد على الايدي المحادثة المراد جعلها كروب التخزين\n- ( `.وضع كروب الحفظ` )\n-بالرد على الايدي المحادثة المراد جعلها كروب الحفظ\n- ( `.وقت العراق` )\n- لوضع الساعة بتوقيت العراق\n- ( `.وقت السعودية` )\n- لوضع الساعة بتوقيت السعودية\n- ( `.وقت مصر` )\n-لوضع الساعة بتوقيت مصر\n- ( `.وقت الاردن` )\n- لوضع الساعة بتوقيت الاردن\n- ( `.وقت اليمن` )\n- لوضع الساعة بتوقيت اليمن\n- ( `.وقت سوريا` )\n- لوضع الساعة بتوقيت سوريا\n- تنويه : عندما تريد حذف الفار استعمل الامر (ازالة) بدل كلمة (وضع)\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

@jmthon.ar_cmd(pattern="اوامر الوهمي")
async def fake_commands(event):
    await event.edit(
        "قائمة اوامر الوهمي\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙اختر احدى هذه الاوامر\n\n- ( `.كتابة` )\n- مثال : .كتابة + عدد الثواني\n- ( `.صوتية` )\n- مثال : .صوتية + عدد الثواني\n- ( `.فيد` )\n- مثال : .فيد + عدد الثواني\n- ( `.لعبة` )\n- مثال : .لعبة + عدد الثواني\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n⌯︙CH : @SSSTlF"
    )

# =====================================================================
#                        أَمْرُ الْأَوَامِرِ (قائمة الأوامر الرئيسية)
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.الاوامر$'))
async def show_commands(event):
    if not await is_owner(event):
        return
    commands_text = """
✧ **قائمة الأوامر الرئيسية** ✧

**📥 أوامر التنصيب:**
◙ `.تنصيب` - تنصيب البوت بالرقم والرمز
◙ `.تنصيب جلسة` - تنصيب البوت بالجلسة المستخرجة
◙ `.تنصيب مصنع` - تنصيب حساب جديد كنسخة من السورس

**🛡️ أوامر الحماية:**
◙ `.قفل <نوع>` - قفل خاصية
◙ `.فتح <نوع>` - فتح خاصية
◙ `.الحاله` - عرض حالة الحماية
◙ `.البوتات` - كشف البوتات
◙ `.البوتات طرد` - طرد جميع البوتات

**👥 أوامر المجموعة:**
◙ `.تفليش` - حظر جميع الأعضاء
◙ `.تصفير` - طرد جميع الأعضاء
◙ `.الاعضاء` - عرض قائمة جميع الأعضاء
◙ `.المشرفين` - عرض قائمة المشرفين
◙ `.المعلومات` - عرض معلومات المجموعة
◙ `.المحذوفين` - عرض الحسابات المحذوفة
◙ `.المحذوفين تنظيف` - حظر الحسابات المحذوفة
◙ `.مسح المحظورين` - مسح جميع المحظورين
◙ `.غادر` - مغادرة المجموعة
◙ `.تاك <نص>` - تاك جميع الأعضاء مع نص

**👑 أوامر المشرفين:**
◙ `.رفع مشرف` - رفع شخص مشرف
◙ `.رفع مالك` - رفع شخص مشرف بكل الصلاحيات
◙ `.اخفاء` - رفع مشرف مع إخفاء الهوية
◙ `.تنزيل مشرف` - تنزيل مشرف
◙ `.حظر` - حظر شخص
◙ `.الغاء حظر` - الغاء حظر شخص
◙ `.كتم` - كتم شخص
◙ `.الغاء كتم` - الغاء كتم شخص
◙ `.طرد` - طرد شخص

**📥 أوامر التحميل:**
◙ `.تحميل صوتي <رابط>` - تحميل صوت من رابط
◙ `.تحميل فيد <رابط>` - تحميل فيديو من رابط
◙ `.صوتي <عنوان>` - تحميل صوت بالبحث

**📋 أوامر المعلومات:**
◙ `.ا` - عرض معلومات حسابك
◙ `.ايدي` - عرض معلومات الشخص مع الصورة
◙ `.ايديي` - عرض ايديك فقط
◙ `.اسمي` - عرض اسمك
◙ `.كشف` - معلومات مفصلة عن الشخص
◙ `.id` - عرض الايدي فقط
◙ `.stat` - عرض إحصائيات الحساب
◙ `.رابط الحساب` - إنشاء رابط لحساب الشخص

**🔍 أوامر البحث:**
◙ `.بحث <نص>` - البحث في جوجل
◙ `.فيديو <اسم>` - البحث عن فيديو
◙ `.اغنية <اسم>` - البحث عن أغنية

**⏰ أوامر الوقت:**
◙ `.تفعيل الوقت` - تفعيل عرض الوقت في الاسم
◙ `.تعطيل الوقت` - تعطيل عرض الوقت
◙ `.صوره وقتيه` - تفعيل الصورة الوقتية
◙ `.اسم وقتي` - تفعيل الاسم الوقتي
◙ `.بايو وقتي` - تفعيل البايو الوقتي
◙ `.ايقاف صوره وقتيه` - إيقاف الصورة الوقتية
◙ `.ايقاف اسم وقتي` - إيقاف الاسم الوقتي
◙ `.ايقاف بايو وقتي` - إيقاف البايو الوقتي

**🎯 أوامر الصيد:**
◙ `.الصيد` - شرح أوامر الصيد
◙ `.صيد <نوع>` - صيد معرفات عشوائية
◙ `.تثبيت معرف <معرف>` - تثبيت على معرف
◙ `.ايقاف الصيد` - إيقاف الصيد
◙ `.ايقاف التثبيت` - إيقاف التثبيت
◙ `.حالة الصيد` - عدد محاولات الصيد
◙ `.حالة التثبيت` - عدد محاولات التثبيت

**📸 أوامر الذاتية:**
◙ `.الذاتيه` - شرح أوامر الذاتية
◙ `.تفعيل الذاتيه` - تفعيل حفظ الذاتية التلقائي
◙ `.تعطيل الذاتيه` - تعطيل حفظ الذاتية التلقائي
◙ `.ذاتيه` - حفظ صورة ذاتية بالرد

**📢 أوامر الإعلان:**
◙ `.اعلان <وقت> <رسالة>` - إعلان مؤقت
◙ `.إعلان <وقت> <رسالة>` - إعلان مؤقت مع تحذير

**🔎 أمر الكاشف:**
◙ `.الكاشف` - شرح أمر الكاشف
◙ `.كاشف <دولة> <رقم>` - كشف معلومات الرقم

**🎭 أوامر التسلية:**
◙ `.كت` - عرض حكمة عشوائية
◙ `.نسبه الحب <اسم1, اسم2>` - نسبة الحب بين شخصين

**📖 أوامر أخرى:**
◙ `.تنصيب` - تنصيب البوت تلقائياً
◙ `.مساعده` - عرض المساعدة

**🔄 أوامر التكرار:**
◙ `.سبام <عدد> <رسالة>` - تكرار إرسال رسالة (الحد الأقصى 99)
◙ `.مكرر <وقت> <عدد> <رسالة>` - تكرار إرسال رسالة بفاصل زمني
◙ `.فصخ <جملة>` - تفصيخ الجملة حرفاً حرفاً
◙ `.ايقاف مكرر` - إيقاف أمر المكرر

✧ **سورس عبود** ✧
"""
    await event.reply(commands_text)

@client.on(events.NewMessage(pattern=r'^\.مساعده$'))
async def help_command(event):
    if not await is_owner(event):
        return
    help_text = """
✧ **قائمة المساعدة السريعة** ✧

**📥 التنصيب:**
◙ `.تنصيب` - تنصيب البوت بالرقم والرمز
◙ `.تنصيب جلسة` - تنصيب البوت بالجلسة المستخرجة
◙ `.تنصيب مصنع` - تنصيب حساب جديد كنسخة من السورس

**📖 الأوامر الرئيسية:**
◙ `.الاوامر` - عرض جميع الأوامر
◙ `.ا` - معلومات حسابك
◙ `.تفعيل الوقت` - تفعيل عرض الوقت
◙ `.كت` - حكمة عشوائية
◙ `.بحث` - بحث في جوجل

**🛡️ الحماية:**
◙ `.الحاله` - عرض حالة الحماية
◙ `.قفل` - قفل خاصية
◙ `.فتح` - فتح خاصية

**👑 المشرفين:**
◙ `.رفع مشرف` - رفع مشرف
◙ `.حظر` - حظر شخص
◙ `.كتم` - كتم شخص
◙ `.طرد` - طرد شخص

**🔄 التكرار:**
◙ `.سبام <عدد> <رسالة>` - تكرار إرسال رسالة
◙ `.مكرر <وقت> <عدد> <رسالة>` - تكرار إرسال رسالة بفاصل زمني
◙ `.فصخ <جملة>` - تفصيخ الجملة
◙ `.ايقاف مكرر` - إيقاف أمر المكرر

✧ **سورس عبود** ✧
"""
    await event.reply(help_text)

# =====================================================================
#                        أَوَامِرُ التَّنْصِيبِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.تنصيب جلسة$'))
async def install_session_command(event):
    await event.reply("""
📥 **أرسل جلسة تيليجرام المستخرجة**

📌 اكتب الجلسة في رسالة جديدة
⚠️ تأكد من نسخها كاملة

✧ **سورس عبود** ✧
""")
    global waiting_for_session, session_user_id
    waiting_for_session = True
    session_user_id = event.sender_id

@client.on(events.NewMessage(incoming=True))
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
✅ **تم التنصيب بنجاح!**

👤 الحساب: {me.first_name}
🆔 الايدي: `{me.id}`
🔄 جاري إعادة التشغيل...

✧ **سورس عبود** ✧
""")
    waiting_for_session = False
    try:
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
    except:
        await event.reply("⚠️ أعد تشغيل البوت يدوياً")

@client.on(events.NewMessage(pattern=r'^\.تنصيب$'))
async def install_bot(event):
    global install_waiting, install_user_id, install_step, install_client
    if install_client:
        try:
            await install_client.disconnect()
        except:
            pass
    install_waiting = True
    install_user_id = event.sender_id
    install_step = "phone"
    install_client = None
    await event.reply("""
📥 **أمر التنصيب التلقائي**

📌 **الخطوات:**
1️⃣ أرسل رقم هاتفك مع مفتاح الدولة (مثال: +9665XXXXXXXX)
2️⃣ انتظر رمز التحقق من تيليجرام
3️⃣ أرسل الرمز المكون من 5 أرقام هنا
4️⃣ إذا كان الحساب مفعل بخطوتين، أرسل كلمة المرور

💡 **بديل:** استخدم `.تنصيب جلسة` إذا كنت تملك جلسة مستخرجة

✧ **سورس عبود** ✧
""")

@client.on(events.NewMessage(incoming=True))
async def handle_install_input(event):
    global install_waiting, install_user_id, install_phone, install_client, install_step, install_hash
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
📱 تم استقبال الرقم: `{phone}`

⏳ جاري إرسال رمز التحقق...
📩 أرسل الرمز الذي وصل إلى تيليجرام

✧ **سورس عبود** ✧
""")
                install_step = "code"
            except PhoneNumberInvalidError:
                await event.reply("❌ رقم الهاتف غير صحيح! تأكد من كتابته مع مفتاح الدولة\nمثال: +9665XXXXXXXX")
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
✅ **تم التنصيب بنجاح!**

📋 المعرف: `{me_new.id}`
📛 الاسم: {me_new.first_name}
🆔 اليوزر: @{me_new.username if me_new.username else 'لا يوجد'}

🔄 جاري إعادة التشغيل...

✧ **سورس عبود** ✧
""")
                await install_client.disconnect()
                install_client = None
                install_waiting = False
                subprocess.Popen([sys.executable, __file__])
                sys.exit(0)
            except SessionPasswordNeededError:
                await event.reply("""
🔐 **مطلوب كلمة مرور الخطوتين!**

📌 أرسل الآن كلمة المرور الخاصة بحسابك

✧ **سورس عبود** ✧
""")
                install_step = "password"
            except PhoneCodeInvalidError:
                await event.reply("❌ رمز التحقق غير صحيح! أعد المحاولة")
            except FloodWaitError as e:
                await event.reply(f"⏳ انتظر {e.seconds} ثانية قبل المحاولة مرة أخرى")
            except Exception as e:
                await event.reply(f"❌ خطأ: {str(e)}\n\n📌 أعد المحاولة بـ `.تنصيب`")
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
✅ **تم التنصيب بنجاح!**

📋 المعرف: `{me_new.id}`
📛 الاسم: {me_new.first_name}
🆔 اليوزر: @{me_new.username if me_new.username else 'لا يوجد'}

🔄 جاري إعادة التشغيل...

✧ **سورس عبود** ✧
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
        await event.reply(f"❌ خطأ عام: {str(e)}\n\n📌 أعد المحاولة بـ `.تنصيب`")
        install_waiting = False
        install_step = "phone"
        if install_client:
            await install_client.disconnect()
            install_client = None

@client.on(events.NewMessage(pattern=r'^\.تنصيب مصنع$'))
async def factory_install_command(event):
    global factory_active, factory_user_id, factory_step
    factory_active = True
    factory_user_id = event.sender_id
    factory_step = "waiting"
    await event.reply("""
🏭 **مصنع تنصيب الحسابات**

📥 أرسل جلسة تليثون مستخرجة جاهزة
⚠️ تأكد من نسخها كاملة

✧ **سورس عبود** ✧
""")

@client.on(events.NewMessage(incoming=True))
async def factory_session_handler(event):
    global factory_active, factory_user_id, factory_step
    if not factory_active:
        return
    if event.sender_id != factory_user_id:
        return
    if event.text.startswith('.'):
        return
    if factory_step != "waiting":
        return
    session_str = event.text.strip()
    await event.reply("📥 **جاري استقبال الجلسة...**")
    if len(session_str) < 20:
        await event.reply("❌ الجلسة غير صالحة! تأكد من نسخها كاملة")
        factory_active = False
        return
    factory_step = "processing"
    try:
        await event.reply("🔄 **جاري التحقق من صحة الجلسة...**")
        temp_client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await temp_client.connect()
        me = await temp_client.get_me()
        await temp_client.disconnect()
        await event.reply(f"✅ **الجلسة صالحة!**\n👤 الحساب: {me.first_name}\n🆔 الايدي: `{me.id}`")
    except Exception as e:
        await event.reply(f"❌ **الجلسة غير صالحة:**\n{str(e)}")
        factory_active = False
        return
    account_id = me.id
    source_file = f"sorcer_{account_id}.py"
    runner_file = f"run_{account_id}.py"
    try:
        await event.reply("📝 **جاري إنشاء ملفات الحساب الجديد...**")
        with open(__file__, 'r', encoding='utf-8') as f:
            source_code = f.read()
        modified_code = source_code.replace(
            'SESSION = os.environ.get("SESSION_STRING", CONFIG.get("session_string", ""))',
            f'SESSION = "{session_str}"'
        )
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(modified_code)
        runner_script = f'''# -*- coding: utf-8 -*-
import os
import sys
import subprocess

if __name__ == "__main__":
    print("🚀 جاري تشغيل الحساب الجديد...")
    try:
        subprocess.Popen([sys.executable, "{source_file}"])
        print("✅ تم تشغيل الحساب بنجاح!")
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {{e}}")
'''
        with open(runner_file, 'w', encoding='utf-8') as f:
            f.write(runner_script)
    except Exception as e:
        await event.reply(f"❌ **خطأ في إنشاء الملفات:**\n{str(e)}")
        factory_active = False
        return
    await event.reply(f"""
✅ **تم تنصيب الحساب بنجاح!**

━━━━━━━━━━━━━━━━
👤 **الحساب:** {me.first_name}
🆔 **الايدي:** `{account_id}`
📁 **ملف السورس:** `{source_file}`
🚀 **ملف التشغيل:** `{runner_file}`
━━━━━━━━━━━━━━━━

🔄 **لتشغيل الحساب استخدم:**
`python {runner_file}`

✧ **سورس عبود** ✧
""")
    try:
        subprocess.Popen([sys.executable, runner_file])
        await event.reply("✅ **تم تشغيل الحساب الجديد بنجاح!**")
    except Exception as e:
        await event.reply(f"⚠️ **تم التنصيب لكن فشل التشغيل التلقائي:**\n{str(e)}")
    factory_active = False
    factory_step = "done"

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
    await event.reply(f"🎵 جاري البحث عن: **{query}**...")
    await search_and_download_audio(event, query)

# =====================================================================
#                        أَوَامِرُ الْحِمَايَةِ (PROTECTION)
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
        await event.reply(f"✅ تم قفل `{lock_type}`")
    else:
        await event.reply(f"❌ نوع القفل `{lock_type}` غير معروف")

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
        await event.reply(f"✅ تم فتح `{lock_type}`")
    else:
        await event.reply(f"❌ نوع القفل `{lock_type}` غير معروف")

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
    text = "✧ **حالة الحماية في هذه الدردشة** ✧\n\n"
    for name, status in locks_status.items():
        icon = "🔒" if status else "🔓"
        text += f"{icon} `{name}` : {'مقفل' if status else 'مفتوح'}\n"
    text += "\n✧ **سورس عبود** ✧"
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
                bots.append(f"• {user.first_name} (`{user.id}`)")
        if bots:
            text = f"🤖 **تم العثور على {len(bots)} بوت:**\n\n" + "\n".join(bots)
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
    mentions = "✧ **قائمة الأعضاء** ✧\n\n"
    count = 0
    async for user in client.iter_participants(event.chat_id):
        count += 1
        if user.deleted:
            mentions += f"• حساب محذوف (`{user.id}`)\n"
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
    mentions = "✧ **قائمة المشرفين** ✧\n\n"
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
✧ **معلومات المجموعة** ✧

📛 الاسم: {chat.title}
🆔 الايدي: `{event.chat_id}`
👥 الأعضاء: {full_chat.full_chat.participants_count}
🛡️ المشرفين: {full_chat.full_chat.admins_count if hasattr(full_chat.full_chat, 'admins_count') else 'غير معروف'}
🚫 المحظورين: {full_chat.full_chat.kicked_count if hasattr(full_chat.full_chat, 'kicked_count') else 'غير معروف'}
📝 الوصف: {full_chat.full_chat.about if full_chat.full_chat.about else 'لا يوجد'}

✧ **سورس عبود** ✧
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
        text = f"⚠️ **تم العثور على {len(deleted)} حساب محذوف:**\n\n"
        for idx, user_id in enumerate(deleted[:20], 1):
            text += f"{idx}. `{user_id}`\n"
        if len(deleted) > 20:
            text += f"\n... و {len(deleted) - 20} آخرين"
        text += f"\n\nلحظرهم استخدم: `.المحذوفين تنظيف`"
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
✧ **إحصائيات الحساب** ✧

👤 الاسم: {me.first_name}
🆔 الايدي: `{me.id}`

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

✧ **سورس عبود** ✧
"""
    await zedevent.edit(text)

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
    is_bot = replied_user.bot
    restricted = replied_user.restricted
    verified = replied_user.verified
    photo = await event.client.download_profile_photo(user_id, os.path.join("downloads", str(user_id) + ".jpg"), download_big=True)
    first_name = first_name.replace("\u2060", "") if first_name else "هذا المستخدم ليس له اسم أول"
    full_name = full_name or first_name
    username = f"@{username}" if username else "لايوجد معرف"
    user_bio = "لاتوجد نبذة" if not user_bio else user_bio
    rotbat = "⌁ من مطورين السورس ⌁" if user_id == 5502537272 else "⌁ العضو ⌁"
    if user_id == (await event.client.get_me()).id and user_id != 5502537272:
        rotbat = "⌁ مالك الحساب ⌁"
    caption = "✛━━━━━━━━━━━━━✛\n"
    caption += f"<b> •❃╎الاسم    ⇠ </b> {full_name}\n"
    caption += f"<b> •❃╎المعرف  ⇠ </b> {username}\n"
    caption += f"<b> •❃╎الايدي   ⇠ </b> <code>{user_id}</code>\n"
    caption += f"<b> •❃╎الرتبة  ⇠ {rotbat} </b>\n"
    caption += f"<b> •❃╎الصور   ⇠ </b> {replied_user_profile_photos_count}\n"
    caption += f"<b> •❃╎الحساب ⇠ </b> "
    caption += f'<a href="tg://user?id={user_id}">{first_name}</a>'
    caption += f"\n<b> •❃╎البايو    ⇠ </b> {user_bio} \n"
    caption += f"✛━━━━━━━━━━━━━✛"
    return photo, caption

@client.on(events.NewMessage(pattern=r'^\.ايدي(?: |$)(.*)'))
async def who(event):
    cat = await edit_or_reply(event, "⇆ جاري جلب المعلومات...")
    if not os.path.isdir("downloads"):
        os.makedirs("downloads")
    replied_user = await get_user_from_event(event)
    if not replied_user:
        return await edit_or_reply(cat, "**- لم استطع العثور على الشخص**")
    try:
        photo, caption = await fetch_info(replied_user, event)
    except AttributeError:
        return await edit_or_reply(cat, "**- لم استطع العثور على الشخص**")
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
    replied_user = await get_user_from_event(event)
    if not replied_user:
        return
    catevent = await edit_or_reply(event, "᯽︙ جاري إحضار معلومات المستخدم ⚒️")
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
        cas = "**Antispam(CAS) محظور:** `True`" if data and data.get("ok") else "**Antispam(CAS) محظور:** `False`"
    except:
        cas = "**Antispam(CAS) محظور:** `تعذر الجلب`"
    caption = f"""**معلومات المستخدم [{first_name}](tg://user?id={user_id}):**
   • الايدي: `{user_id}`
   • المجموعات المشتركة: `{common_chats}`
   • رقم قاعدة البيانات: `{dc_id}`
   • حساب موثق: `{replied_user.users[0].restricted}`
   • {cas}
"""
    await edit_or_reply(catevent, caption)

@client.on(events.NewMessage(pattern=r'^\.id(?:\s|$)(.*)'))
async def get_id_command(event):
    input_str = event.pattern_match.group(1)
    if input_str:
        try:
            p = await event.client.get_entity(input_str)
            if hasattr(p, 'first_name'):
                return await edit_or_reply(event, f"᯽︙ ايدي المستخدم `{input_str}` هو `{p.id}`")
            elif hasattr(p, 'title'):
                return await edit_or_reply(event, f"᯽︙ ايدي الدردشة/القناة `{p.title}` هو `{p.id}`")
        except Exception as e:
            return await edit_delete(event, f"`{str(e)}`", 5)
    elif event.reply_to_msg_id:
        r_msg = await event.get_reply_message()
        if r_msg.media:
            await edit_or_reply(event, f"᯽︙ ايدي الدردشه: `{str(event.chat_id)}` \n᯽︙ ايدي المستخدم: `{str(r_msg.sender_id)}`")
        else:
            await edit_or_reply(event, f"᯽︙ ايدي الدردشه: `{str(event.chat_id)}` \n᯽︙ ايدي المستخدم: `{str(r_msg.sender_id)}`")
    else:
        await edit_or_reply(event, f"᯽︙ الدردشة الحالية: `{str(event.chat_id)}`")

@client.on(events.NewMessage(pattern=r'^\.ايديي$'))
async def my_id_command(event):
    if not await is_owner(event):
        return
    me = await client.get_me()
    await event.reply(f"📋 ايديك: `{me.id}`")

@client.on(events.NewMessage(pattern=r'^\.اسمي$'))
async def my_name_command(event):
    if not await is_owner(event):
        return
    me = await client.get_me()
    await event.reply(f"📛 اسمك: {me.first_name} {me.last_name or ''}")

@client.on(events.NewMessage(pattern=r'^\.رابط الحساب(?:\s|$)([\s\S]*)'))
async def permalink(event):
    user = await get_user_from_event(event)
    if not user:
        return
    custom = event.pattern_match.group(1)
    if custom:
        return await edit_or_reply(event, f"[{custom}](tg://user?id={user.id})")
    tag = user.first_name.replace("\u2060", "") if user.first_name else user.username or "مستخدم"
    await edit_or_reply(event, f"⌔︙[{tag}](tg://user?id={user.id})")

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

✧ **سورس عبود** ✧"""
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

✧ **سورس عبود** ✧"""
        photos = await client.get_profile_photos(me)
        if photos:
            await event.reply(text, file=photos[0])
        else:
            await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

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
        await event.reply(f"🔍 جاري البحث عن: **{query}**...")
        await asyncio.sleep(1)
        text = f"""
✧ نتيجة البحث ✧

📝 البحث : {query}
✅ النتيجة : تم العثور
🔗 الرابط : [اضغط هنا](https://www.google.com/search?q={query.replace(' ', '+')})

✧ **سورس عبود** ✧"""
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
        await event.reply(f"🎬 جاري البحث عن فيديو: **{query}**...")
        await asyncio.sleep(1)
        text = f"""
✧ نتيجة الفيديو ✧

🎥 اسم الفيديو : {query}
🔗 رابط المشاهدة : [اضغط هنا](https://www.youtube.com/results?search_query={query.replace(' ', '+')})

✧ **سورس عبود** ✧"""
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
        await event.reply(f"🎵 جاري البحث عن أغنية: **{query}**...")
        await asyncio.sleep(1)
        text = f"""
✧ نتيجة الاغنية ✧

🎵 اسم الاغنية : {query}
🔗 رابط الاستماع : [اضغط هنا](https://www.youtube.com/results?search_query={query.replace(' ', '+')}+song)

✧ **سورس عبود** ✧"""
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

✧ **سورس عبود** ✧"""
        await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.نسبه الحب(?: (.+))?$'))
async def love_percent(event):
    if not await is_owner(event):
        return
    text = event.pattern_match.group(1) if event.pattern_match.group(1) else ""
    if not text:
        await event.reply("❌ اكتب اسمين مفصولين بفاصلة\nمثال: `.نسبه الحب احمد, سارة`")
        return
    names = [name.strip() for name in text.split(',')]
    if len(names) < 2:
        await event.reply("❌ اكتب اسمين مفصولين بفاصلة")
        return
    percent = random.randint(0, 100)
    heart = "❤️" * (percent // 10) + "🖤" * (10 - percent // 10)
    await event.reply(f"""
✧ **نسبة الحب** ✧

💑 {names[0]} 🤝 {names[1]}

💕 النسبة: **{percent}%**
{heart}

✧ **سورس عبود** ✧
""")

# =====================================================================
#                        أَوَامِرُ الْوَقْتِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.تفعيل الوقت$'))
async def enable_time(event):
    global time_enabled
    if not await is_owner(event):
        await event.reply("❌ هذا الأمر فقط لصاحب الحساب")
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
        await event.reply("❌ هذا الأمر فقط لصاحب الحساب")
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
        print("❌ Pillow غير مثبت - تعطيل الصورة الوقتية")
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
            print(f"❌ خطأ في الصورة الوقتية: {e}")
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
            print(f"❌ خطأ في الاسم الوقتي: {e}")
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
            print(f"❌ خطأ في البايو الوقتي: {e}")
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
#                        أَوَامِرُ الْمُشْرِفِينَ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.رفع مشرف(?:\s|$)([\s\S]*)'))
async def promote(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "**⪼ أحتاج الى صلاحيات المشرف هنا!!**")
        return
    new_rights = ChatAdminRights(add_admins=False, invite_users=True, change_info=False, ban_users=False, delete_messages=True, pin_messages=True)
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "**╮ ❐ جاري رفعه مشرف ...❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("**⪼ ليست لدي صلاحيات كافية في هذه المجموعة**")
    await zzevent.edit("**- ❝ ⌊ تم ترقيته مشرف .. بنجاح**")

@client.on(events.NewMessage(pattern=r'^\.رفع مالك(?:\s|$)([\s\S]*)'))
async def promote_full(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "**⪼ أحتاج الى صلاحيات المشرف هنا!!**")
        return
    new_rights = ChatAdminRights(add_admins=True, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True, manage_call=True)
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "**╮ ❐ جاري رفعه مشرف بكل الصلاحيات ❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("**⪼ ليست لدي صلاحيات كافية في هذه المجموعة**")
    await zzevent.edit("**- ❝ ⌊ تم ترقيته مشرف عام بكل الصلاحيات ...**")

@client.on(events.NewMessage(pattern=r'^\.اخفاء(?:\s|$)([\s\S]*)'))
async def promote_anonymous(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "**⪼ أحتاج الى صلاحيات المشرف هنا!!**")
        return
    new_rights = ChatAdminRights(add_admins=True, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True, manage_call=True, anonymous=True)
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "**╮ ❐ جاري التعديل ❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("**⪼ ليست لدي صلاحيات كافية في هذه المجموعة**")
    await zzevent.edit("**- ❝ ⌊ تم التعديل بنجاح**")

@client.on(events.NewMessage(pattern=r'^\.تنزيل مشرف(?:\s|$)([\s\S]*)'))
async def demote(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "**⪼ أحتاج الى صلاحيات المشرف هنا!!**")
        return
    user, _ = await get_user_from_event(event)
    if not user:
        return
    zzevent = await edit_or_reply(event, "**╮ ❐ جاري التنزيل ❏╰**")
    newrights = ChatAdminRights(add_admins=None, invite_users=None, change_info=None, ban_users=None, delete_messages=None, pin_messages=None)
    rank = "مشرف"
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, newrights, rank))
    except BadRequestError:
        return await zzevent.edit("**⪼ ليست لدي صلاحيات كافية في هذه المجموعة**")
    await zzevent.edit("**- ❝ ⌊ تم تنزيله من الاشراف بنجاح**")

@client.on(events.NewMessage(pattern=r'^\.حظر(?:\s|$)([\s\S]*)'))
async def _ban_person(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if user.id == event.client.uid:
        return await edit_delete(event, "**⪼ عذراً ..لا استطيع حظر نفسي**")
    if user.id == 5502537272:
        return await edit_delete(event, "**╮ ❐ دي لا يمكنني حظر احد مطورين السورس ❏╰**")
    zedevent = await edit_or_reply(event, "**╮ ❐... جاري الحظر ...❏╰**")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await zedevent.edit("**⪼ ليست لدي صلاحيات كافية في هذه المجموعة**")
    if reason:
        await zedevent.edit(f"**- المستخدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تم حظره بنجاح ☑️**\n\n**- السبب :** `{reason}`")
    else:
        await zedevent.edit(f"**- المستخدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تم حظره بنجاح ☑️**")

@client.on(events.NewMessage(pattern=r'^\.الغاء حظر(?:\s|$)([\s\S]*)'))
async def nothanos(event):
    user, _ = await get_user_from_event(event)
    if not user:
        return
    zedevent = await edit_or_reply(event, "**╮ ❐.. جاري الغاء حظره ..❏╰**")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await zedevent.edit(f"**- المستخدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تم الغاء حظره بنجاح ✓**")
    except UserIdInvalidError:
        await zedevent.edit("`Uh oh my unban logic broke!`")
    except Exception as e:
        await zedevent.edit(f"**- خطأ :**\n`{e}`")

@client.on(events.NewMessage(pattern=r'^\.كتم(?:\s|$)([\s\S]*)'))
async def startmute(event):
    if event.is_private:
        replied_user = await event.client.get_entity(event.chat_id)
        if is_muted(event.chat_id, event.chat_id):
            return await event.edit("**- ❝ ⌊هذا المستخدم مكتوم .. سابقاً**")
        if event.chat_id == client.uid:
            return await edit_delete(event, "**- لا تستطع كتم نفسي**")
        if event.chat_id == 5502537272:
            return await edit_delete(event, "**╮ ❐ دي لا يمكنني كتم احد مطورين السورس ❏╰**")
        try:
            mute_user(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"**- خطأ **\n`{e}`")
        else:
            await event.edit("**⪼ تم كتم المستخدم .. بنجاح 🔕**")
    else:
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        if not admin and not creator:
            return await edit_or_reply(event, "**⪼ أنا لست مشرف هنا ؟!!**")
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == client.uid:
            return await edit_or_reply(event, "**- عذراً .. لا استطيع كتم نفسي**")
        if user.id == 5502537272:
            return await edit_or_reply(event, "**╮ ❐ دي لا يمكنني كتم احد مطورين السورس ❏╰**")
        if is_muted(user.id, event.chat_id):
            return await edit_or_reply(event, "**عذراً .. هذا الشخص مكتوم سابقاً هنا**")
        try:
            mute_user(user.id, event.chat_id)
        except Exception as e:
            return await edit_or_reply(event, f"**- خطأ : **`{e}`")
        if reason:
            await edit_or_reply(event, f"**- المستخدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تم كتمه بنجاح ☑️**\n\n**- السبب :** {reason}")
        else:
            await edit_or_reply(event, f"**- المستخدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تم كتمه بنجاح ☑️**")

@client.on(events.NewMessage(pattern=r'^\.الغاء كتم(?:\s|$)([\s\S]*)'))
async def endmute(event):
    if event.is_private:
        replied_user = await event.client.get_entity(event.chat_id)
        if not is_muted(event.chat_id, event.chat_id):
            return await event.edit("**عذراً .. هذا الشخص غير مكتوم هنا**")
        try:
            unmute_user(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"**- خطأ **\n`{e}`")
        else:
            await event.edit("**- تم الغاء كتم الشخص هنا .. بنجاح ✓**")
    else:
        user, _ = await get_user_from_event(event)
        if not user:
            return
        try:
            if is_muted(user.id, event.chat_id):
                unmute_user(user.id, event.chat_id)
            else:
                result = await event.client.get_permissions(event.chat_id, user.id)
                if result.participant.banned_rights.send_messages:
                    await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        except AttributeError:
            return await edit_or_reply(event, "**- الشخص غير مكتوم**")
        except Exception as e:
            return await edit_or_reply(event, f"**- خطأ : **`{e}`")
        await edit_or_reply(event, f"**- المستخدم :** [{user.first_name}](tg://user?id={user.id}) \n**- تم الغاء كتمه بنجاح ☑️**")

@client.on(events.NewMessage(pattern=r'^\.طرد(?:\s|$)([\s\S]*)'))
async def kick(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if user.id == 5502537272:
        return await edit_delete(event, "**╮ ❐ دي لا يمكنني طرد احد مطورين السورس ❏╰**")
    zedevent = await edit_or_reply(event, "**╮ ❐... جاري الطرد ...❏╰**")
    try:
        await event.client.kick_participant(event.chat_id, user.id)
    except Exception as e:
        return await zedevent.edit(f"**⪼ ليست لدي صلاحيات كافية في هذه المجموعة**\n{e}")
    if reason:
        await zedevent.edit(f"**- تم طرد** [{user.first_name}](tg://user?id={user.id})  **بنجاح ✓**\n\n**- السبب :** {reason}")
    else:
        await zedevent.edit(f"**- تم طرد** [{user.first_name}](tg://user?id={user.id})  **بنجاح ✓**")

# =====================================================================
#                        أَمْرُ الْأَحْدَاثِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.الاحداث( م)?(?: |$)(\d*)?$'))
async def _iundlt(event):
    zedevent = await edit_or_reply(event, "**- جاري البحث عن آخر الاحداث انتظر ...🔍**")
    flag = event.pattern_match.group(1)
    lim = int(event.pattern_match.group(2)) if event.pattern_match.group(2) else 5
    lim = min(lim, 15) if lim > 0 else 1
    adminlog = await event.client.get_admin_log(event.chat_id, limit=lim, edit=False, delete=True)
    deleted_msg = f"**- اليك آخر {lim} رسائل محذوفة لهذا الكروب 🗑 :**"
    if not flag:
        for msg in adminlog:
            ruser = await event.client.get_entity(msg.old.from_id)
            _media_type = media_type(msg.old)
            if _media_type is None:
                deleted_msg += f"\n🖇┊{msg.old.message} \n\n**🛂┊تم ارسالها بواسطة** [{ruser.first_name}](tg://user?id={ruser.id})"
            else:
                deleted_msg += f"\n🖇┊{_media_type} \n\n**🛂┊تم ارسالها بواسطة** [{ruser.first_name}](tg://user?id={ruser.id})"
        await edit_or_reply(zedevent, deleted_msg)
    else:
        main_msg = await edit_or_reply(zedevent, deleted_msg)
        for msg in adminlog:
            ruser = await event.client.get_entity(msg.old.from_id)
            _media_type = media_type(msg.old)
            if _media_type is None:
                await main_msg.reply(f"\n🖇┊{msg.old.message} \n\n**🛂┊تم ارسالها بواسطة** [{ruser.first_name}](tg://user?id={ruser.id})")
            else:
                await main_msg.reply(f"\n🖇┊{msg.old.message} \n\n**🛂┊تم ارسالها بواسطة** [{ruser.first_name}](tg://user?id={ruser.id})", file=msg.old.media)

# =====================================================================
#                        أَمْرُ الْكَاشِفِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.الكاشف$'))
async def cmd(event):
    await edit_or_reply(event, """
سورس عبود @SSSTlF - كاشف الارقام العربية 📲

**⪼ الامر :**

⪼ `.كاشف` + اسم الدولة + الرقم بدون مفتاح الدولة

**⪼ الوصف :**
**- لجلب معلومات عن رقم هاتف معين**

**⪼ مثال :**

`.كاشف اليمن 777887798`
`.كاشف السعوديه 555542317`
`.كاشف الامارات 43171234`

**الامر يدعم الدول التالية :** 🇾🇪🇸🇦🇦🇪🇰🇼🇶🇦🇧🇭🇴🇲

**سورس عبود** @SSSTlF
""")

@client.on(events.NewMessage(pattern=r'^\.كاشف ?(.*)'))
async def phone_info(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id and not event.pattern_match.group(1):
        reply_to_id = await event.get_reply_message()
        reply_to_id = str(reply_to_id.message)
    else:
        reply_to_id = str(event.pattern_match.group(1))
    if not reply_to_id:
        return await edit_or_reply(event, "**╮ . كاشف الارقام العربية 📲.. ارسل** `.الكاشف` **للتعليمات**")
    chat = "@Zelzalybot"
    zzzzl1l = await edit_or_reply(event, "**╮•⎚ جاري الكشف عن الرقم 📲 ⌭ ...**")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(events.NewMessage(incoming=True, from_users=1194140165))
            await event.client.send_message(chat, "{}".format(input_str))
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await zzzzl1l.edit("**╮•⎚ تحقق من انك لم تقم بحظر البوت @Zelzalybot .. ثم اعيد استخدام الامر ...🤖♥️**")
            return
        if response.text.startswith("I can't find that"):
            await zzzzl1l.edit("**╮•⎚ عذراً .. لم استطع ايجاد المطلوب ☹️💔**")
        else:
            await zzzzl1l.delete()
            await event.client.send_message(event.chat_id, response.message)

# =====================================================================
#                        فِلْتَرُ الرَّسَائِلِ
# =====================================================================

@client.on(events.NewMessage(incoming=True))
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
        print(f"❌ خطأ في تحديث الاسم: {e}")

# =====================================================================
#                        أَوَامِرُ التَّكْرَارِ
# =====================================================================

spam_running = {}

@client.on(events.NewMessage(pattern=r'^\.سبام (\d+) ([\s\S]+)$'))
async def spam_command(event):
    if not await is_owner(event):
        return
    try:
        count = int(event.pattern_match.group(1))
        if count > 99:
            await event.reply("⚠️ لا يمكن السبام أكثر من 99 رسالة")
            return
        message = event.pattern_match.group(2)
        await event.delete()
        for i in range(count):
            await event.reply(message)
            await asyncio.sleep(0.5)
    except Exception as e:
        await event.reply(f"❌ خطأ في السبام: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.مكرر (\d+\.?\d*) (\d+) ([\s\S]+)$'))
async def spam_with_delay(event):
    if not await is_owner(event):
        return
    try:
        delay = float(event.pattern_match.group(1))
        count = int(event.pattern_match.group(2))
        message = event.pattern_match.group(3)
        chat_id = event.chat_id
        await event.delete()
        spam_running[chat_id] = True
        for i in range(count):
            if not spam_running.get(chat_id, False):
                break
            await event.reply(message)
            await asyncio.sleep(delay)
        if chat_id in spam_running:
            del spam_running[chat_id]
    except Exception as e:
        await event.reply(f"❌ خطأ في المكرر: {str(e)}")
        if chat_id in spam_running:
            del spam_running[chat_id]

@client.on(events.NewMessage(pattern=r'^\.ايقاف مكرر$'))
async def stop_spam(event):
    if not await is_owner(event):
        return
    chat_id = event.chat_id
    if spam_running.get(chat_id, False):
        spam_running[chat_id] = False
        await event.reply("✅ تم إيقاف المكرر بنجاح")
    else:
        await event.reply("❌ لا يوجد مكرر يعمل حالياً")

@client.on(events.NewMessage(pattern=r'^\.فصخ ([\s\S]+)$'))
async def typewriter(event):
    if not await is_owner(event):
        return
    message = event.pattern_match.group(1)
    typing_symbol = "|"
    old_text = ""
    msg = await event.reply(typing_symbol)
    await asyncio.sleep(0.2)
    try:
        for character in message:
            old_text = old_text + character
            typing_text = old_text + typing_symbol
            await msg.edit(typing_text)
            await asyncio.sleep(0.1)
            await msg.edit(old_text)
            await asyncio.sleep(0.1)
    except Exception as e:
        await msg.edit(f"❌ خطأ: {str(e)}")

# =====================================================================
#                        أَوَامِرُ الصَّيْدِ
# =====================================================================

a = "qwertyuiopassdfghjklzxcvbnm"
b = "1234567890"
e = "qwertyuiopassdfghjklzxcvbnm1234567890"
trys, trys2 = [0], [0]
isclaim = ["off"]
isauto = ["off"]

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

@client.on(events.NewMessage(pattern=r'^\.الصيد$'))
async def hunt_help(event):
    await event.edit("""
**أوامر الصيد الخاصة بسورس عبود**:

— — — — — — — — — —

النوع :( سداسي حرفين/ ثلاثي/ سداسي/ بوتات/ خماسي حرفين/خماسي /سباعي )

الامر: `.صيد` + النوع
- يقوم بصيد معرفات عشوائية حسب النوع

الامر: `تثبيت معرف` + معرف
* وظيفة الامر : يقوم بالتثبيت على المعرف عندما يصبح متاح يأخذه

— — — — — — — — — —
الامر: `.حالة الصيد`
• لمعرفة عدد المحاولات للصيد

الامر: `.حالة التثبيت`
• لمعرفة عدد المحاولات للصيد

**سورس عبود - @SSSTlF**
""")

@client.on(events.NewMessage(pattern=r'^\.صيد (.*)$'))
async def hunterusername(event):
    choice = str(event.pattern_match.group(1))
    await event.edit(f"**- تم تفعيل الصيد بنجاح الان**")
    try:
        ch = await client(CreateChannelRequest(title="ABOOD HUNTER - صيد عبود", about="This channel to hunt username by - @SSSTlF"))
        ch = ch.updates[1].channel_id
    except Exception as e:
        await client.send_message(event.chat_id, f"خطأ في انشاء القناة , الخطأ**- : {str(e)}**")
        return
    isclaim.clear()
    isclaim.append("on")
    sedmod = True
    while sedmod:
        username = gen_user(choice)
        if username == "error":
            await event.edit("**- يرجى وضع النوع بشكل صحيح**")
            break
        isav = check_user(username)
        if isav == True:
            try:
                await client(UpdateUsernameRequest(channel=ch, username=username))
                await event.client.send_file(event.chat_id, "https://t.me/Repthongif/2", caption="🐊 سورس عبود 🐊\n- - - - - - - - - - - - - - - - - - - - - - - -\n- UserName: ❲ @{} ❳\n- ClickS: ❲ {} ❳\n- Type: {}\n- Save: ❲ Channel ❳\n- - - - - - - - - - - - - - - - - - - - - - - -\nسورس عبود ❲ @SSSTlF ❳ ".format(username, trys, choice))
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
    msg = event.text.split()
    try:
        ch = str(msg[2])
        ch = ch.replace("@", "")
        await event.edit(f"حسناً سيتم بدء التثبيت في**- @{ch} .**")
    except:
        try:
            ch = await client(CreateChannelRequest(title="ABOOD HUNTER - تثبيت عبود", about="This channel to hunt username by - @SSSTlF"))
            ch = ch.updates[1].channel_id
            await event.edit(f"**- تم بنجاح بدأ التثبيت**")
        except Exception as e:
            await client.send_message(event.chat_id, f"خطأ في انشاء القناة , الخطأ : {str(e)}")
            return
    isauto.clear()
    isauto.append("on")
    username = str(msg[1])
    swapmod = True
    while swapmod:
        isav = check_user(username)
        if isav == True:
            try:
                await client(UpdateUsernameRequest(channel=ch, username=username))
                await event.client.send_file(event.chat_id, "https://t.me/Repthongif/2", caption="🐊 سورس عبود 🐊\n- - - - - - - - - - - - - - - - - - - - - - - -\n- UserName: ❲ @{} ❳\n- ClickS: ❲ {} ❳\n- Save: ❲ Channel ❳\n- - - - - - - - - - - - - - - - - - - - - - - -\nسورس عبود ❲ @SSSTlF ❳ ".format(username, trys2))
                swapmod = False
                break
            except Exception as eee:
                await client.send_message(event.chat_id, f"""خطأ مع {username} , الخطأ :{str(eee)}""")
                swapmod = False
                break
        else:
            pass
        trys2[0] += 1
    isauto.clear()
    isauto.append("off")

@client.on(events.NewMessage(pattern=r'^\.ايقاف الصيد$'))
async def stop_hunt(event):
    if "on" in isclaim:
        isclaim.clear()
        isclaim.append("off")
        return await event.edit("**- تم بنجاح ايقاف عملية الصيد**")
    elif "off" in isclaim:
        return await event.edit("**- لم يتم تفعيل الصيد بالأصل لأيقافه**")
    else:
        return await event.edit("**- لقد حدث خطأ ما وتوقف الامر لديك**")

@client.on(events.NewMessage(pattern=r'^\.ايقاف التثبيت$'))
async def stop_fix(event):
    if "on" in isauto:
        isauto.clear()
        isauto.append("off")
        return await event.edit("**- تم بنجاح ايقاف عملية التثبيت**")
    elif "off" in isauto:
        return await event.edit("**- لم يتم تفعيل التثبيت بالأصل لأيقافه**")
    else:
        return await event.edit("**-لقد حدث خطأ ما وتوقف الامر لديك**")

@client.on(events.NewMessage(pattern=r'^\.حالة الصيد$'))
async def hunt_status(event):
    if "on" in isclaim:
        await event.edit(f"**- الصيد وصل لـ({trys[0]}) من المحاولات**")
    elif "off" in isclaim:
        await event.edit("**- الصيد بالاصل لا يعمل .**")
    else:
        await event.edit("- لقد حدث خطأ ما وتوقف الامر لديك")

@client.on(events.NewMessage(pattern=r'^\.حالة التثبيت$'))
async def fix_status(event):
    if "on" in isauto:
        await event.edit(f"**- التثبيت وصل لـ({trys2[0]}) من المحاولات**")
    elif "off" in isauto:
        await event.edit("**- التثبيت بالاصل لا يعمل .**")
    else:
        await event.edit("-لقد حدث خطأ ما وتوقف الامر لديك")

# =====================================================================
#                        أَوَامِرُ الذَّاتِيَّةِ
# =====================================================================

repself = True

@client.on(events.NewMessage(pattern=r'^\.الذاتيه$'))
async def cmd(baqir):
    await edit_or_reply(baqir, """
سورس عبود @SSSTlF - حفظ الذاتيه 🧧

**⪼** `.تفعيل الذاتيه`
**لتفعيل الحفظ التلقائي للذاتيه**
**سوف يقوم حسابك بحفظ الذاتيه تلقائياً في حافظة حسابك عندما يرسل لك اي شخص ميديا ذاتيه**

**⪼** `.تعطيل الذاتيه`
**لتعطيل الحفظ التلقائي للذاتيه**

**⪼** `.ذاتيه`
**بالرد على صورة ذاتيه لحفظها في حال كان امر الحفظ التلقائي معطل**

**⪼** `.اعلان`
**الامر + الوقت بالدقائق + الرساله**
**امر مفيد لجماعة التمويل لعمل إعلان مؤقت بالقنوات**

**سورس عبود** @SSSTlF
""")

@client.on(events.NewMessage(pattern=r'^\.ذاتيه(?: |$)(.*)'))
async def oho(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالرد على صورة ذاتية التدمير**...")
    e_7_v = await event.get_reply_message()
    pic = await e_7_v.download_media()
    await client.send_file("me", pic, caption=f"**⎉╎تم حفظ الصورة الذاتيه .. بنجاح ☑️**")
    await event.delete()

@client.on(events.NewMessage(pattern=r'^\.تفعيل الذاتيه$'))
async def start_datea(event):
    global repself
    if repself:
        return await edit_or_reply(event, "**⎉╎حفظ الذاتية التلقائي .. مفعله مسبقاً ☑️**")
    repself = True
    await edit_or_reply(event, "**⎉╎تم تفعيل حفظ الذاتية التلقائي .. بنجاح ☑️**")

@client.on(events.NewMessage(pattern=r'^\.تعطيل الذاتيه$'))
async def stop_datea(event):
    global repself
    if repself:
        repself = False
        return await edit_or_reply(event, "**⎉╎تم تعطيل حفظ الذاتية التلقائي .. بنجاح ☑️**")
    await edit_or_reply(event, "**⎉╎حفظ الذاتية التلقائي .. معطله مسبقاً ☑️**")

@client.on(events.NewMessage(func=lambda e: e.is_private and (e.photo or e.video) and e.media_unread))
async def sddm(event):
    global repself
    baqir = event.sender_id
    taiba = client.uid
    if baqir == taiba:
        return
    if repself:
        sender = await event.get_sender()
        chat = await event.get_chat()
        pic = await event.download_media()
        await client.send_file("me", pic, caption=f"**سورس عبود** @SSSTlF - حفظ الذاتيه 🧧 .\n\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n**⌔╎مرحباً عزيزي المالك 🫂\n⌔╎تم حفظ الذاتية تلقائياً .. بنجاح ☑️** ❝\n**⌔╎المرسل** [{sender.first_name}](tg://user?id={sender.id}) .")

# =====================================================================
#                        أَوَامِرُ الإِعْلَانِ
# =====================================================================

@client.on(events.NewMessage(pattern=r'^\.اعلان (\d*) ([\s\S]*)'))
async def selfdestruct(destroy):
    rep = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = rep[1]
    ttl = int(rep[0])
    baqir = ttl * 60
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, message)
    await asyncio.sleep(baqir)
    await smsg.delete()

@client.on(events.NewMessage(pattern=r'^\.إعلان (\d*) ([\s\S]*)'))
async def selfdestruct2(destroy):
    rep = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = rep[1]
    ttl = int(rep[0])
    baqir = ttl * 60
    text = message + f"\n\n**- هذا الاعلان سيتم حذفه تلقائياً بعد {baqir} دقائق ⏳**"
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, text)
    await asyncio.sleep(baqir)
    await smsg.delete()

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
        print("⚠️ aiohttp غير مثبت - خادم الويب معطل")
    except Exception as e:
        print(f"⚠️ خطأ في تشغيل خادم الويب: {e}")

# =====================================================================
#                        حَلْقَةُ الْإِبْقَاءِ
# =====================================================================

async def keep_alive():
    while True:
        try:
            me = await client.get_me()
            await client.send_message(me.id, f"🔄 البوت يعمل... {datetime.now().strftime('%H:%M')}")
            print(f"✅ تم إرسال إشارة Keep-Alive في {datetime.now()}")
        except Exception as e:
            print(f"❌ خطأ في Keep-Alive: {e}")
            try:
                await client.disconnect()
                await client.start()
                print("✅ تم إعادة الاتصال")
            except:
                print("❌ فشل إعادة الاتصال")
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
