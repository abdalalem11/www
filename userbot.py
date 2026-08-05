# -*- coding: utf-8 -*-
import asyncio
import os
import random
import re
import json
import aiohttp
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto
from urllib.parse import quote

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION:
    raise Exception("❌ تأكد من تعيين API_ID, API_HASH, SESSION_STRING في المتغيرات")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ========== قائمة الحكم والكلمات ==========
QUOTES = [
    "النجاح ليس نهائياً، والفشل ليس قاتلاً: الشجاعة للاستمرار هي ما يهم.",
    "كن التغيير الذي تريد رؤيته في العالم.",
    "الحياة ليست عن إيجاد الذات، الحياة عن خلق الذات.",
    "المستقبل لأولئك الذين يؤمنون بجمال أحلامهم.",
    "لا تخف من الفشل، اخشَ عدم المحاولة.",
    "أفضل طريقة لبدء المستقبل هي صنعه.",
    "الطريقة الوحيدة للقيام بعمل عظيم هي أن تحب ما تفعله.",
    "لا تضيع وقتك في الحلم بالنجاح، اعمل من أجله.",
    "الصبر مفتاح الفرج، والمثابرة طريق النجاح.",
    "كل يوم هو فرصة جديدة لتغيير حياتك.",
    "العلم نور والجهل ظلام.",
    "من جد وجد، ومن زرع حصد.",
    "خير الناس أنفعهم للناس.",
    "السعادة ليست في المال، بل في القناعة.",
    "التواضع من أخلاق النبلاء."
]

# ========== دالة البحث عن فيديو ==========
async def search_video(query):
    try:
        # استخدام API يوتيوب للبحث
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={quote(query)}&type=video&key=AIzaSyD_mYqO4vLkXKue8eQ0Y6n3dZ_5N5L3X3o&maxResults=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if data.get('items'):
                    video_id = data['items'][0]['id']['videoId']
                    return f"https://www.youtube.com/watch?v={video_id}"
                return None
    except:
        return None

# ========== دالة البحث عن أغنية ==========
async def search_audio(query):
    try:
        # استخدام API يوتيوب للبحث عن أغاني
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={quote(query + ' song audio')}&type=video&key=AIzaSyD_mYqO4vLkXKue8eQ0Y6n3dZ_5N5L3X3o&maxResults=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if data.get('items'):
                    video_id = data['items'][0]['id']['videoId']
                    return f"https://www.youtube.com/watch?v={video_id}"
                return None
    except:
        return None

# ========== أمر .ا ==========
@client.on(events.NewMessage(pattern=r'\.ا'))
async def my_info(event):
    try:
        me = await event.client.get_me()
        user_id = me.id
        first_name = me.first_name or "لا يوجد"
        last_name = me.last_name or ""
        username = f"@{me.username}" if me.username else "لا يوجد يوزر"
        
        photos = await event.client.get_profile_photos(me)
        
        text = f"""**ᯓ  سورس عبود - معلومات الحساب 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **الايدي:** `{user_id}`
⎆ **الاسم:** {first_name} {last_name}
⎆ **اليوزر:** {username}
⎆ **المطور:** @SSSTlF
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
        
        if photos:
            await event.reply(text, file=photos[0])
        else:
            await event.reply(text)
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .المطور ==========
@client.on(events.NewMessage(pattern=r'\.المطور'))
async def developer_info(event):
    try:
        me = await event.client.get_me()
        user_id = me.id
        first_name = me.first_name or "المطور"
        
        photos = await event.client.get_profile_photos(me)
        
        text = f"""**ᯓ  سورس عبود - مطور السورس 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **المطور:** عبود
⎆ **الايدي:** `{user_id}`
⎆ **الاسم:** {first_name}
⎆ **القناة:** @SSSTlF
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
        
        if photos:
            await event.reply(text, file=photos[0])
        else:
            await event.reply(text)
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .ايدي ==========
@client.on(events.NewMessage(pattern=r'\.ايدي'))
async def get_id(event):
    try:
        me = await event.client.get_me()
        user_id = me.id
        chat_id = event.chat_id
        
        photos = await event.client.get_profile_photos(me)
        
        text = f"""**ᯓ  سورس عبود - معرف الأيدي 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **ايديك:** `{user_id}`
⎆ **ايدي المحادثة:** `{chat_id}`
⎆ **ايدي المطور:** `{user_id}`
⎆ **مبرمج السورس:** @SSSTlF
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
        
        if photos:
            await event.reply(text, file=photos[0])
        else:
            await event.reply(text)
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .بحث ==========
@client.on(events.NewMessage(pattern=r'\.بحث (.+)'))
async def search_command(event):
    try:
        query = event.pattern_match.group(1)
        await event.reply(f"🔍 جاري البحث عن: {query}...")
        
        # محاولة البحث عن فيديو
        video_url = await search_video(query)
        
        if video_url:
            text = f"""**ᯓ  سورس عبود - نتيجة البحث 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **البحث:** {query}
⎆ **النتيجة:** [اضغط هنا للمشاهدة]({video_url})
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
            await event.reply(text)
        else:
            await event.reply(f"❌ لم يتم العثور على نتائج لـ: {query}")
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .فيديو ==========
@client.on(events.NewMessage(pattern=r'\.فيديو (.+)'))
async def video_command(event):
    try:
        query = event.pattern_match.group(1)
        await event.reply(f"🎬 جاري البحث عن فيديو: {query}...")
        
        video_url = await search_video(query)
        
        if video_url:
            text = f"""**ᯓ  سورس عبود - فيديو 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **اسم الفيديو:** {query}
⎆ **رابط المشاهدة:** [اضغط هنا]({video_url})
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
            await event.reply(text)
        else:
            await event.reply(f"❌ لم يتم العثور على فيديو لـ: {query}")
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .اغنية ==========
@client.on(events.NewMessage(pattern=r'\.اغنية (.+)'))
async def audio_command(event):
    try:
        query = event.pattern_match.group(1)
        await event.reply(f"🎵 جاري البحث عن أغنية: {query}...")
        
        audio_url = await search_audio(query)
        
        if audio_url:
            text = f"""**ᯓ  سورس عبود - أغنية 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **اسم الأغنية:** {query}
⎆ **رابط الاستماع:** [اضغط هنا]({audio_url})
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
            await event.reply(text)
        else:
            await event.reply(f"❌ لم يتم العثور على أغنية لـ: {query}")
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .كت ==========
@client.on(events.NewMessage(pattern=r'\.كت'))
async def quote_command(event):
    try:
        quote = random.choice(QUOTES)
        text = f"""**ᯓ  سورس عبود - حكمة 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **الحكمة:** {quote}
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
        await event.reply(text)
        
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
