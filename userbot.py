# -*- coding: utf-8 -*-
import asyncio
import os
import random
import re
import json
import sys
import subprocess
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto, ChatBannedRights
from telethon.errors import FloodWaitError, PhoneNumberInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditBannedRequest

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
BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True
)

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

# ========== مرشح الرسائل للحماية ==========
@client.on(events.NewMessage(incoming=True))
async def protection_filter(event):
    if event.is_private:
        return
    
    chat_id = event.chat_id
    sender = await event.get_sender()
    
    # تجاهل رسائل المالك والمشرفين
    if sender.id == (await client.get_me()).id:
        return
    
    # تجاهل المشرفين
    try:
        permissions = await client.get_permissions(chat_id, sender.id)
        if permissions.is_admin or permissions.is_creator:
            return
    except:
        pass
    
    text = event.raw_text
    
    # فحص الفشار (كلمات بذيئة)
    if is_locked(chat_id, "badwords"):
        bad_words = ["خرا", "كسها", "كسمك", "كسختك", "عيري", "طيز", "سكس", "نيك", "زب", "اير", "خول", "عرص"]
        if any(word in text for word in bad_words):
            try:
                await event.delete()
                await event.reply(f"⚠️ @{sender.username or sender.id} ممنوع الألفاظ البذيئة!")
            except:
                pass
    
    # فحص الروابط
    if is_locked(chat_id, "links"):
        if "http" in text or "www." in text:
            try:
                await event.delete()
                await event.reply(f"⚠️ @{sender.username or sender.id} ممنوع إرسال الروابط!")
            except:
                pass

# ========== معالج التنصيب التلقائي ==========
@client.on(events.NewMessage(pattern=r'^\.تنصيب$'))
async def install_bot(event):
    global install_waiting, install_user_id, install_step
    
    if not await is_owner(event):
        await event.reply("❌ هذا الأمر فقط لصاحب الحساب")
        return
    
    try:
        install_waiting = True
        install_user_id = event.sender_id
        install_step = "phone"
        
        await event.reply("""
📥 **أمر التنصيب التلقائي**

📌 أرسل الآن رقم هاتفك مع مفتاح الدولة
📱 مثال: `+9665XXXXXXXX`

✧ سورس عبود ✧
""")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")
        install_waiting = False

@client.on(events.NewMessage(incoming=True))
async def handle_install_input(event):
    global install_waiting, install_user_id, install_phone, install_client, install_step, install_hash

    if not install_waiting or event.sender_id != install_user_id or event.text.startswith('.'):
        return

    try:
        if install_step == "phone":
            phone = event.text.strip()
            install_phone = phone
            install_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await install_client.connect()
            
            try:
                result = await install_client.send_code_request(phone)
                install_hash = result.phone_code_hash
                await event.reply(f"📱 تم استقبال الرقم: `{phone}`\n⏳ أرسل رمز التحقق الآن")
                install_step = "code"
            except Exception as e:
                await event.reply(f"❌ خطأ: {str(e)}")
                install_waiting = False

        elif install_step == "code":
            code = event.text.strip()
            try:
                await install_client.sign_in(phone=install_phone, code=code, phone_code_hash=install_hash)
                me = await install_client.get_me()
                new_session = install_client.session.save()
                CONFIG["session_string"] = new_session
                save_config()
                await event.reply(f"✅ تم التنصيب بنجاح!\n📋 المعرف: `{me.id}`")
                await install_client.disconnect()
                await client.disconnect()
                subprocess.Popen([sys.executable, __file__])
                sys.exit(0)
            except SessionPasswordNeededError:
                await event.reply("🔐 مطلوب كلمة مرور الخطوتين، أرسلها الآن")
                install_step = "password"
            except Exception as e:
                await event.reply(f"❌ خطأ: {str(e)}")
                install_waiting = False

        elif install_step == "password":
            password = event.text.strip()
            try:
                await install_client.sign_in(password=password)
                me = await install_client.get_me()
                new_session = install_client.session.save()
                CONFIG["session_string"] = new_session
                save_config()
                await event.reply(f"✅ تم التنصيب بنجاح!\n📋 المعرف: `{me.id}`")
                await install_client.disconnect()
                await client.disconnect()
                subprocess.Popen([sys.executable, __file__])
                sys.exit(0)
            except Exception as e:
                await event.reply(f"❌ كلمة المرور غير صحيحة: {str(e)}")

    except Exception as e:
        await event.reply(f"❌ خطأ عام: {str(e)}")
        install_waiting = False

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

