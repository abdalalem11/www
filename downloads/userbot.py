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

# ========== مكتبات خارجية ==========
from telethon import TelegramClient, events, Button
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
    YouBlockedUserError
)
from telethon.tl.functions.account import UpdateProfileRequest
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
    EditChatDefaultBannedRightsRequest
)
from telethon.tl.functions.phone import (
    CreateGroupCallRequest as startvc,
    DiscardGroupCallRequest as stopvc,
    GetGroupCallRequest as getvc,
    InviteToGroupCallRequest as invitetovc
)
from telethon.tl.functions.photos import GetUserPhotosRequest, DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.utils import get_input_location, get_display_name

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

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", CONFIG.get("api_id", 0)))
API_HASH = os.environ.get("API_HASH", CONFIG.get("api_hash", ""))
SESSION = os.environ.get("SESSION_STRING", CONFIG.get("session_string", ""))

if not API_ID or not API_HASH:
    print("❌ تأكد من تعيين API_ID و API_HASH في المتغيرات أو ملف config.json")
    print("⚠️ سيتم استخدام القيم الافتراضية للتجربة")
    API_ID = 2040
    API_HASH = "b18441a1ff607e10a989891a5462e627"

# ========== متغيرات عامة ==========
time_enabled = CONFIG.get("time_enabled", False)
SAUDI_OFFSET = timedelta(hours=CONFIG.get("saudi_offset_hours", 3))
QUOTES = CONFIG.get("quotes", [])
DEFAULTUSER = gvarstatus("ALIVE_NAME") or "المستخدم"
CHANGE_TIME = int(gvarstatus("CHANGE_TIME")) if gvarstatus("CHANGE_TIME") else 60

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

# ========== التحقق من الجلسة عند بدء التشغيل ==========
async def start_client():
    try:
        await client.start()
        me = await client.get_me()
        print(f"✅ البوت يعمل كـ: {me.first_name} (ID: {me.id})")
        return True
    except Exception as e:
        print(f"❌ خطأ في الجلسة: {e}")
        print("📌 استخدم أمر .تنصيب جلسة لإرسال جلسة جديدة")
        return False

# ========== دوال مساعدة ==========
def get_saudi_time():
    utc_now = datetime.utcnow()
    saudi_time = utc_now + SAUDI_OFFSET
    return saudi_time

# ========== تعطيل حماية المالك لأوامر التنصيب ==========
OWNER_ONLY_COMMANDS = ['.تنصيب', '.تنصيب جلسة']

async def is_owner(event):
    # إذا كان الأمر من أوامر التنصيب، اسمح لأي شخص
    if event.raw_text and any(cmd in event.raw_text for cmd in OWNER_ONLY_COMMANDS):
        return True
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

async def fetch_info(replied_user, event):
    """جلب معلومات المستخدم"""
    FullUser = (await event.client(GetFullUserRequest(replied_user.id))).full_user
    replied_user_profile_photos = await event.client(
        GetUserPhotosRequest(user_id=replied_user.id, offset=42, max_id=0, limit=80)
    )
    replied_user_profile_photos_count = "لايـوجـد بروفـايـل"
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
    
    photo = await event.client.download_profile_photo(
        user_id,
        os.path.join("downloads", str(user_id) + ".jpg"),
        download_big=True
    )
    
    first_name = first_name.replace("\u2060", "") if first_name else "هذا المستخدم ليس له اسم أول"
    full_name = full_name or first_name
    username = f"@{username}" if username else "لايـوجـد معـرف"
    user_bio = "لاتـوجـد نبـذة" if not user_bio else user_bio
    
    rotbat = "⌁ مـن مـطـوريـن الـسـورس ⌁" if user_id == 5502537272 else "⌁ العضـو ⌁"
    if user_id == (await event.client.get_me()).id and user_id != 5502537272:
        rotbat = "⌁ مـالـك الـحسـاب ⌁"
    
    caption = "✛━━━━━━━━━━━━━✛\n"
    caption += f"<b> •❃╎الاسـم    ⇠ </b> {full_name}\n"
    caption += f"<b> •❃╎المعـرف  ⇠ </b> {username}\n"
    caption += f"<b> •❃╎الايـدي   ⇠ </b> <code>{user_id}</code>\n"
    caption += f"<b> •❃╎الرتبـــه  ⇠ {rotbat} </b>\n"
    caption += f"<b> •❃╎الصـور   ⇠ </b> {replied_user_profile_photos_count}\n"
    caption += f"<b> •❃╎الحساب ⇠ </b> "
    caption += f'<a href="tg://user?id={user_id}">{first_name}</a>'
    caption += f"\n<b> •❃╎البايـو    ⇠ </b> {user_bio} \n"
    caption += f"✛━━━━━━━━━━━━━✛"
    return photo, caption

# ================================================================
#                        حلقات الخلفية
# ================================================================

async def keep_alive():
    """إبقاء البوت نشطاً"""
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

async def digitalpic_loop():
    """حلقة الصورة الوقتية"""
    global digitalpic_running
    if Image is None:
        print("❌ Pillow غير مثبت - تعطيل الصورة الوقتية")
        digitalpic_running = False
        return
    
    i = 0
    while digitalpic_running:
        digitalpic_path = gvarstatus("DIGITAL_PIC_PATH") or "digital_pic.png"
        if not os.path.exists(digitalpic_path):
            print("❌ الصورة الوقتية غير موجودة")
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
                await client(DeletePhotosRequest(
                    await client.get_profile_photos("me", limit=1)
                ))
            i += 1
            await client(UploadProfilePhotoRequest(file))
            os.remove(autophoto_path)
        except Exception as e:
            print(f"❌ خطأ في الصورة الوقتية: {e}")
        
        await asyncio.sleep(CHANGE_TIME)

async def autoname_loop():
    """حلقة الاسم الوقتي"""
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

async def autobio_loop():
    """حلقة البايو الوقتي"""
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

