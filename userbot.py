# -*- coding: utf-8 -*-
import asyncio
import os
import random
import re
import json
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto
from telethon.errors import FloodWaitError
from telethon.tl.functions.account import UpdateProfileRequest

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION:
    raise Exception("❌ تأكد من تعيين API_ID, API_HASH, SESSION_STRING في المتغيرات")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ========== متغيرات الوقت ==========
time_enabled = False  # تفعيل الوقت بشكل افتراضي
# توقيت السعودية (UTC+3)
SAUDI_OFFSET = timedelta(hours=3)

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

# ========== دالة الحصول على الوقت بتوقيت السعودية ==========
def get_saudi_time():
    # الحصول على الوقت الحالي بتوقيت UTC وإضافة 3 ساعات (توقيت السعودية)
    utc_now = datetime.utcnow()
    saudi_time = utc_now + SAUDI_OFFSET
    return saudi_time

# ========== دالة التحقق من صاحب الجلسة ==========
async def is_owner(event):
    me = await event.client.get_me()
    sender = await event.get_sender()
    return sender.id == me.id

# ========== دالة تحديث الاسم ==========
async def update_name(first_name, last_name=None):
    try:
        # استخدام UpdateProfileRequest لتحديث الاسم
        request = UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name or ""
        )
        await client(request)
        return True
    except Exception as e:
        print(f"❌ خطأ في تحديث الاسم: {e}")
        return False

# ========== معالج الرسائل لإضافة الوقت ==========
@client.on(events.NewMessage(outgoing=True))
async def add_time_to_message(event):
    global time_enabled
    
    # التأكد من أن الرسالة مرسلة من الحساب نفسه
    if not event.out:
        return
    
    # التحقق من تفعيل الوقت
    if not time_enabled:
        return
    
    # الحصول على الوقت الحالي بتوقيت السعودية
    now = get_saudi_time()
    time_str = now.strftime("%I:%M %p")  # 12-hour format with AM/PM
    
    # تعديل اسم المستخدم لإضافة الوقت
    try:
        me = await client.get_me()
        first_name = me.first_name or ""
        last_name = me.last_name or ""
        
        # إزالة الوقت القديم إذا موجود
        name_parts = first_name.split(' ⌚')
        clean_name = name_parts[0]
        
        # الاسم الجديد مع الوقت
        new_name = f"{clean_name} ⌚ {time_str}"
        
        # تغيير الاسم الأول فقط (بدون تغيير الاسم الأخير)
        await update_name(new_name, last_name)
        
    except Exception as e:
        print(f"❌ خطأ في تحديث الاسم: {e}")

# ========== أمر .تفعيل الوقت ==========
@client.on(events.NewMessage(pattern=r'^\.تفعيل الوقت$'))
async def enable_time(event):
    global time_enabled
    
    if not await is_owner(event):
        await event.reply("❌ هذا الأمر فقط لصاحب الحساب")
        return
    
    try:
        time_enabled = True
        
        # الحصول على الوقت الحالي
        now = get_saudi_time()
        time_str = now.strftime("%I:%M %p")
        
        # تحديث الاسم فوراً
        me = await client.get_me()
        first_name = me.first_name or ""
        last_name = me.last_name or ""
        
        # إزالة الوقت القديم إذا موجود
        name_parts = first_name.split(' ⌚')
        clean_name = name_parts[0]
        
        # الاسم الجديد مع الوقت
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

# ========== أمر .تعطيل الوقت ==========
@client.on(events.NewMessage(pattern=r'^\.تعطيل الوقت$'))
async def disable_time(event):
    global time_enabled
    
    if not await is_owner(event):
        await event.reply("❌ هذا الأمر فقط لصاحب الحساب")
        return
    
    try:
        time_enabled = False
        
        # إزالة الوقت من الاسم
        me = await client.get_me()
        first_name = me.first_name or ""
        last_name = me.last_name or ""
        
        # إزالة الوقت من الاسم
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

# ========== أمر .ا (معلومات الحساب) - لصاحب الجلسة فقط ==========
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
            
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .المطور - لصاحب الجلسة فقط ==========
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
            
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .ايدي - يظهر إيدي الشخص الذي كتب الأمر ==========
@client.on(events.NewMessage(pattern=r'^\.ايدي$'))
async def get_id(event):
    try:
        sender = await event.get_sender()
        sender_id = sender.id
        sender_name = sender.first_name or "لا يوجد"
        sender_username = f"@{sender.username}" if sender.username else "لا يوجد يوزر"
        
        me = await client.get_me()
        owner_id = me.id
        
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
            
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .بحث - لصاحب الجلسة فقط ==========
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
        
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .فيديو - لصاحب الجلسة فقط ==========
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
        
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .اغنية - لصاحب الجلسة فقط ==========
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
        
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .كت - لصاحب الجلسة فقط ==========
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
        
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== خادم ويب وهمي ==========
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
    print(f"✅ خادم الويب الوهمي يعمل على المنفذ {port}")
    
    await asyncio.Event().wait()

# ========== تشغيل البوت ==========
async def main():
    await client.start()
    print("✅ البوت يعمل الآن...")
    await run_web_server()

if __name__ == "__main__":
    asyncio.run(main())
