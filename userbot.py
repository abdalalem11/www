# -*- coding: utf-8 -*-
import asyncio
import os
import re
import random
import time
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest, DeleteMessagesRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import FloodWaitError
from telethon.tl.types import MessageEntityTextUrl

# ========== إعدادات البوت ==========
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION:
    raise Exception("❌ تأكد من تعيين API_ID, API_HASH, SESSION_STRING في المتغيرات")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ========== قاموس الأوامر الرئيسية ==========
CMD_LIST = {
    ".م1": "أوامـر الإدارة والكروبـات",
    ".م2": "أوامـر الألعـاب والترفيـه",
    ".م3": "الأوامـر الأساسيـة والإعدادات",
    ".م4": "أوامـر متقدمـة وإعدادات",
    ".م5": "الأوامـر الوقتيـة والمزامنـة",
    ".م6": "أوامـر الإضافـة والتفليـش",
    ".م7": "الذكـاء الاصطناعـي والذاكـرة",
    ".م8": "التخزيـن والأرشفـة",
    ".م9": "تحويـل ورفـع الملفـات",
    ".م10": "انتحـال الهويـات",
    ".م11": "الهمسـات والرسائـل السريـة",
    ".م12": "ربـط الواتسـاب",
    ".م13": "أوقـات الصلاة والأذكـار",
    ".م14": "النشـر التلقائـي والجدولـة",
    ".م15": "أوامـر المطـوّر الخاصـة",
    ".م16": "إنشـاء ومغادرة المجموعـات",
    ".م17": "البـث الصوتـي والأذكـار",
    ".م18": "تحويـل النـص إلى صـوت",
    ".م19": "أوامـر إضافيـة متنوعـة",
    ".م20": "البصمـات الصوتيـة",
    ".م21": "أوامـر الأفتـارات",
    ".م22": "أدوات التهكيـر المزحـي",
    ".م23": "التاغ والمنشـن الجماعـي",
    ".م24": "حفـظ الذاتيـة والإعدادات",
    ".م25": "رفـع ترفيهـي ومضحـك",
    ".م26": "الاشتراك الإجبـاري للقنـوات",
    ".م27": "صيـد اليوزرات والمعـرّفات",
    ".م28": "تخصيص الكليشـات والقوالـب",
    ".م29": "حمايـة الرسائـل الخاصـة",
    ".م30": "تحميـل الاستوريات",
    ".م31": "الخطـوط والأنمـاط التلقائيـة",
    ".م32": "البنـك وتجميـع النقـاط",
    ".م33": "الحالات الوهميـة والمزيفـة",
    ".م34": "البريـد الإلكترونـي المؤقـت",
    ".م35": "مراقبـة الأشخـاص والتتبـع",
    ".م36": "أوامـر التسليـة الإضافيـة",
    ".م37": "أوامـر التعيينـات",
    ".م38": "بـوت التواصـل والدعـم",
    ".م39": "أوامـر المناسبـات الدينيـة",
    ".م40": "أوامـر البلاغـات",
    ".م41": "تحديثـات شاومـي",
    ".م42": "هدايـا تليجـرام (النجـوم)",
    ".م43": "أوامـر المسابقـات"
}

# ========== أمر القائمة الرئيسية ==========
@client.on(events.NewMessage(pattern=r'\.قائمة'))
async def main_menu(event):
    user = await event.get_sender()
    name = user.first_name or "المستخدم"
    text = f"""**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - قائمـة الأوامـر 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ مـرحبًــا {name}
⎆ اضغـط ع الامـر لـ النسـخ التلقائي
⎆ ضـع نقطة (.) بداية كل امـر :
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆"""
    
    buttons = []
    for i in range(1, 44):
        cmd = f".م{i}"
        if cmd in CMD_LIST:
            # زر ينسخ الأمر تلقائياً عند الضغط
            buttons.append([Button.inline(f"{cmd} ➥ {CMD_LIST[cmd]}", f"copy_{cmd}")])
    
    await event.reply(text, buttons=buttons)

# ========== معالج النسخ التلقائي ==========
@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    if data.startswith("copy_"):
        cmd = data.replace("copy_", "")
        # نسخ الأمر تلقائياً وإظهار إشعار
        await event.answer(f"✅ تم نسخ الأمر: {cmd}", alert=False)
        # إرسال الأمر في مربع الكتابة (نسخ تلقائي)
        await event.edit(f"**الأمر:** `{cmd}`\n**الوصف:** {CMD_LIST.get(cmd, '')}\n\n✅ تم النسخ، أرسل الأمر الآن")
    elif data == "menu":
        await main_menu(event)

# ========== أمر .م1 (الإدارة) ==========
@client.on(events.NewMessage(pattern=r'\.م1'))
async def admin_commands(event):
    text = """**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - أوامـر الإدارة والكروبـات 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **.طرد** ➥ طرد عضو من المجموعة
⎆ **.كتم** ➥ كتم عضو مؤقتاً
⎆ **.رفع مشرف** ➥ ترقية عضو لمشرف
⎆ **.تنزيل مشرف** ➥ إلغاء صلاحيات المشرف
⎆ **.حظر** ➥ حظر عضو نهائياً
⎆ **.الغاء حظر** ➥ إلغاء حظر عضو
⎆ **.تثبيت** ➥ تثبيت رسالة
⎆ **.الغاء تثبيت** ➥ إلغاء تثبيت الرسالة
⎆ **.تنظيف** ➥ حذف رسائل محددة
⎆ **.تعديل** ➥ تعديل رسالة مرسلة
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩 - قنـاة السـورس 𓆪
@SSSTlF"""
    await event.reply(text, buttons=[
        [Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]
    ])