# ================================================================
#                   قائمة الأوامر (Commands List)
# ================================================================

@client.on(events.NewMessage(pattern=r'^\.الاوامر$'))
async def show_commands(event):
    if not await is_owner(event):
        return
    
    commands_text = """
✧ **قائمة الأوامر الرئيسية** ✧

**📥 أوامر التنصيب:**
◙ `.تنصيب` - تنصيب البوت بالرقم والرمز
◙ `.تنصيب جلسة` - تنصيب البوت بالجلسة المستخرجة

**🛡️ أوامر الحماية:**
◙ `.قفل <نوع>` - قفل خاصية (البوتات، المعرفات، الدخول، الاضافه، التوجيه، الميديا، الانلاين، الفشار، الروابط، الفارسيه، الكل)
◙ `.فتح <نوع>` - فتح خاصية
◙ `.الحاله` - عرض حالة الحماية
◙ `.البوتات` - كشف البوتات
◙ `.البوتات طرد` - طرد جميع البوتات

**👥 أوامر المجموعة:**
◙ `.تفليش` - حظر جميع الأعضاء (ما عدا المشرفين)
◙ `.تصفير` - طرد جميع الأعضاء (ما عدا المشرفين)
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

# ================================================================
#                   أمر التنصيب بالجلسة (Install Session)
# ================================================================

@client.on(events.NewMessage(pattern=r'^\.تنصيب جلسة$'))
async def install_session_command(event):
    # تم إزالة شرط is_owner للسماح لأي حساب بالتنصيب
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
    
    # التحقق من الجلسة
    try:
        temp_client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await temp_client.connect()
        me = await temp_client.get_me()
        await temp_client.disconnect()
    except Exception as e:
        await event.reply(f"❌ الجلسة غير صالحة: {str(e)}")
        waiting_for_session = False
        return
    
    # حفظ الجلسة
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
    
    # إعادة تشغيل البوت
    try:
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
    except:
        await event.reply("⚠️ أعد تشغيل البوت يدوياً")

# ================================================================
#                   أمر التنصيب العادي (Install)
# ================================================================

@client.on(events.NewMessage(pattern=r'^\.تنصيب$'))
async def install_bot(event):
    global install_waiting, install_user_id, install_step, install_client

    # تم إزالة شرط is_owner للسماح لأي حساب بالتنصيب

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
                await install_client.sign_in(
                    phone=install_phone,
                    code=code,
                    phone_code_hash=install_hash
                )

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

# ================================================================
#                   أوامر التحميل (Download Commands)
# ================================================================

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

# ================================================================
#                   أوامر الحماية (Protection)
# ================================================================

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

# ================================================================
#                   أوامر المجموعة (Group Commands)
# ================================================================

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

# ================================================================
#                   أوامر المعلومات (Info Commands)
# ================================================================

@client.on(events.NewMessage(pattern=r'^\.ايدي(?: |$)(.*)'))
async def who(event):
    """عرض معلومات الشخص"""
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
            await event.client.send_file(
                event.chat_id,
                photo,
                caption=caption,
                link_preview=False,
                force_document=False,
                reply_to=message_id_to_reply,
                parse_mode="html",
            )
            if os.path.exists(photo):
                os.remove(photo)
            await cat.delete()
        else:
            await cat.edit(caption, parse_mode="html")
    except Exception as e:
        await cat.edit(caption, parse_mode="html")

@client.on(events.NewMessage(pattern=r'^\.كشف(?:\s|$)([\s\S]*)'))
async def userinfo(event):
    """عرض معلومات المستخدم مع تفاصيل إضافية"""
    replied_user = await get_user_from_event(event)
    if not replied_user:
        return
    
    catevent = await edit_or_reply(event, "᯽︙ جاري إحضار معلومات المستخدم ⚒️")
    replied_user = await event.client(GetFullUserRequest(replied_user.id))
    user_id = replied_user.users[0].id
    first_name = html.escape(replied_user.users[0].first_name)
    if first_name is not None:
        first_name = first_name.replace("\u2060", "")
    
    common_chats = 1
    try:
        dc_id, location = get_input_location(replied_user.profile_photo)
    except Exception:
        dc_id = "Couldn't fetch DC ID!"
    
    try:
        casurl = f"https://api.cas.chat/check?user_id={user_id}"
        data = get(casurl).json()
        if data and data.get("ok"):
            cas = "**Antispam(CAS) محظور:** `True`"
        else:
            cas = "**Antispam(CAS) محظور:** `False`"
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
    """عرض الايدي فقط"""
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
            await edit_or_reply(
                event,
                f"᯽︙ ايدي الدردشه: `{str(event.chat_id)}` \n᯽︙ ايدي المستخدم: `{str(r_msg.sender_id)}`"
            )
        else:
            await edit_or_reply(
                event,
                f"᯽︙ ايدي الدردشه: `{str(event.chat_id)}` \n᯽︙ ايدي المستخدم: `{str(r_msg.sender_id)}`"
            )
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
    """إنشاء رابط للمستخدم"""
    user = await get_user_from_event(event)
    if not user:
        return
    custom = event.pattern_match.group(1)
    if custom:
        return await edit_or_reply(event, f"[{custom}](tg://user?id={user.id})")
    tag = user.first_name.replace("\u2060", "") if user.first_name else user.username
    await edit_or_reply(event, f"⌔︙[{tag}](tg://user?id={user.id})")

# ================================================================
#                   أوامر البحث (Search Commands)
# ================================================================

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

# ================================================================
#                   أوامر التسلية (Fun Commands)
# ================================================================

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

# ================================================================
#                   أوامر الوقت (Time Commands)
# ================================================================

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

# ================================================================
#                   أوامر الوقتية (Auto Profile Commands)
# ================================================================

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

# ================================================================
#                   أوامر المشرفين (Admin Commands)
# ================================================================

# أوامر رفع وتنزيل المشرفين
@client.on(events.NewMessage(pattern=r'^\.رفع مشرف(?:\s|$)([\s\S]*)'))
async def promote(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "**⪼ أحتـاج الى صلاحيـات المشـرف هنـا!!**")
        return
    
    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=False,
        delete_messages=True,
        pin_messages=True,
    )
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "**╮ ❐  جـارِ  ࢪفعـه مشـرف  . . .❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("**⪼ ليست لدي صلاحيـات كافيـه في هـذه المجمـوعـة**")
    await zzevent.edit("**- ❝ ⌊  تـم تـرقيتـه مشـرف .. بنجـاح**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#رفــع_مشــرف\
            \n**- الشخـص :** [{user.first_name}](tg://user?id={user.id})\
            \n**- الكــروب :** {get_display_name(await event.get_chat())} (`{event.chat_id}`)",
        )

@client.on(events.NewMessage(pattern=r'^\.رفع مالك(?:\s|$)([\s\S]*)'))
async def promote_full(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "**⪼ أحتـاج الى صلاحيـات المشـرف هنـا!!**")
        return
    new_rights = ChatAdminRights(
        add_admins=True,
        invite_users=True,
        change_info=True,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
        manage_call=True,
    )
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "**╮ ❐  جـاري ࢪفعه مشـرف بكـل الصـلاحيـات  ❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("**⪼ ليست لدي صلاحيـات كافيـه في هـذه المجمـوعـة**")
    await zzevent.edit("**- ❝ ⌊  تم تـرقيتـه مشـرف عـام بكـل الصـلاحيـات . . .**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#رفــع_مشــرف\
            \n**- الشخـص :** [{user.first_name}](tg://user?id={user.id})\
            \n**- الكــروب :** {get_display_name(await event.get_chat())} (`{event.chat_id}`)",
        )

@client.on(events.NewMessage(pattern=r'^\.اخفاء(?:\s|$)([\s\S]*)'))
async def promote_anonymous(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "**⪼ أحتـاج الى صلاحيـات المشـرف هنـا!!**")
        return
    new_rights = ChatAdminRights(
        add_admins=True,
        invite_users=True,
        change_info=True,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
        manage_call=True,
        anonymous=True,
    )
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    zzevent = await edit_or_reply(event, "**╮ ❐  جـارِ التعديل  ❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await zzevent.edit("**⪼ ليست لدي صلاحيـات كافيـه في هـذه المجمـوعـة**")
    await zzevent.edit("**- ❝ ⌊  تم التعديل بنجاح**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#رفــع_مشــرف\
            \n**- الشخـص :** [{user.first_name}](tg://user?id={user.id})\
            \n**- الكــروب :** {get_display_name(await event.get_chat())} (`{event.chat_id}`)",
        )

@client.on(events.NewMessage(pattern=r'^\.تنزيل مشرف(?:\s|$)([\s\S]*)'))
async def demote(event):
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, "**⪼ أحتـاج الى صلاحيـات المشـرف هنـا!!**")
        return
    user, _ = await get_user_from_event(event)
    if not user:
        return
    zzevent = await edit_or_reply(event, "**╮ ❐ جـارِ التنزيل  ❏╰**")
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    rank = "مشرف"
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, newrights, rank))
    except BadRequestError:
        return await zzevent.edit("**⪼ ليست لدي صلاحيـات كافيـه في هـذه المجمـوعـة**")
    await zzevent.edit("**- ❝ ⌊  تم تنزيلـه من الاشـرف بنجـاح**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#تنـزيــل_مشــرف\
            \n**- الشخـص :** [{user.first_name}](tg://user?id={user.id})\
            \n**- الكــروب :** {get_display_name(await event.get_chat())}(`{event.chat_id}`)",
        )

# أوامر الحظر والكتم والطرد
@client.on(events.NewMessage(pattern=r'^\.حظر(?:\s|$)([\s\S]*)'))
async def _ban_person(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if user.id == event.client.uid:
        return await edit_delete(event, "**⪼ عـذراً ..لا استطيـع حظـࢪ نفسـي**")
    if user.id == 5502537272:
        return await edit_delete(event, "**╮ ❐ دي لا يمڪنني حظـر احـد مطـورين السـورس  ❏╰**")
    zedevent = await edit_or_reply(event, "**╮ ❐... جـاࢪِ الحـظـࢪ ...❏╰**")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await zedevent.edit("**⪼ ليست لدي صلاحيـات كافيـه في هـذه المجمـوعـة**")
    if reason:
        await zedevent.edit(f"**- المستخـدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تـم حظـࢪه بنجـاح ☑️**\n\n**- السـبب :** `{reason}`")
    else:    
        await zedevent.edit(f"**- المستخـدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تـم حظــࢪه بنجـاح ☑️**")
    if BOTLOG:
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#الحظــࢪ\
                \n- الشخـص : [{user.first_name}](tg://user?id={user.id})\
                \n- الدردشــه: {get_display_name(await event.get_chat())}(`{event.chat_id}`)\
                \n- السـبب : {reason}",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#الحظــࢪ\
                \n- الشخـص : [{user.first_name}](tg://user?id={user.id})\
                \n- الدردشــه : {get_display_name(await event.get_chat())}(`{event.chat_id}`)",
            )

@client.on(events.NewMessage(pattern=r'^\.الغاء حظر(?:\s|$)([\s\S]*)'))
async def nothanos(event):
    user, _ = await get_user_from_event(event)
    if not user:
        return
    zedevent = await edit_or_reply(event, "**╮ ❐.. جـاري الغاء حـظࢪه ..❏╰**")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await zedevent.edit(f"**- المستخـدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تم الغـاء حظــࢪه بنجــاح ✓**")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الغــاء_الحظــࢪ\n"
                f"- الشخـص : [{user.first_name}](tg://user?id={user.id})\n"
                f"- الدردشــه : {get_display_name(await event.get_chat())}(`{event.chat_id}`)",
            )
    except UserIdInvalidError:
        await zedevent.edit("`Uh oh my unban logic broke!`")
    except Exception as e:
        await zedevent.edit(f"**- خطــأ :**\n`{e}`")

@client.on(events.NewMessage(pattern=r'^\.كتم(?:\s|$)([\s\S]*)'))
async def startmute(event):
    if event.is_private:
        replied_user = await event.client.get_entity(event.chat_id)
        if is_muted(event.chat_id, event.chat_id):
            return await event.edit("**- ❝ ⌊هـذا المسـتخـدم مڪتـوم . . سـابقـاً**")
        if event.chat_id == client.uid:
            return await edit_delete(event, "**- لا تستطــع كتـم نفسـك**")
        if event.chat_id == 5502537272:
            return await edit_delete(event, "**╮ ❐ دي لا يمڪنني كتـم احـد مطـورين السـورس  ❏╰**")
        try:
            mute_user(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"**- خطـأ **\n`{e}`")
        else:
            await event.edit("**⪼ تم ڪتـم الـمستخـدم  . . بنجـاح 🔕**")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#كتــم_الخــاص\n"
                f"**- الشخـص  :** [{replied_user.first_name}](tg://user?id={event.chat_id})\n",
            )
    else:
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        if not admin and not creator:
            return await edit_or_reply(event, "**⪼ أنـا لسـت مشـرف هنـا ؟!!**")
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == client.uid:
            return await edit_or_reply(event, "**- عــذراً .. لا استطيــع كتــم نفســي**")
        if user.id == 5502537272:
            return await edit_or_reply(event, "**╮ ❐ دي لا يمڪنني كتـم احـد مطـورين السـورس  ❏╰**")
        if is_muted(user.id, event.chat_id):
            return await edit_or_reply(event, "**عــذراً .. هـذا الشخـص مكتــوم سـابقــاً هنـا**")
        try:
            mute_user(user.id, event.chat_id)
        except Exception as e:
            return await edit_or_reply(event, f"**- خطــأ : **`{e}`")
        if reason:
            await edit_or_reply(event, f"**- المستخـدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تـم كتمـه بنجـاح ☑️**\n\n**- السـبب :** {reason}")
        else:
            await edit_or_reply(event, f"**- المستخـدم :** [{user.first_name}](tg://user?id={user.id})  \n**- تـم كتمـه بنجـاح ☑️**")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الكــتم\n"
                f"**الشخـص :** [{user.first_name}](tg://user?id={user.id})\n"
                f"**الدردشـه :** {get_display_name(await event.get_chat())}(`{event.chat_id}`)",
            )

@client.on(events.NewMessage(pattern=r'^\.الغاء كتم(?:\s|$)([\s\S]*)'))
async def endmute(event):
    if event.is_private:
        replied_user = await event.client.get_entity(event.chat_id)
        if not is_muted(event.chat_id, event.chat_id):
            return await event.edit("**عــذراً .. هـذا الشخـص غيــر مكتــوم هنـا**")
        try:
            unmute_user(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"**- خطـأ **\n`{e}`")
        else:
            await event.edit("**- تـم الغــاء كتــم الشخـص هنـا .. بنجــاح ✓**")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الغــاء_الكــتم\n"
                f"**- الشخـص :** [{replied_user.first_name}](tg://user?id={event.chat_id})\n",
            )
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
            return await edit_or_reply(event, "**- الشخـص غيـر مكـتـوم**")
        except Exception as e:
            return await edit_or_reply(event, f"**- خطــأ : **`{e}`")
        await edit_or_reply(event, f"**- المستخـدم :** [{user.first_name}](tg://user?id={user.id}) \n**- تـم الغـاء كتمـه بنجـاح ☑️**")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الغــاء_الكــتم\n"
                f"**- الشخـص :** [{user.first_name}](tg://user?id={user.id})\n"
                f"**- الدردشــه :** {get_display_name(await event.get_chat())}(`{event.chat_id}`)",
            )

@client.on(events.NewMessage(pattern=r'^\.طرد(?:\s|$)([\s\S]*)'))
async def kick(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if user.id == 5502537272:
        return await edit_delete(event, "**╮ ❐ دي لا يمڪنني طـرد احـد مطـورين السـورس  ❏╰**")
    zedevent = await edit_or_reply(event, "**╮ ❐... جـاࢪِ الطــࢪد ...❏╰**")
    try:
        await event.client.kick_participant(event.chat_id, user.id)
    except Exception as e:
        return await zedevent.edit(f"**⪼ ليست لدي صلاحيـات كافيـه في هـذه المجمـوعـة**\n{e}")
    if reason:
        await zedevent.edit(f"**- تـم طــࢪد** [{user.first_name}](tg://user?id={user.id})  **بنجــاح ✓**\n\n**- السـبب :** {reason}")
    else:
        await zedevent.edit(f"**- تـم طــࢪد** [{user.first_name}](tg://user?id={user.id})  **بنجــاح ✓**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#الـطــࢪد\n"
            f"**- الشخـص**: [{user.first_name}](tg://user?id={user.id})\n"
            f"**- الدردشــه** : {get_display_name(await event.get_chat())}(`{event.chat_id}`)\n",
        )

# ================================================================
#                   أوامر الصورة (Photo Commands)
# ================================================================

PP_TOO_SMOL = "**⪼ الصورة صغيرة جدا**"
PP_ERROR = "**⪼ فشل اثناء معالجة الصورة**"
NO_ADMIN = "**⪼ أحتـاج الى صلاحيـات المشـرف هنـا!!**"
NO_PERM = "**⪼ ليست لدي صلاحيـات كافيـه في هـذه المجمـوعـة**"
CHAT_PP_CHANGED = "**⪼ تم تغييـر صـورة المجمـوعـة .. بنجـاح ✓**"
INVALID_MEDIA = "**⪼ ابعاد الصورة غير صالحة**"

@client.on(events.NewMessage(pattern=r'^\.الصورة (وضع|حذف)$'))
async def set_group_photo(event):
    "لـ وضـع صــوره لـ المجمـوعـه"
    flag = (event.pattern_match.group(1)).strip()
    if flag == "وضع":
        replymsg = await event.get_reply_message()
        photo = None
        if replymsg and replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await event.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split("/"):
                photo = await event.client.download_file(replymsg.media.document)
            else:
                return await edit_delete(event, INVALID_MEDIA)
        if photo:
            try:
                await event.client(
                    EditPhotoRequest(
                        event.chat_id, await event.client.upload_file(photo)
                    )
                )
                await edit_delete(event, CHAT_PP_CHANGED)
            except PhotoCropSizeSmallError:
                return await edit_delete(event, PP_TOO_SMOL)
            except ImageProcessFailedError:
                return await edit_delete(event, PP_ERROR)
            except Exception as e:
                return await edit_delete(event, f"**- خطــأ : **`{str(e)}`")
            process = "تم تغييرهـا"
    else:
        try:
            await event.client(EditPhotoRequest(event.chat_id, InputChatPhotoEmpty()))
        except Exception as e:
            return await edit_delete(event, f"**- خطــأ : **`{e}`")
        process = "تم حذفهـا"
        await edit_delete(event, "**- صورة الدردشـه {process} . . بنجـاح ✓**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#صـورة_المجمـوعـة\n"
            f"صورة المجموعه {process} بنجاح ✓ "
            f"الدردشة: {get_display_name(await event.get_chat())}(`{event.chat_id}`)",
        )

# ================================================================
#                   أوامر التثبيت (Pin Commands)
# ================================================================

@client.on(events.NewMessage(pattern=r'^\.تثبيت( لود|$)$'))
async def pin(event):
    "لـ تثبيـت الرسـائـل فـي الكــروب"
    to_pin = event.reply_to_msg_id
    if not to_pin:
        return await edit_delete(event, "**- بالــرد ع رسـالـه لـ تثبيتـهـا...**", 5)
    options = event.pattern_match.group(1)
    is_silent = bool(options)
    try:
        await event.client.pin_message(event.chat_id, to_pin, notify=is_silent)
    except BadRequestError:
        return await edit_delete(event, NO_PERM, 5)
    except Exception as e:
        return await edit_delete(event, f"`{e}`", 5)
    await edit_delete(event, "**- تـم تثبيـت الرسـالـه .. بنجــاح ✓**", 3)
    if BOTLOG and not event.is_private:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#تثبيــت_رســالـه\
                \n**- تـم تثبيــت رســالـه فـي الدردشــه**\
                \n**- الدردشــه** : {get_display_name(await event.get_chat())}(`{event.chat_id}`)\
                \n**- لـــود** : {is_silent}",
        )

@client.on(events.NewMessage(pattern=r'^\.الغاء تثبيت( الكل|$)$'))
async def unpin(event):
    "لـ الغــاء تثبيـت الرسـائـل فـي الكــروب"
    to_unpin = event.reply_to_msg_id
    options = (event.pattern_match.group(1)).strip()
    if not to_unpin and options != "الكل":
        return await edit_delete(
            event,
            "**- بالــرد ع رســالـه لـ الغــاء تثبيتـهــا او اسـتخـدم امـر .الغاء تثبيت الكل**",
            5,
        )
    try:
        if to_unpin and not options:
            await event.client.unpin_message(event.chat_id, to_unpin)
        elif options == "all":
            await event.client.unpin_message(event.chat_id)
        else:
            return await edit_delete(
                event, "**- بالــرد ع رســالـه لـ الغــاء تثبيتـهــا او اسـتخـدم امـر .الغاء تثبيت الكل**", 5
            )
    except BadRequestError:
        return await edit_delete(event, NO_PERM, 5)
    except Exception as e:
        return await edit_delete(event, f"`{e}`", 5)
    await edit_delete(event, "**- تـم الغـاء تثبيـت الرسـالـه/الرسـائـل .. بنجــاح ✓**", 3)
    if BOTLOG and not event.is_private:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#الغــاء_تثبيــت_رســالـه\
                \n**- تـم الغــاء تثبيــت رســالـه فـي الدردشــه**\
                \n**- الدردشــه** : {get_display_name(await event.get_chat())}(`{event.chat_id}`)",
        )

# ================================================================
#                   أوامر الأحداث (Admin Log Commands)
# ================================================================

@client.on(events.NewMessage(pattern=r'^\.الاحداث( م)?(?: |$)(\d*)?$'))
async def _iundlt(event):
    "لـ جـلب آخـر الرسـائـل المحـذوفـه مـن الاحـداث بـ العـدد"
    zedevent = await edit_or_reply(event, "**- جـاري البحث عـن آخـر الاحداث انتظــر ...🔍**")
    flag = event.pattern_match.group(1)
    if event.pattern_match.group(2) != "":
        lim = int(event.pattern_match.group(2))
        lim = min(lim, 15)
        if lim <= 0:
            lim = 1
    else:
        lim = 5
    adminlog = await event.client.get_admin_log(
        event.chat_id, limit=lim, edit=False, delete=True
    )
    deleted_msg = f"**- اليـك آخـر {lim} رسـائـل محذوفــه لـ هـذا الكــروب 🗑 :**"
    if not flag:
        for msg in adminlog:
            ruser = await event.client.get_entity(msg.old.from_id)
            _media_type = media_type(msg.old)
            if _media_type is None:
                deleted_msg += f"\n🖇┊{msg.old.message} \n\n**🛂┊تم ارسـالهـا بـواسطـة** [{ruser.first_name}](tg://user?id={ruser.id})"
            else:
                deleted_msg += f"\n🖇┊{_media_type} \n\n**🛂┊تم ارسـالهـا بـواسطـة** [{ruser.first_name}](tg://user?id={ruser.id})"
        await edit_or_reply(zedevent, deleted_msg)
    else:
        main_msg = await edit_or_reply(zedevent, deleted_msg)
        for msg in adminlog:
            ruser = await event.client.get_entity(msg.old.from_id)
            _media_type = media_type(msg.old)
            if _media_type is None:
                await main_msg.reply(
                    f"\n🖇┊{msg.old.message} \n\n**🛂┊تم ارسـالهـا بـواسطـة** [{ruser.first_name}](tg://user?id={ruser.id})"
                )
            else:
                await main_msg.reply(
                    f"\n🖇┊{msg.old.message} \n\n**🛂┊تم ارسـالهـا بـواسطـة** [{ruser.first_name}](tg://user?id={ruser.id})",
                    file=msg.old.media,
                )

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

# ================================================================
#                   أوامر الصيد (Hunt Commands)
# ================================================================

import random
import requests
from fake_useragent import UserAgent
from telethon.sync import functions

a = "qwertyuiopassdfghjklzxcvbnm"
b = "1234567890"
e = "qwertyuiopassdfghjklzxcvbnm1234567890"

trys, trys2 = [0], [0]
isclaim = ["off"]
isauto = ["off"]

def check_user(username):
    url = "https://t.me/" + str(username)
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    session = requests.Session()
    response = session.get(url, headers=headers)
    if response.text.find('If you have <strong>Telegram</strong>, you can contact <a class="tgme_username_link"') >= 0:
        return True
    else:
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
        username = "".join(f)
        username = username + "bot"
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
**أوامـر الـصـيـد الخـاصة بـســورس عبود**: 

ٴ— — — — — — — — — —

النوع :(  سداسي حرفين/ ثلاثي/ سداسي/ بوتات/ خماسي حرفين/خماسي /سباعي )

الامر:  `.صيد` + النوع
- يقوم بصيد معرفات عشوائية حسب النوع

الامر:  `تثبيت معرف` + معرف
* وظيفة الامر : يقوم بالتثبيت على المعرف عندما يصبح متاح يأخذه

ٴ— — — — — — — — — —
الامر:   `.حالة الصيد`
• لمعرفة عدد المحاولات للصيد

الامر:  `.حالة التثبيت`
• لمعرفة عدد المحاولات للصيد

**سورس عبود - @SSSTlF**

""")

