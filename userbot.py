# -*- coding: utf-8 -*-
import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION:
    raise Exception("❌ تأكد من تعيين API_ID, API_HASH, SESSION_STRING في المتغيرات")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ========== معرف المطور ==========
DEVELOPER_ID = 6272941790  # ضع معرفك هنا

# ========== أمر .ا ==========
@client.on(events.NewMessage(pattern=r'\.ا'))
async def my_info(event):
    try:
        # جلب معلومات الحساب
        me = await event.client.get_me()
        user_id = me.id
        first_name = me.first_name or "لا يوجد"
        last_name = me.last_name or ""
        username = f"@{me.username}" if me.username else "لا يوجد يوزر"
        
        # جلب صورة الملف الشخصي
        photos = await event.client.get_profile_photos(me)
        if photos:
            photo = photos[0]
            file = await event.client.download_media(photo, file=bytes)
        else:
            file = None
        
        # نص الرد
        text = f"""**ᯓ  سورس عبود - معلومات الحساب 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **الايدي:** `{user_id}`
⎆ **الاسم:** {first_name} {last_name}
⎆ **اليوزر:** {username}
⎆ **المطور:** @SSSTlF
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
        
        # إرسال الرد مع الصورة إن وجدت
        if file:
            await event.reply(text, file=file)
        else:
            await event.reply(text)
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .المطور ==========
@client.on(events.NewMessage(pattern=r'\.المطور'))
async def developer_info(event):
    try:
        # جلب معلومات المطور (الحساب نفسه)
        me = await event.client.get_me()
        user_id = me.id
        first_name = me.first_name or "المطور"
        
        # جلب صورة المطور
        photos = await event.client.get_profile_photos(me)
        if photos:
            photo = photos[0]
            file = await event.client.download_media(photo, file=bytes)
        else:
            file = None
        
        text = f"""**ᯓ  سورس عبود - مطور السورس 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **المطور:** عبود
⎆ **الايدي:** `{user_id}`
⎆ **الاسم:** {first_name}
⎆ **القناة:** @SSSTlF
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
        
        if file:
            await event.reply(text, file=file)
        else:
            await event.reply(text)
            
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

# ========== أمر .ايدي ==========
@client.on(events.NewMessage(pattern=r'\.ايدي'))
async def get_id(event):
    try:
        # جلب ايدي المستخدم نفسه
        me = await event.client.get_me()
        user_id = me.id
        
        # جلب ايدي المحادثة (مجموعة أو خاص)
        chat_id = event.chat_id
        
        # جلب صورة المستخدم
        photos = await event.client.get_profile_photos(me)
        if photos:
            photo = photos[0]
            file = await event.client.download_media(photo, file=bytes)
        else:
            file = None
        
        # جلب معلومات المطور (نفس الحساب)
        dev_id = me.id
        
        text = f"""**ᯓ  سورس عبود - معرف الأيدي 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **ايديك:** `{user_id}`
⎆ **ايدي المحادثة:** `{chat_id}`
⎆ **ايدي المطور:** `{dev_id}`
⎆ **مبرمج السورس:** @SSSTlF
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩  سورس عبود - قنـاة السـورس 𓆪
@SSSTlF"""
        
        if file:
            await event.reply(text, file=file)
        else:
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
