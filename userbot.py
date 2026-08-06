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
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto, ChatBannedRights, ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin, InputPeerUser, MessageEntityMentionName
from telethon.errors import FloodWaitError, PhoneNumberInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError, UserAlreadyParticipantError, UserPrivacyRestrictedError, UserNotMutualContactError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditBannedRequest, InviteToChannelRequest, GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest, GetHistoryRequest, ImportChatInviteRequest as Get
from telethon.tl.functions.phone import CreateGroupCallRequest as startvc
from telethon.tl.functions.phone import DiscardGroupCallRequest as stopvc
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.utils import get_input_location
from requests import get

# ========== تحميل الإعدادات من ملف JSON ==========
CONFIG_FILE = "config.json"

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

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", CONFIG.get("api_id", 0)))
API_HASH = os.environ.get("API_HASH", CONFIG.get("api_hash", ""))
SESSION = os.environ.get("SESSION_STRING", CONFIG.get("session_string", ""))

if not API_ID or not API_HASH or not SESSION:
    raise Exception("❌ تأكد من تعيين API_ID, API_HASH, SESSION_STRING في المتغيرات أو ملف config.json")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ========== متغيرات الوقت ==========
time_enabled = CONFIG.get("time_enabled", False)
SAUDI_OFFSET = timedelta(hours=CONFIG.get("saudi_offset_hours", 3))
install_waiting = False
install_user_id = None
install_phone = None
install_client = None
install_step = "phone"
install_hash = None
install_password = None

# ========== قائمة الحكم والكلمات ==========
QUOTES = CONFIG.get("quotes", [])

# ========== إعدادات تحميل اليوتيوب ==========
ytd = {
    "prefer_ffmpeg": CONFIG["download_settings"].get("prefer_ffmpeg", True),
    "addmetadata": CONFIG["download_settings"].get("addmetadata", True),
    "geo-bypass": CONFIG["download_settings"].get("geo-bypass", True),
    "nocheckcertificate": CONFIG["download_settings"].get("nocheckcertificate", True),
    "postprocessors": [{"key": "FFmpegMetadata"}],
}

# ========== دوال مساعدة ==========
def get_saudi_time():
    utc_now = datetime.utcnow()
    saudi_time = utc_now + SAUDI_OFFSET
    return saudi_time

async def is_owner(event):
    me = await event.client.get_me()
    sender = await event.get_sender()
    return sender.id == me.id

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

# ========== دوال الحماية ==========
BANNED_RIGHTS = ChatBannedRights(until_date=None, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)
UNBAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=False)

def is_locked(chat_id, lock_type):
    locks = CONFIG.get("locks", {})
    chat_locks = locks.get(str(chat_id), {})
    return chat_locks.get(lock_type, False)

def update_lock(chat_id, lock_type, value):
    if "locks" not in CONFIG:
        CONFIG["locks"] = {}
    if str(chat_id) not in CONFIG["locks"]:
        CONFIG["locks"][str(chat_id)] = {}
    CONFIG["locks"][str(chat_id)][lock_type] = value
    save_config()

# ========== دوال الحصول على المستخدم ==========
async def get_user_from_event(event):
    """الحصول على المستخدم من الأمر أو الرد"""
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_object = await event.client.get_entity(previous_message.sender_id)
    else:
        user = event.pattern_match.group(1)
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

# ========== Keep-Alive ==========
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

# ========== دوال التحميل ==========
async def download_audio(event, url):
    ytd_copy = ytd.copy()
    ytd_copy["format"] = "bestaudio"
    ytd_copy["outtmpl"] = "%(id)s.m4a"
    ytd_copy["postprocessors"] = [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "128",
        },
        {"key": "FFmpegMetadata"}
    ]
    try:
        from .. import download_yt, is_url_work
        if not await is_url_work(url):
            await event.reply("❌ الرابط غير صحيح أو لا يعمل")
            return
        await download_yt(event, url, ytd_copy)
    except ImportError:
        await event.reply("⚠️ مكتبة التحميل غير مثبتة\nيرجى تثبيت: pip install yt-dlp")
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
        from .. import download_yt, is_url_work
        if not await is_url_work(url):
            await event.reply("❌ الرابط غير صحيح أو لا يعمل")
            return
        await download_yt(event, url, ytd_copy)
    except ImportError:
        await event.reply("⚠️ مكتبة التحميل غير مثبتة\nيرجى تثبيت: pip install yt-dlp")
    except Exception as e:
        await event.reply(f"❌ خطأ في التحميل: {str(e)}")

async def search_and_download_audio(event, query):
    ytd_copy = ytd.copy()
    ytd_copy["format"] = "bestaudio"
    ytd_copy["outtmpl"] = "%(id)s.m4a"
    ytd_copy["postprocessors"] = [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "128",
        },
        {"key": "FFmpegMetadata"}
    ]
    try:
        from .. import get_yt_link, download_yt
        url = get_yt_link(query, ytd_copy)
        if not url:
            await event.reply("❌ لم يتم العثور على الفيديو، اكتب عنوان مفصل بشكل صحيح")
            return
        await download_yt(event, url, ytd_copy)
    except ImportError:
        await event.reply("⚠️ مكتبة التحميل غير مثبتة\nيرجى تثبيت: pip install yt-dlp")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أوامر التحميل ==========
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

# ========== أوامر الحماية ==========
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
                bots.append(f"• {user.first_name} (`{user.id}`)")
        if bots:
            text = f"🤖 **تم العثور على {len(bots)} بوت:**\n\n" + "\n".join(bots)
            await event.reply(text)
        else:
            await event.reply("✅ لا يوجد بوتات في هذه المجموعة")