@client.on(events.NewMessage(pattern=r'^\.صيد (.*)$'))
async def hunterusername(event):
    choice = str(event.pattern_match.group(1))
    await event.edit(f"**- تم تفعيل الصيد بنجاح الان**")
    try:
        ch = await client(
            functions.channels.CreateChannelRequest(
                title="ABOOD HUNTER - صيد عبود",
                about="This channel to hunt username by - @SSSTlF",
            )
        )
        ch = ch.updates[1].channel_id
    except Exception as e:
        await client.send_message(
            event.chat_id, f"خطأ في انشاء القناة , الخطأ**-  : {str(e)}**"
        )
        sedmod = False
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
                await client(
                    functions.channels.UpdateUsernameRequest(
                        channel=ch, username=username
                    )
                )
                await event.client.send_file(
                    event.chat_id,
                    "https://t.me/Repthongif/2",
                    caption="🐊 سورس عبود 🐊\n- - - - - - - - - - - - - - - - - - - - - - - -\n- UserName: ❲ @{} ❳\n- ClickS: ❲ {} ❳\n- Type: {}\n- Save: ❲ Chaneel ❳\n- - - - - - - - - - - - - - - - - - - - - - - -\nسورس عبود ❲ @SSSTlF ❳ ".format(
                        username, trys, choice
                    ),
                )
                await event.client.send_file(
                    ch,
                    "https://t.me/Repthongif/2",
                    caption="🐊 سورس عبود 🐊\n- - - - - - - - - - - - - - - - - - - - - - - -\n- UserName: ❲ @{} ❳\n- ClickS: ❲ {} ❳\n- Type: {}\n- Save: ❲ Chaneel ❳\n- - - - - - - - - - - - - - - - - - - - - - - -\nسورس عبود ❲ @SSSTlF ❳ ".format(
                        username, trys, choice
                    ),
                )
                sedmod = False
                break
            except telethon.errors.rpcerrorlist.UsernameInvalidError:
                pass
            except Exception as baned:
                if "(caused by UpdateUsernameRequest)" in str(baned):
                    pass
            except telethon.errors.FloodError as e:
                await client.send_message(
                    event.chat_id,
                    f"للاسف تبندت , مدة الباند**-  ({e.seconds}) ثانية .**",
                )
                sedmod = False
                break
            except Exception as eee:
                if "the username is already" in str(eee):
                    pass
                if "USERNAME_PURCHASE_AVAILABLE" in str(eee):
                    pass
                else:
                    await client.send_message(
                        event.chat_id,
                        f"""- خطأ مع @{username} , الخطأ :{str(eee)}""",
                    )
                    sedmod = False
                    break
        else:
            pass
        trys[0] += 1
    isclaim.clear()
    isclaim.append("off")