# ========== أمر .طرد ==========
@client.on(events.NewMessage(pattern=r'\.طرد (?:@|)([\w]+)'))
async def kick_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.kick_participant(event.chat_id, user)
        await event.reply(f"✅ تم طرد {user.first_name}")
    except Exception as e:
        await event.reply(f"❌ فشل الطرد: {str(e)}")

# ========== أمر .حظر ==========
@client.on(events.NewMessage(pattern=r'\.حظر (?:@|)([\w]+)'))
async def ban_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.ban_participant(event.chat_id, user)
        await event.reply(f"✅ تم حظر {user.first_name}")
    except Exception as e:
        await event.reply(f"❌ فشل الحظر: {str(e)}")

# ========== أمر .الغاء حظر ==========
@client.on(events.NewMessage(pattern=r'\.الغاء حظر (?:@|)([\w]+)'))
async def unban_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.unban_participant(event.chat_id, user)
        await event.reply(f"✅ تم إلغاء حظر {user.first_name}")
    except Exception as e:
        await event.reply(f"❌ فشل إلغاء الحظر: {str(e)}")

# ========== أمر .تثبيت ==========
@client.on(events.NewMessage(pattern=r'\.تثبيت'))
async def pin_message(event):
    try:
        msg = await event.get_reply_message()
        if msg:
            await event.client.pin_message(event.chat_id, msg.id)
            await event.reply("✅ تم تثبيت الرسالة")
        else:
            await event.reply("❌ قم بالرد على رسالة لتثبيتها")
    except Exception as e:
        await event.reply(f"❌ فشل التثبيت: {str(e)}")

# ========== أمر .الغاء تثبيت ==========
@client.on(events.NewMessage(pattern=r'\.الغاء تثبيت'))
async def unpin_message(event):
    try:
        await event.client.unpin_message(event.chat_id)
        await event.reply("✅ تم إلغاء تثبيت الرسالة")
    except Exception as e:
        await event.reply(f"❌ فشل إلغاء التثبيت: {str(e)}")

# ========== أمر .تنظيف ==========
@client.on(events.NewMessage(pattern=r'\.تنظيف (\d+)'))
async def clean_messages(event):
    try:
        count = int(event.pattern_match.group(1))
        if count > 100:
            await event.reply("❌ لا يمكن حذف أكثر من 100 رسالة في المرة الواحدة")
            return
        msgs = await event.client.get_messages(event.chat_id, limit=count)
        ids = [msg.id for msg in msgs]
        await event.client.delete_messages(event.chat_id, ids)
        await event.reply(f"✅ تم حذف {len(ids)} رسالة")
    except Exception as e:
        await event.reply(f"❌ فشل التنظيف: {str(e)}")

# ========== أمر .م2 (الألعاب) ==========
@client.on(events.NewMessage(pattern=r'\.م2'))
async def games_commands(event):
    text = """**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - أوامـر الألعـاب والترفيـه 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **.حصان** ➥ لعبة الحصان (تخمين)
⎆ **.سؤال** ➥ سؤال عشوائي
⎆ **.نرد** ➥ رمي النرد
⎆ **.تخمين** ➥ لعبة تخمين الرقم
⎆ **.تويت** ➥ تغريدة عشوائية
⎆ **.نكتة** ➥ نكتة مضحكة
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆"""
    await event.reply(text, buttons=[
        [Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]
    ])

# ========== أمر .نرد ==========
@client.on(events.NewMessage(pattern=r'\.نرد'))
async def dice(event):
    num = random.randint(1, 6)
    await event.reply(f"🎲 نتيجة النرد: **{num}**")

# ========== أمر .نكتة ==========
@client.on(events.NewMessage(pattern=r'\.نكتة'))
async def joke(event):
    jokes = [
        "لماذا لم يتزوج الحاسوب؟ لأنه كان يبحث عن شريحة متوافقة 😂",
        "ماذا قال الجوال للحاسوب؟ لا تنسَ أن تشحن نفسك! 🔋",
        "لماذا ذهب المبرمج إلى الطبيب؟ لأنه كان يعاني من `SyntaxError` في حياته 😅",
    ]
    await event.reply(random.choice(jokes))

# ========== خادم ويب وهمي لإرضاء Render ==========
async def run_web_server():
    """خادم ويب بسيط لإبقاء Render سعيداً"""
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
    
    # إبقاء الخادم مفتوحاً
    await asyncio.Event().wait()

# ========== تشغيل البوت مع خادم الويب ==========
async def main():
    # تشغيل البوت في الخلفية
    await client.start()
    print("✅ البوت يعمل الآن...")
    
    # تشغيل خادم الويب الوهمي
    await run_web_server()

if __name__ == "__main__":
    asyncio.run(main())