# ========== أوامر إضافية من ريبثون ==========
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

✧ سورس عبود ✧
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

# ========== أوامر الايدي الجديدة ==========
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
    
    # التحقق من Spamwatch
    try:
        from repthon import spamwatch
        if spamwatch:
            ban = spamwatch.get_ban(user_id)
            if ban:
                sw = f"**Spamwatch محظور:** `True` \n**السبب:** `{ban.reason}`"
            else:
                sw = f"**Spamwatch محظور:** `False`"
        else:
            sw = "**Spamwatch:** `غير متصل`"
    except:
        sw = "**Spamwatch:** `غير متصل`"
    
    # التحقق من CAS
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
   • {sw}
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

# ========== مرشح الرسائل للحماية ==========
@client.on(events.NewMessage(incoming=True))
async def protection_filter(event):
    if event.is_private:
        return
    
    chat_id = event.chat_id
    sender = await event.get_sender()
    
    if sender.id == (await client.get_me()).id:
        return
    
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

# ========== أوامر الوقت ==========
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

# ========== الأوامر الأخرى ==========
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
        await event.reply(f"🎬 جاري البحث عن فيديو: **{query}**...")
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
        await event.reply(f"🎵 جاري البحث عن أغنية: **{query}**...")
        await asyncio.sleep(1)
        text = f"""
✧ نتيجة الاغنية ✧

🎵 اسم الاغنية : {query}
🔗 رابط الاستماع : [اضغط هنا](https://www.youtube.com/results?search_query={query.replace(' ', '+')}+song)

✧ سورس عبود ✧"""
        await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

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

✧ سورس عبود ✧
""")

@client.on(events.NewMessage(pattern=r'^\.الاوامر$'))
async def show_commands(event):
    if not await is_owner(event):
        return
    
    commands_text = """
✧ **قائمة الأوامر** ✧

**🛡️ أوامر الحماية:**
◙ `.قفل <نوع>` - قفل خاصية
◙ `.فتح <نوع>` - فتح خاصية
◙ `.الحاله` - عرض حالة الحماية
◙ `.البوتات` - كشف البوتات
◙ `.البوتات طرد` - طرد جميع البوتات

**👥 أوامر المجموعة:**
◙ `.تفليش` - حظر جميع الأعضاء
◙ `.تصفير` - طرد جميع الأعضاء
◙ `.الاعضاء` - عرض قائمة الأعضاء
◙ `.المشرفين` - عرض قائمة المشرفين
◙ `.المعلومات` - معلومات المجموعة
◙ `.المحذوفين` - عرض الحسابات المحذوفة
◙ `.المحذوفين تنظيف` - حظر الحسابات المحذوفة
◙ `.مسح المحظورين` - مسح جميع المحظورين
◙ `.غادر` - مغادرة المجموعة
◙ `.تاك <نص>` - تاك جميع الأعضاء

**📥 أوامر التحميل:**
◙ `.تحميل صوتي <رابط>` - تحميل صوت
◙ `.تحميل فيد <رابط>` - تحميل فيديو
◙ `.صوتي <عنوان>` - تحميل صوت بالبحث

**📋 أوامر المعلومات:**
◙ `.ا` - معلومات حسابك
◙ `.ايدي` - معلومات الشخص
◙ `.ايديي` - عرض ايديك فقط
◙ `.اسمي` - عرض اسمك
◙ `.كشف` - معلومات مفصلة عن الشخص
◙ `.id` - عرض الايدي فقط
◙ `.stat` - إحصائيات الحساب
◙ `.رابط الحساب` - رابط حساب الشخص

**🔍 أوامر البحث:**
◙ `.بحث <نص>` - البحث في جوجل
◙ `.فيديو <اسم>` - البحث عن فيديو
◙ `.اغنية <اسم>` - البحث عن أغنية

**⏰ أوامر الوقت:**
◙ `.تفعيل الوقت` - تفعيل عرض الوقت
◙ `.تعطيل الوقت` - تعطيل عرض الوقت

**🎭 أوامر التسلية:**
◙ `.كت` - حكمة عشوائية
◙ `.نسبه الحب <اسم1, اسم2>` - نسبة الحب

**📖 أوامر أخرى:**
◙ `.تنصيب` - تنصيب البوت تلقائياً
◙ `.مساعده` - عرض المساعدة

✧ **سورس عبود** ✧
"""
    await event.reply(commands_text)

@client.on(events.NewMessage(pattern=r'^\.مساعده$'))
async def help_command(event):
    if not await is_owner(event):
        return
    
    help_text = """
✧ **قائمة المساعدة التفصيلية** ✧

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

**📖 أوامر أخرى:**
◙ `.كت` - عرض حكمة عشوائية
◙ `.تنصيب` - تنصيب البوت تلقائياً

✧ سورس عبود ✧
"""
    await event.reply(help_text)

# ========== معالج الوقت ==========
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

# ========== خادم ويب ==========
async def run_web_server():
    from aiohttp import web
    
    async def handle(request):
        return web.Response(text="✅ Userbot is running!")
    
    app = web.Application()
    app.router.add_get('/', handle)
    
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ خادم الويب يعمل على المنفذ {port}")
    
    await asyncio.Event().wait()

# ========== التشغيل الرئيسي ==========
async def main():
    await client.start()
    print("✅ البوت يعمل الآن...")
    print(f"📁 ملف الإعدادات: {CONFIG_FILE}")
    asyncio.create_task(keep_alive())
    await run_web_server()

if __name__ == "__main__":
    asyncio.run(main())