@client.on(events.NewMessage(pattern=r'^\.تثبيت معرف (.*)$'))
async def _(event):
    msg = event.text.split()
    try:
        ch = str(msg[2])
        ch = ch.replace("@", "")
        await event.edit(f"حسناً سيتم بدء التثبيت في**-  @{ch} .**")
    except:
        try:
            ch = await client(
                functions.channels.CreateChannelRequest(
                    title="ABOOD HUNTER - تثبيت عبود",
                    about="This channel to hunt username by - @SSSTlF",
                )
            )
            ch = ch.updates[1].channel_id
            await event.edit(f"**- تم بنجاح بدأ التثبيت**")
        except Exception as e:
            await client.send_message(
                event.chat_id, f"خطأ في انشاء القناة , الخطأ : {str(e)}"
            )
    isauto.clear()
    isauto.append("on")
    username = str(msg[1])
    swapmod = True
    while swapmod:
        isav = check_user(username)
        if isav == True:
            try:
                await client(
                    functions.channels.UpdateUsernameRequest(
                        channel=ch, username=username
                    )
                )
                await event.client.send_file(
                    ch,
                    "https://t.me/Repthongif/2",
                    caption="🐊 سورس عبود 🐊\n- - - - - - - - - - - - - - - - - - - - - - - -\n- UserName: ❲ @{} ❳\n- ClickS: ❲ {} ❳\n- Save: ❲ Chaneel ❳\n- - - - - - - - - - - - - - - - - - - - - - - -\nسورس عبود ❲ @SSSTlF ❳ ".format(
                        username, trys2
                    ),
                )
                await event.client.send_file(
                    event.chat_id,
                    "https://t.me/Repthongif/2",
                    caption="🐊 سورس عبود 🐊\n- - - - - - - - - - - - - - - - - - - - - - - -\n- UserName: ❲ @{} ❳\n- ClickS: ❲ {} ❳\n- Save: ❲ Chaneel ❳\n- - - - - - - - - - - - - - - - - - - - - - - -\nسورس عبود ❲ @SSSTlF ❳ ".format(
                        username, trys2
                    ),
                )
                swapmod = False
                break
            except telethon.errors.rpcerrorlist.UsernameInvalidError:
                await event.client.send_message(
                    event.chat_id, f"المعرف **-  @{username} غير صالح . **"
                )
                swapmod = False
                break
            except telethon.errors.FloodError as e:
                await client.send_message(
                    event.chat_id, f"للاسف تبندت , مدة الباند ({e.seconds}) ثانية ."
                )
                swapmod = False
                break
            except Exception as eee:
                await client.send_message(
                    event.chat_id,
                    f"""خطأ مع {username} , الخطأ :{str(eee)}""",
                )
                swapmod = False
                break
        else:
            pass
        trys2[0] += 1
    isauto.clear()
    isauto.append("off")

