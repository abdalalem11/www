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

# ========== مكتبات خارجية ==========
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
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

# ========== متغيرات الصيد ==========
a = "qwertyuiopassdfghjklzxcvbnm"
b = "1234567890"
e = "qwertyuiopassdfghjklzxcvbnm1234567890"
trys, trys2 = [0], [0]
isclaim = ["off"]
isauto = ["off"]

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
    """جلب المستخدم من الحدث"""
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
    """التحقق من أن المستخدم هو المالك"""
    try:
        me = await event.client.get_me()
        sender = await event.get_sender()
        return sender.id == me.id
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

def get_saudi_time():
    utc_now = datetime.utcnow()
    saudi_time = utc_now + SAUDI_OFFSET
    return saudi_time

# =====================================================================
#                        فئة الديكورات
# =====================================================================

class jmthon:
    @staticmethod
    def ar_cmd(pattern=None, **kwargs):
        """ديكور معدل للأوامر"""
        def decorator(func):
            return func
        return decorator

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
#                        أَمْرُ فَحْص (ALIVE)
# =====================================================================

ALIVE_ET = Config.ALIVE_ET or "فحص"

@jmthon.ar_cmd(pattern=rf"{ALIVE_ET}")
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
    me = await event.client.get_me()
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
        except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
            return await edit_or_reply(
                event,
                f"**الميديا خطأ **\nغير الرابط باستخدام الأمر \n `.اضف_فار ALIVE_PIC رابط صورتك`\n\n**لا يمكن الحصول على صورة من الرابط :-** `{PIC}`",
            )
    else:
        await edit_or_reply(event, caption)

# =====================================================================
#                        أَمْرُ الْأَوَامِرِ
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
◙ `.نسخ احتياطي` - إنشاء نسخ احتياطي للإعدادات والجلسة

**🔄 أوامر التحديث وإعادة التشغيل:**
◙ `.اعادة تشغيل` - إعادة تشغيل البوت بالكامل
◙ `.تحديث` - تحديث السورس من GitHub تلقائياً
◙ `.تحديث قسري` - تحديث قسري مع إعادة تعيين التغييرات
◙ `.اخر تحديث` - عرض آخر تحديث وحالة السورس
◙ `.الانتحال` - شرح أوامر الانتحال
◙ `.انتحال جلسة <جلسة>` - انتحال حساب بجلسة

**📦 أوامر المتغيرات العامة (Gvar):**
◙ `.اضف_فار <اسم> <قيمة>` - إضافة متغير عام
◙ `.حذف_فار <اسم>` - حذف متغير عام
◙ `.فار <اسم>` - عرض قيمة متغير عام
◙ `.كل_الفارات` - عرض جميع المتغيرات العامة

**🛡️ أوامر الحماية:**
◙ `.قفل <نوع>` - قفل خاصية
◙ `.فتح <نوع>` - فتح خاصية
◙ `.الحاله` - عرض حالة الحماية
◙ `.البوتات` - كشف البوتات
◙ `.البوتات طرد` - طرد جميع البوتات
◙ `.غبان <ايدي>` - حظر عام للمستخدم
◙ `.الغاء غبان <ايدي>` - إلغاء الحظر العام
◙ `.المغبانيين` - عرض قائمة المحظورين عاماً

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
◙ `.الاحداث` - عرض آخر الرسائل المحذوفة
◙ `.الاحداث م` - عرض آخر الرسائل المحذوفة مع الميديا

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
◙ `.المطور` - عرض معلومات المطور
◙ `.جلسة` - عرض الجلسة الحالية

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
◙ `.اعلان <وقت> <رسالة>` - إعلان مؤقت (بالدقائق)
◙ `.إعلان <وقت> <رسالة>` - إعلان مؤقت مع تحذير

**🔎 أمر الكاشف:**
◙ `.الكاشف` - شرح أمر الكاشف
◙ `.كاشف <دولة> <رقم>` - كشف معلومات الرقم

**🎭 أوامر التسلية:**
◙ `.كت` - عرض حكمة عشوائية
◙ `.نسبه الحب <اسم1, اسم2>` - نسبة الحب بين شخصين

**🖼️ أوامر البروفايل:**
◙ `.تغيير اسمي <اسم>` - تغيير اسم الحساب
◙ `.تغيير بايو <نص>` - تغيير البايو
◙ `.تغيير صورتي` - تغيير صورة البروفايل (بالرد على صورة)
◙ `.حذف صورتي` - حذف جميع صور البروفايل

**📦 أوامر الإنشاء والتخزين:**
◙ `.انشاء مجموعة تخزين` - إنشاء مجموعة مخصصة للتخزين
◙ `.انشاء مجموعة <اسم>` - إنشاء مجموعة جديدة
◙ `.انشاء قناة <اسم>` - إنشاء قناة جديدة
◙ `.المجموعات` - عرض قائمة جميع المجموعات
◙ `.القنوات` - عرض قائمة جميع القنوات

**📖 أوامر أخرى:**
◙ `.مساعده` - عرض المساعدة
◙ `.فحص` - فحص البوت
◙ `.تنظيف` - تنظيف الملفات المؤقتة

**🔄 أوامر التكرار:**
◙ `.سبام <عدد> <رسالة>` - تكرار إرسال رسالة (الحد الأقصى 99)
◙ `.مكرر <وقت> <عدد> <رسالة>` - تكرار إرسال رسالة بفاصل زمني
◙ `.فصخ <جملة>` - تفصيخ الجملة حرفاً حرفاً
◙ `.ايقاف مكرر` - إيقاف أمر المكرر

✧ **سورس عبود** ✧
"""
    await event.reply(commands_text)

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
🆔 الايدي: `{me.id}`
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
📱 تم استقبال الرقم: `{phone}`

⏳ جاري إرسال رمز التحقق...
📩 أرسل الرمز الذي وصل إلى تيليجرام

✧ سورس عبود ✧
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
✅ تم التنصيب بنجاح!

📋 المعرف: `{me_new.id}`
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

📋 المعرف: `{me_new.id}`
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

📌 الإصدار الحالي: `{current_commit}`
👤 آخر تحديث: {latest_author}
📝 الرسالة: {latest_message}

✧ سورس عبود ✧
""")
            return
        
        await zedevent.edit(f"""
🔄 جاري تحديث السورس...

📌 الإصدار الحالي: `{current_commit}`
📌 الإصدار الجديد: `{latest_commit}`
👤 المطور: {latest_author}
📝 التحديث: {latest_message}

⏳ جاري سحب التحديثات...
""")
        
        pull_result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        
        if pull_result.returncode != 0:
            return await zedevent.edit(f"""
❌ فشل التحديث!

📌 الخطأ:
`{pull_result.stderr}`

💡 الحل: تأكد من الاتصال بالإنترنت وصلاحية الوصول إلى GitHub
""")
        
        await zedevent.edit(f"""
✅ تم تحديث السورس بنجاح!

📌 الإصدار الجديد: `{latest_commit}`
📝 التحديث: {latest_message}
👤 المطور: {latest_author}

🔄 جاري إعادة تشغيل البوت...
✧ سورس عبود ✧
""")
        
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
        
    except Exception as e:
        await zedevent.edit(f"❌ خطأ في التحديث:\n`{str(e)}`")

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

📌 الإصدار الحالي: `{current_commit}`
📌 آخر إصدار: `{latest_commit}`

👤 المطور: {latest_author}
📝 آخر تحديث: {latest_message}

📖 آخر 5 تغييرات:
