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
from telethon.tl.types import MessageMediaPhoto
from telethon.errors import FloodWaitError, PhoneNumberInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError
from telethon.tl.functions.account import UpdateProfileRequest

# ========== إعدادات التحميل ==========
try:
    from .. import download_yt, get_yt_link, is_url_work, Tepthon_cmd
except ImportError:
    # تعريف دوال مؤقتة في حالة عدم وجود المكتبات
    async def download_yt(jmbot, url, ytd):
        await jmbot.eor("⚠️ مكتبة التحميل غير مثبتة")
    
    def get_yt_link(query, ytd):
        return None
    
    async def is_url_work(url):
        return True
    
    def Tepthon_cmd(pattern):
        return lambda func: func

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION:
    raise Exception("❌ تأكد من تعيين API_ID, API_HASH, SESSION_STRING في المتغيرات")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ========== متغيرات الوقت ==========
time_enabled = False
SAUDI_OFFSET = timedelta(hours=3)
install_waiting = False
install_user_id = None
install_phone = None
install_client = None
install_step = "phone"
install_hash = None
install_password = None

# ========== إعدادات تحميل اليوتيوب ==========
ytd = {
    "prefer_ffmpeg": True,
    "addmetadata": True,
    "geo-bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [{"key": "FFmpegMetadata"}],
}

# ========== قائمة الحكم والكلمات ==========
QUOTES = [
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
]

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
    """تحميل ملف صوتي من رابط"""
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
        await download_yt(event, url, ytd_copy)
    except Exception as e:
        await event.reply(f"❌ خطأ في التحميل: {str(e)}")

async def download_video(event, url):
    """تحميل فيديو من رابط"""
    ytd_copy = ytd.copy()
    ytd_copy["format"] = "best"
    ytd_copy["outtmpl"] = "%(id)s.mp4"
    ytd_copy["postprocessors"] = [
        {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        {"key": "FFmpegMetadata"}
    ]
    
    try:
        await download_yt(event, url, ytd_copy)
    except Exception as e:
        await event.reply(f"❌ خطأ في التحميل: {str(e)}")

# ========== أوامر التحميل الجديدة ==========
@client.on(events.NewMessage(pattern=r'^\.تحميل صوتي (.+)$'))
async def download_audio_command(event):
    """تحميل صوتي من رابط"""
    if not await is_owner(event):
        return
    
    url = event.pattern_match.group(1).strip()
    if not url:
        await event.reply("❌ يجب عليك وضع رابط للتحميل الصوتي")
        return
    
    try:
        await is_url_work(url)
    except Exception:
        await event.reply("❌ الرابط غير صحيح أو لا يعمل")
        return
    
    await event.reply("🎵 جاري تحميل الملف الصوتي...")
    await download_audio(event, url)

@client.on(events.NewMessage(pattern=r'^\.تحميل فيد (.+)$'))
async def download_video_command(event):
    """تحميل فيديو من رابط"""
    if not await is_owner(event):
        return
    
    url = event.pattern_match.group(1).strip()
    if not url:
        await event.reply("❌ يجب عليك وضع رابط لتحميل الفيديو")
        return
    
    try:
        await is_url_work(url)
    except Exception:
        await event.reply("❌ الرابط غير صحيح أو لا يعمل")
        return
    
    await event.reply("🎬 جاري تحميل الفيديو...")
    await download_video(event, url)

@client.on(events.NewMessage(pattern=r'^\.صوتي(?: (.+))?$'))
async def search_audio_command(event):
    """تحميل صوتي بالبحث عن عنوان"""
    if not await is_owner(event):
        return
    
    query = event.pattern_match.group(1) if event.pattern_match.group(1) else None
    if not query:
        await event.reply("❌ يجب عليك تحديد ما تريد تحميله، اكتب عنوان مع الأمر")
        return
    
    await event.reply(f"🎵 جاري البحث عن: **{query}**...")
    
    try:
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
        
        url = get_yt_link(query, ytd_copy)
        if not url:
            await event.reply("❌ لم يتم العثور على الفيديو، اكتب عنوان مفصل بشكل صحيح")
            return
        
        await event.reply("🎵 جاري تحميل الملف الصوتي...")
        await download_yt(event, url, ytd_copy)
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر المساعدة مع الأوامر الجديدة ==========
@client.on(events.NewMessage(pattern=r'^\.الاوامر$'))
async def help_command(event):
    """عرض جميع الأوامر المتاحة"""
    if not await is_owner(event):
        return
    
    help_text = """
✧ **قائمة الأوامر** ✧

**⏰ أوامر الوقت:**
◙ `.تفعيل الوقت` - تفعيل عرض الوقت في الاسم
◙ `.تعطيل الوقت` - تعطيل عرض الوقت في الاسم

**📥 أوامر التحميل:**
◙ `.تحميل صوتي` <رابط> - تحميل صوت من رابط يوتيوب أو أي منصة
◙ `.تحميل فيد` <رابط> - تحميل فيديو من رابط يوتيوب أو أي منصة
◙ `.صوتي` <عنوان> - تحميل صوت بالبحث عن العنوان

**📋 أوامر المعلومات:**
◙ `.ا` - عرض معلومات حسابك
◙ `.المطور` - عرض معلومات المطور
◙ `.ايدي` - عرض معرفك ومعلومات المحادثة

**🔍 أوامر البحث:**
◙ `.بحث` <نص> - البحث في جوجل
◙ `.فيديو` <اسم> - البحث عن فيديو في يوتيوب
◙ `.اغنية` <اسم> - البحث عن أغنية في يوتيوب

**📖 أوامر أخرى:**
◙ `.كت` - عرض حكمة عشوائية
◙ `.تنصيب` - تنصيب البوت تلقائياً

✧ سورس عبود ✧
"""
    await event.reply(help_text)

# ========== معالج الرسائل ==========
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

# ========== معالج التنصيب التلقائي ==========
@client.on(events.NewMessage(incoming=True))
async def handle_install_input(event):
    global install_waiting, install_user_id, install_phone, install_client, install_step, install_hash, install_password

    if not install_waiting:
        return

    if event.sender_id != install_user_id:
        return

    if event.text.startswith('.'):
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
                
                await event.reply(f"""
📱 **تم استقبال الرقم بنجاح!**

📞 الرقم: `{phone}`
🔑 جاري إرسال رمز التحقق...

⏳ انتظر وصول الرمز ثم أرسله هنا
✧ سورس عبود ✧
""")
                install_step = "code"

            except PhoneNumberInvalidError:
                await event.reply("❌ رقم الهاتف غير صحيح! تأكد من كتابته مع مفتاح الدولة\nمثال: +9665XXXXXXXX")
                install_waiting = False
                install_step = "phone"
                await install_client.disconnect()
            except FloodWaitError as e:
                await event.reply(f"⏳ انتظر {e.seconds} ثانية قبل المحاولة مرة أخرى")
                install_waiting = False
                install_step = "phone"
                await install_client.disconnect()

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
                
                await event.reply(f"""
✅ **تم التنصيب بنجاح!**

📋 المعرف: `{me_new.id}`
📛 الاسم: {me_new.first_name}
🆔 اليوزر: @{me_new.username if me_new.username else 'لا يوجد'}

🔄 جاري حفظ الجلسة وإعادة التشغيل...
✧ سورس عبود ✧
""")

                with open("session.string", "w") as f:
                    f.write(new_session)
                
                os.environ["SESSION_STRING"] = new_session
                
                await install_client.disconnect()
                await client.disconnect()
                
                subprocess.Popen([sys.executable, __file__])
                sys.exit(0)

            except SessionPasswordNeededError:
                await event.reply("""
🔐 **مطلوب كلمة مرور الخطوتين!**

📌 أرسل الآن كلمة المرور الخاصة بحسابك
⚠️ سيتم استخدامها لتسجيل الدخول
✧ سورس عبود ✧
""")
                install_step = "password"
                
            except PhoneCodeInvalidError:
                await event.reply("❌ رمز التحقق غير صحيح! أعد المحاولة")
            except FloodWaitError as e:
                await event.reply(f"⏳ انتظر {e.seconds} ثانية قبل المحاولة مرة أخرى")
            except Exception as e:
                await event.reply(f"❌ خطأ: {str(e)}\n\n📌 أعد المحاولة باستخدام `.تنصيب`")
                install_waiting = False
                install_step = "phone"
                await install_client.disconnect()

        elif install_step == "password":
            password = event.text.strip()
            
            try:
                await install_client.sign_in(password=password)
                
                me_new = await install_client.get_me()
                new_session = install_client.session.save()
                
                await event.reply(f"""
✅ **تم التنصيب بنجاح!**

📋 المعرف: `{me_new.id}`
📛 الاسم: {me_new.first_name}
🆔 اليوزر: @{me_new.username if me_new.username else 'لا يوجد'}

🔄 جاري حفظ الجلسة وإعادة التشغيل...
✧ سورس عبود ✧
""")

                with open("session.string", "w") as f:
                    f.write(new_session)
                
                os.environ["SESSION_STRING"] = new_session
                
                await install_client.disconnect()
                await client.disconnect()
                
                subprocess.Popen([sys.executable, __file__])
                sys.exit(0)

            except Exception as e:
                await event.reply(f"❌ كلمة المرور غير صحيحة!\nالخطأ: {str(e)}\n\n📌 أعد المحاولة")
                install_step = "password"

    except Exception as e:
        await event.reply(f"❌ خطأ عام: {str(e)}")
        install_waiting = False
        install_step = "phone"

# ========== أمر التنصيب ==========
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
📱 مثال: `+201270270609`

⚠️ **تنبيه:**
• سيتم إرسال رمز التحقق تلقائياً
• بعد استلام الرمز، أرسله هنا
• إذا كان الحساب مفعل بخطوتين ستحتاج لإرسال كلمة المرور

✧ سورس عبود ✧
""")
        
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")
        install_waiting = False
        install_step = "phone"
        install_user_id = None

# ========== أوامر الوقت ==========
@client.on(events.NewMessage(pattern=r'^\.تفعيل الوقت$'))
async def enable_time(event):
    global time_enabled
    if not await is_owner(event):
        await event.reply("❌ هذا الأمر فقط لصاحب الحساب")
        return
    try:
        time_enabled = True
        now = get_saudi_time()
        time_str = now.strftime("%I:%M %p")
        me = await client.get_me()
        first_name = me.first_name or ""
        last_name = me.last_name or ""
        name_parts = first_name.split(' ⌚')
        clean_name = name_parts[0]
        new_name = f"{clean_name} ⌚ {time_str}"
        await update_name(new_name, last_name)
        await event.reply(f"""
✅ **تم تفعيل عرض الوقت**

🕐 الوقت الحالي: {time_str}
📍 المنطقة: السعودية - الرياض
👤 سيظهر الوقت بجانب اسمك

✧ سورس عبود ✧
""")
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
        me = await client.get_me()
        first_name = me.first_name or ""
        last_name = me.last_name or ""
        name_parts = first_name.split(' ⌚')
        clean_name = name_parts[0]
        await update_name(clean_name, last_name)
        await event.reply(f"""
✅ **تم تعطيل عرض الوقت**

🕐 تم إزالة الوقت من اسمك
📍 المنطقة: السعودية - الرياض

✧ سورس عبود ✧
""")
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
        photos = await client.get_profile_photos(me)
        text = f"""
✧ معلومات الحساب ✧

📋 المعرف : {user_id}
📛 الاسم : {first_name} {last_name}
🆔 اليوزر : {username}

📅 التاريخ : {date_str}
📍 المنطقة : السعودية - الرياض
👨‍💻 المطور : @SSSTlF

✧ سورس عبود ✧"""
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
        photos = await client.get_profile_photos(me)
        text = f"""
✧ مطور السورس ✧

👨‍💻 الاسم : عبود
🆔 الايدي : {user_id}
🏷️ اللقب : {first_name}

📢 القناة : @SSSTlF
💎 المنصب : مطور السورس
🌟 الحالة : الحمد لله

✧ سورس عبود ✧"""
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
        photos = await client.get_profile_photos(sender)
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
👨‍💻 المطور : @SSSTlF

✧ سورس عبود ✧"""
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
    asyncio.create_task(keep_alive())
    await run_web_server()

if __name__ == "__main__":
    asyncio.run(main())