@client.on(events.NewMessage(pattern=r'^\.ايقاف الصيد$'))
async def _(event):
    if "on" in isclaim:
        isclaim.clear()
        isclaim.append("off")
        return await event.edit("**- تم بنجاح ايقاف عملية الصيد**")
    elif "off" in isclaim:
        return await event.edit("**- لم يتم تفعيل الصيد بالأصل لأيقافه**")
    else:
        return await event.edit("**- لقد حدث خطأ ما وتوقف الامر لديك**")

@client.on(events.NewMessage(pattern=r'^\.ايقاف التثبيت$'))
async def _(event):
    if "on" in isauto:
        isauto.clear()
        isauto.append("off")
        return await event.edit("**- تم بنجاح ايقاف عملية التثبيت**")
    elif "off" in isauto:
        return await event.edit("**- لم يتم تفعيل التثبيت بالأصل لأيقافه**")
    else:
        return await event.edit("**-لقد حدث خطأ ما وتوقف الامر لديك**")

@client.on(events.NewMessage(pattern=r'^\.حالة الصيد$'))
async def _(event):
    if "on" in isclaim:
        await event.edit(f"**- الصيد وصل لـ({trys[0]}) **من المحاولات")
    elif "off" in isclaim:
        await event.edit("**- الصيد بالاصل لا يعمل .**")
    else:
        await event.edit("- لقد حدث خطأ ما وتوقف الامر لديك")

