# -*- coding: utf-8 -*-
import asyncio
import os
import random
import re
import json
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto
from telethon.errors import FloodWaitError

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION:
    raise Exception("❌ تأكد من تعيين API_ID, API_HASH, SESSION_STRING في المتغيرات")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

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

# ========== أمر .ا (معلومات الحساب) ==========
@client.on(events.NewMessage(pattern=r'\.ا'))
async def my_info(event):
    try:
        me = await event.client.get_me()
        user_id = me.id
        first_name = me.first_name or "لا يوجد"
        last_name = me.last_name or ""
        username = f"@{me.username}" if me.username else "لا يوجد يوزر"
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        photos = await event.client.get_profile_photos(me)
        
        text = f"""
✧ معلومات الحساب ✧

📋 المعرف : {user_id}
📛 الاسم : {first_name} {last_name}
🆔 اليوزر : {username}

📅 التاريخ : {date_str}
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

# ========== أمر .المطور (معلومات المطور) - بدون إطار ==========
@client.on(events.NewMessage(pattern=r'\.المطور'))
async def developer_info(event):
    try:
        me = await event.client.get_me()
        user_id = me.id
        first_name = me.first_name or "المطور"
        
        photos = await event.client.get_profile_photos(me)
        
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

# ========== أمر .ايدي (معرف الأيدي) - بدون إطار ==========
@client.on(events.NewMessage(pattern=r'\.ايدي'))
async def get_id(event):
    try:
        me = await event.client.get_me()
        user_id = me.id
        chat_id = event.chat_id
        
        sender = await event.get_sender()
        sender_id = sender.id
        sender_name = sender.first_name or "لا يوجد"
        
        photos = await event.client.get_profile_photos(me)
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        text = f"""
✧ معرف الايدي ✧

👤 ايديك : {user_id}
💬 ايدي المحادثة : {chat_id}
📛 اسم المرسل : {sender_name}
🆔 ايدي المرسل : {sender_id}

⏰ التاريخ : {date_str}
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

# ========== أمر .بحث ==========
@client.on(events.NewMessage(pattern=r'\.بحث (.+)'))
async def search_command(event):
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

# ========== أمر .فيديو ==========
@client.on(events.NewMessage(pattern=r'\.فيديو (.+)'))
async def video_command(event):
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

# ========== أمر .اغنية ==========
@client.on(events.NewMessage(pattern=r'\.اغنية (.+)'))
async def audio_command(event):
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

# ========== أمر .كت ==========
@client.on(events.NewMessage(pattern=r'\.كت'))
async def quote_command(event):
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