@client.on(events.NewMessage(pattern=r'^\.ايدي$'))
async def get_id(event):
    try:
        sender = await event.get_sender()
        sender_id = sender.id
        sender_name = sender.first_name or "لا يوجد"
        sender_username = f"@{sender.username}" if sender.username else "لا يوجد يوزر"
        chat_id = event.chat_id
        now = get_saudi_time()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        text = f"""
✧ معرف الايدي ✧

👤 ايديك : {sender_id}
📛 اسمك : {sender_name}
🆔 يوزرك : {sender_username}
💬 ايدي المحادثة : {chat_id}

⏰ التاريخ : {date_str}
📍 المنطقة : السعودية - الرياض

✧ سورس عبود ✧"""
        photos = await client.get_profile_photos(sender)
        if photos:
            await event.reply(text, file=photos[0])
        else:
            await event.reply(text)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'^\.ايديي$'))
async def my_id_command(event):
    """عرض الايدي الخاص بك"""
    if not await is_owner(event):
        return
    me = await client.get_me()
    await event.reply(f"📋 ايديك: `{me.id}`")

@client.on(events.NewMessage(pattern=r'^\.اسمي$'))
async def my_name_command(event):
    """عرض اسمك"""
    if not await is_owner(event):
        return
    me = await client.get_me()
    await event.reply(f"📛 اسمك: {me.first_name} {me.last_name or ''}")

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

# ========== أوامر التسلية ==========
@client.on(events.NewMessage(pattern=r'^\.نسبه الحب(?: (.+))?$'))
async def love_percent(event):
    """نسبة الحب بين شخصين"""
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

# ========== أمر عرض الأوامر ==========
@client.on(events.NewMessage(pattern=r'^\.الاوامر$'))
async def show_commands(event):
    """عرض جميع الأوامر المتاحة"""
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

**📥 أوامر التحميل:**
◙ `.تحميل صوتي <رابط>` - تحميل صوت
◙ `.تحميل فيد <رابط>` - تحميل فيديو
◙ `.صوتي <عنوان>` - تحميل صوت بالبحث

**📋 أوامر المعلومات:**
◙ `.ا` - معلومات حسابك
◙ `.المطور` - معلومات المطور
◙ `.ايدي` - معرفك ومعلومات المحادثة
◙ `.ايديي` - عرض ايديك فقط
◙ `.اسمي` - عرض اسمك

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
◙ `.الاوامر` - عرض هذه القائمة

✧ **سورس عبود** ✧
"""
    await event.reply(commands_text)

@client.on(events.NewMessage(pattern=r'^\.مساعده$'))
async def help_command(event):
    """عرض قائمة المساعدة التفصيلية"""
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

**📥 أوامر التحميل:**
◙ `.تحميل صوتي <رابط>` - تحميل صوت من رابط
◙ `.تحميل فيد <رابط>` - تحميل فيديو من رابط
◙ `.صوتي <عنوان>` - تحميل صوت بالبحث

**📋 أوامر المعلومات:**
◙ `.ا` - عرض معلومات حسابك
◙ `.المطور` - عرض معلومات المطور
◙ `.ايدي` - عرض معرفك ومعلومات المحادثة

**🔍 أوامر البحث:**
◙ `.بحث <نص>` - البحث في جوجل
◙ `.فيديو <اسم>` - البحث عن فيديو
◙ `.اغنية <اسم>` - البحث عن أغنية

**📖 أوامر أخرى:**
◙ `.كت` - عرض حكمة عشوائية
◙ `.تنصيب` - تنصيب البوت تلقائياً
◙ `.الاوامر` - عرض هذه القائمة

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