@client.on(events.NewMessage(pattern=r'^\.حالة التثبيت$'))
async def _(event):
    if "on" in isauto:
        await event.edit(f"**- التثبيت وصل لـ({trys2[0]}) من المحاولات**")
    elif "off" in isauto:
        await event.edit("**- التثبيت بالاصل لا يعمل .**")
    else:
        await event.edit("-لقد حدث خطأ ما وتوقف الامر لديك")

# ================================================================
#                   أوامر الذاتية (Self Media Commands)
# ================================================================

repself = True

BaqirSelf_cmd = (
    "سورس عبود @SSSTlF - حفظ الذاتيه 🧧\n\n"
    "**⪼** `.تفعيل الذاتيه`\n"
    "**لـ تفعيـل الحفظ التلقائي للذاتيـه**\n"
    "**سوف يقوم حسابك بحفظ الذاتيه تلقائياً في حافظة حسابك عندما يرسل لك اي شخص ميديـا ذاتيـه**\n\n"
    "**⪼** `.تعطيل الذاتيه`\n"
    "**لـ تعطيـل الحفظ التلقائي للذاتيـه**\n\n"
    "**⪼** `.ذاتيه`\n"
    "**بالـرد ؏ــلى صـوره ذاتيـه لحفظهـا في حال كان امر الحفظ التلقائي معطـل**\n\n\n"
    "**⪼** `.اعلان`\n"
    "**الامـر + الوقت بالدقائق + الرسـاله**\n"
    "**امـر مفيـد لجماعـة التمويـل لـ عمـل إعـلان مـؤقت بالقنـوات**\n\n"
    "\n**سورس عبود** @SSSTlF"
)

@client.on(events.NewMessage(pattern=r'^\.الذاتيه$'))
async def cmd(baqir):
    await edit_or_reply(baqir, BaqirSelf_cmd)

@client.on(events.NewMessage(pattern=r'^\.ذاتيه(?: |$)(.*)'))
async def oho(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة ذاتيـة التدميـر**...")
    e_7_v = await event.get_reply_message()
    pic = await e_7_v.download_media()
    await client.send_file("me", pic, caption=f"**⎉╎تم حفـظ الصـورة الذاتيـه .. بنجـاح ☑️**")
    await event.delete()

@client.on(events.NewMessage(pattern=r'^\.تفعيل الذاتيه$'))
async def start_datea(event):
    global repself
    if repself:
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. مفعـله مسبقـاً ☑️**")
    repself = True
    await edit_or_reply(event, "**⎉╎تم تفعيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")

@client.on(events.NewMessage(pattern=r'^\.تعطيل الذاتيه$'))
async def stop_datea(event):
    global repself
    if repself:
        repself = False
        return await edit_or_reply(event, "**⎉╎تم تعطيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")
    await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. معطلـه مسبقـاً ☑️**")

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
        await client.send_file("me", pic, caption=f"**سورس عبود** @SSSTlF - حفظ الذاتيه 🧧 .\n\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n**⌔╎مࢪحبـاً عـزيـزي المـالك 🫂\n⌔╎ تـم حفـظ الذاتيـة تلقائيـاً .. بنجـاح ☑️** ❝\n**⌔╎المـرسـل** [{sender.first_name}](tg://user?id={sender.id}) .")

# ================================================================
#                   أوامر الإعلان (Announcement Commands)
# ================================================================

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
    text = message + f"\n\n**- هذا الاعلان سيتم حذفه تلقـائيـاً بعـد {baqir} دقائـق ⏳**"
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, text)
    await asyncio.sleep(baqir)
    await smsg.delete()

# ================================================================
#                   أمر الكاشف (Phone Info Command)
# ================================================================

BaqirPH_cmd = (
    "سورس عبود @SSSTlF - كاشف الارقام العربية 📲\n\n"
    "**⪼ الامــر ↵**\n\n"
    "⪼ `.كاشف` + اسـم الدولـة + الـرقـم بـدون مفتـاح الـدولة\n\n"
    "**⪼ الوصـف :**\n"
    "**- لجـلب معلـومـات عـن رقـم هـاتف معيـن**\n\n"
    "**⪼ مثـال :**\n\n"
    "`.كاشف اليمن 777887798` \n\n"
    "`.كاشف السعوديه 555542317` \n\n"
    "`.كاشف الامارات 43171234` \n\n"
    "**الامـر يدعـم الـدول التـاليـة ↵** 🇾🇪🇸🇦🇦🇪🇰🇼🇶🇦🇧🇭🇴🇲 \n\n"
    "🛃 سيتـم اضـافة المزيـد من الدول قريبـاً\n\n"
    "\n**سورس عبود** @SSSTlF"
)

@client.on(events.NewMessage(pattern=r'^\.الكاشف$'))
async def cmd(baqir):
    await edit_or_reply(baqir, BaqirPH_cmd)

@client.on(events.NewMessage(pattern=r'^\.كاشف ?(.*)'))
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id and not event.pattern_match.group(1):
        reply_to_id = await event.get_reply_message()
        reply_to_id = str(reply_to_id.message)
    else:
        reply_to_id = str(event.pattern_match.group(1))
    if not reply_to_id:
        return await edit_or_reply(
            event, "**╮ . كـاشف الاࢪقـام الـ؏ـࢪبيـة 📲.. اࢪسـل** `.الكاشف` **للتعليـمات**"
        )
    chat = "@Zelzalybot"
    zzzzl1l = await edit_or_reply(event, "**╮•⎚ جـارِ الكـشف ؏ــن الـرقـم  📲 ⌭ . . .**")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=1194140165)
            )
            await event.client.send_message(chat, "{}".format(input_str))
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await zzzzl1l.edit("**╮•⎚ تحـقق من انـك لم تقـم بحظر البوت @Zelzalybot .. ثم اعـد استخدام الامـر ...🤖♥️**")
            return
        if response.text.startswith("I can't find that"):
            await zzzzl1l.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")
        else:
            await zzzzl1l.delete()
            await event.client.send_message(event.chat_id, response.message)

# ================================================================
#                   مرشح الرسائل (Message Filter)
# ================================================================

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

# ================================================================
#                   معالج الوقت (Time Handler)
# ================================================================

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

# ================================================================
#                   أوامر التكرار (Spam Commands)
# ================================================================

# المتغيرات العامة للتكرار
spam_running = {}

@client.on(events.NewMessage(pattern=r'^\.سبام (\d+) ([\s\S]+)$'))
async def spam_command(event):
    """أمر السبام لتكرار إرسال رسالة عدد محدد من المرات"""
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
    """أمر المكرر مع وقت بين الإرسالات"""
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
    """إيقاف أمر المكرر"""
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
    """أمر تفصيخ الجملة حرفاً حرفاً"""
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

# ================================================================
#                   خادم الويب (Web Server)
# ================================================================

async def run_web_server():
    """تشغيل خادم ويب بسيط لـ Render"""
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
        
        # نبقى الخادم شغالاً للأبد
        await asyncio.Event().wait()
        
    except ImportError:
        print("⚠️ aiohttp غير مثبت - خادم الويب معطل")
    except Exception as e:
        print(f"⚠️ خطأ في تشغيل خادم الويب: {e}")

# ================================================================
#                   التشغيل الرئيسي (Main)
# ================================================================

async def main():
    try:
        print("🚀 جاري تشغيل البوت...")
        print("✧ سورس عبود ✧ @SSSTlF")
        
        # بدء التشغيل بالجلسة
        if not await start_client():
            print("⏳ انتظر إرسال الجلسة...")
            await client.run_until_disconnected()
            return
        
        print(f"✅ البوت يعمل الآن كـ: {(await client.get_me()).first_name}")
        print(f"📁 ملف الإعدادات: {CONFIG_FILE}")
        
        # تشغيل حلقة keep_alive في الخلفية
        asyncio.create_task(keep_alive())
        
        # تشغيل خادم الويب
        asyncio.create_task(run_web_server())
        
        print("✅ البوت جاهز لاستقبال الأوامر")
        print("✧ سورس عبود ✧ @SSSTlF")
        
        # استمرار التشغيل
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 محاولة إعادة التشغيل بعد 5 ثواني...")
        await asyncio.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)
