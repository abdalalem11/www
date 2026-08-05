# -*- coding: utf-8 -*-
import asyncio
import os
import re
import random
import time
import json
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button, errors
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest, GetParticipantRequest
from telethon.tl.functions.messages import AddChatUserRequest, DeleteMessagesRequest, GetHistoryRequest
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

# ========== قاموس الأوامر الرئيسية والعناوين ==========
COMMANDS = {
    "1": {"title": "أوامـر الإدارة والكروبـات", "cmds": ["طرد", "كتم", "رفع مشرف", "تنزيل مشرف", "حظر", "الغاء حظر", "تثبيت", "الغاء تثبيت", "تنظيف", "تعديل"]},
    "2": {"title": "أوامـر الألعـاب والترفيـه", "cmds": ["نرد", "نكتة", "تويت", "سؤال", "تخمين", "حصان"]},
    "3": {"title": "الأوامـر الأساسيـة والإعدادات", "cmds": ["اعدادات", "تغيير الاسم", "تغيير الصورة", "حالة"]},
    "4": {"title": "أوامـر متقدمـة وإعدادات", "cmds": ["تشفير", "فك تشفير", "ضغط", "فك ضغط"]},
    "5": {"title": "الأوامـر الوقتيـة والمزامنـة", "cmds": ["تذكير", "جدول", "موعد"]},
    "6": {"title": "أوامـر الإضافـة والتفليـش", "cmds": ["اضافة", "حذف", "تفليش"]},
    "7": {"title": "الذكـاء الاصطناعـي والذاكـرة", "cmds": ["ترجم", "ذكي", "ملخص", "تحليل"]},
    "8": {"title": "التخزيـن والأرشفـة", "cmds": ["حفظ", "استرجاع", "ارشفة"]},
    "9": {"title": "تحويـل ورفـع الملفـات", "cmds": ["تحميل", "فيديو", "صورة", "موسيقى", "رفع"]},
    "10": {"title": "انتحـال الهويـات", "cmds": ["تغيير هوية", "اخفاء", "تمويه"]},
    "11": {"title": "الهمسـات والرسائـل السريـة", "cmds": ["همس", "رسالة سرية", "تشفير رسالة"]},
    "12": {"title": "ربـط الواتسـاب", "cmds": ["ربط واتساب", "فصل واتساب"]},
    "13": {"title": "أوقـات الصلاة والأذكـار", "cmds": ["صلاة", "اذكار", "قرآن"]},
    "14": {"title": "النشـر التلقائـي والجدولـة", "cmds": ["نشر تلقائي", "جدولة منشور"]},
    "15": {"title": "أوامـر المطـوّر الخاصـة", "cmds": ["تحديث", "اعادة تشغيل", "توقف"]},
    "16": {"title": "إنشـاء ومغادرة المجموعـات", "cmds": ["انشاء مجموعة", "مغادرة مجموعة"]},
    "17": {"title": "البـث الصوتـي والأذكـار", "cmds": ["بث صوتي", "تسجيل"]},
    "18": {"title": "تحويـل النـص إلى صـوت", "cmds": ["نص لصوت", "صوت لنص"]},
    "19": {"title": "أوامـر إضافيـة متنوعـة", "cmds": ["تطبيقات", "مواقع"]},
    "20": {"title": "البصمـات الصوتيـة", "cmds": ["بصمة", "تسجيل بصمة"]},
    "21": {"title": "أوامـر الأفتـارات", "cmds": ["افتار", "تغيير افتار"]},
    "22": {"title": "أدوات التهكيـر المزحـي", "cmds": ["مزح", "خدعة"]},
    "23": {"title": "التاغ والمنشـن الجماعـي", "cmds": ["تاغ عام", "تاغ خاص", "منشن"]},
    "24": {"title": "حفـظ الذاتيـة والإعدادات", "cmds": ["حفظ اعدادات", "استرجاع اعدادات"]},
    "25": {"title": "رفـع ترفيهـي ومضحـك", "cmds": ["رفع ترفيهي", "مضحك"]},
    "26": {"title": "الاشتراك الإجبـاري للقنـوات", "cmds": ["اشتراك اجباري", "قنوات"]},
    "27": {"title": "صيـد اليوزرات والمعـرّفات", "cmds": ["بحث يوزر", "صيد يوزرات"]},
    "28": {"title": "تخصيص الكليشـات والقوالـب", "cmds": ["كليشات", "قوالب"]},
    "29": {"title": "حمايـة الرسائـل الخاصـة", "cmds": ["حماية", "فلتر"]},
    "30": {"title": "تحميـل الاستوريات", "cmds": ["استوري", "استوري قناة"]},
    "31": {"title": "الخطـوط والأنمـاط التلقائيـة", "cmds": ["خط", "عكسي", "كبير"]},
    "32": {"title": "البنـك وتجميـع النقـاط", "cmds": ["رصيدي", "تحويل", "هدية", "توب"]},
    "33": {"title": "الحالات الوهميـة والمزيفـة", "cmds": ["حالة وهمية", "مزيف"]},
    "34": {"title": "البريـد الإلكترونـي المؤقـت", "cmds": ["بريد مؤقت", "استلام"]},
    "35": {"title": "مراقبـة الأشخـاص والتتبـع", "cmds": ["تتبع", "مراقبة"]},
    "36": {"title": "أوامـر التسليـة الإضافيـة", "cmds": ["تسلية", "فكاهة"]},
    "37": {"title": "أوامـر التعيينـات", "cmds": ["تعيين", "الغاء تعيين"]},
    "38": {"title": "بـوت التواصـل والدعـم", "cmds": ["تواصل", "دعم"]},
    "39": {"title": "أوامـر المناسبـات الدينيـة", "cmds": ["مناسبة", "تقويم"]},
    "40": {"title": "أوامـر البلاغـات", "cmds": ["بلاغ", "شكوى"]},
    "41": {"title": "تحديثـات شاومـي", "cmds": ["شاومي", "اخبار"]},
    "42": {"title": "هدايـا تليجـرام (النجـوم)", "cmds": ["نجوم", "ارسال هدية"]},
    "43": {"title": "أوامـر المسابقـات", "cmds": ["مسابقة", "نتيجة"]}
}

# ========== نظام النقاط المؤقت ==========
user_balances = {}

# ========== أمر القائمة الرئيسية ==========
@client.on(events.NewMessage(pattern=r'\.قائمة'))
async def main_menu(event):
    user = await event.get_sender()
    name = user.first_name or "المستخدم"
    text = f"""**ᯓ  سورس عبود - قائمـة الأوامـر 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ مـرحبًــا {name} - اضغـط ع الامـر لـ النسـخ
⎆ ضـع نقطة (.) بداية كل امـر :
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆"""
    
    buttons = []
    for i in range(1, 44):
        cmd = f".م{i}"
        title = COMMANDS[str(i)]["title"]
        buttons.append([Button.inline(f"{cmd} ➥ {title}", f"show_{i}")])
    
    await event.reply(text, buttons=buttons)

# ========== معالج الأزرار ==========
@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    
    if data.startswith("show_"):
        num = data.replace("show_", "")
        cmd = f".م{num}"
        title = COMMANDS[num]["title"]
        cmds = COMMANDS[num]["cmds"]
        
        text = f"""**ᯓ  سورس عبود - {title} 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆"""
        buttons = []
        for c in cmds:
            buttons.append([Button.inline(f".{c}", f"copy_.{c}")])
        buttons.append([Button.inline("↩ رجوع للقائمة الرئيسية", "menu")])
        await event.edit(text, buttons=buttons)
    
    elif data.startswith("copy_"):
        cmd = data.replace("copy_", "")
        await event.answer(f"✅ تم نسخ الأمر: .{cmd}", alert=False)
        await event.edit(f"**الأمر:** `.{cmd}`\n\n✅ تم النسخ، أرسل الأمر الآن")
    
    elif data == "menu":
        await main_menu(event)

# ========== عرض القائمة عند كتابة الأمر ==========
@client.on(events.NewMessage(pattern=r'\.م(\d+)'))
async def show_menu(event):
    num = event.pattern_match.group(1)
    
    if num in COMMANDS:
        title = COMMANDS[num]["title"]
        cmds = COMMANDS[num]["cmds"]
        
        text = f"""**ᯓ  سورس عبود - {title} 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆"""
        buttons = []
        for c in cmds:
            buttons.append([Button.inline(f".{c}", f"copy_.{c}")])
        buttons.append([Button.inline("↩ رجوع للقائمة الرئيسية", "menu")])
        await event.reply(text, buttons=buttons)
    else:
        await event.reply("❌ قائمة غير موجودة")

# ========== الأوامر الفعلية ==========

# ----- أوامر الإدارة (م1) -----
@client.on(events.NewMessage(pattern=r'\.طرد (?:@|)([\w]+)'))
async def kick_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.kick_participant(event.chat_id, user)
        await event.reply(f"✅ تم طرد {user.first_name}")
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ فشل الطرد: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.حظر (?:@|)([\w]+)'))
async def ban_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.ban_participant(event.chat_id, user)
        await event.reply(f"✅ تم حظر {user.first_name}")
    except FloodWaitError as e:
        await event.reply(f"⏳ انتظر {e.seconds} ثانية ثم حاول")
    except Exception as e:
        await event.reply(f"❌ فشل الحظر: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.الغاء حظر (?:@|)([\w]+)'))
async def unban_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.unban_participant(event.chat_id, user)
        await event.reply(f"✅ تم إلغاء حظر {user.first_name}")
    except Exception as e:
        await event.reply(f"❌ فشل إلغاء الحظر: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.رفع مشرف (?:@|)([\w]+)'))
async def promote_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.edit_admin(event.chat_id, user, is_admin=True)
        await event.reply(f"✅ تم رفع {user.first_name} مشرف")
    except Exception as e:
        await event.reply(f"❌ فشل الرفع: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.تنزيل مشرف (?:@|)([\w]+)'))
async def demote_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.edit_admin(event.chat_id, user, is_admin=False)
        await event.reply(f"✅ تم تنزيل {user.first_name} من المشرفين")
    except Exception as e:
        await event.reply(f"❌ فشل التنزيل: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.كتم (?:@|)([\w]+)'))
async def mute_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        until_date = datetime.now() + timedelta(hours=24)
        await event.client.edit_permissions(event.chat_id, user, until_date=until_date, send_messages=False)
        await event.reply(f"✅ تم كتم {user.first_name} لمدة 24 ساعة")
    except Exception as e:
        await event.reply(f"❌ فشل الكتم: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.الغاء كتم (?:@|)([\w]+)'))
async def unmute_user(event):
    try:
        user = await event.client.get_entity(event.pattern_match.group(1))
        await event.client.edit_permissions(event.chat_id, user, send_messages=True)
        await event.reply(f"✅ تم إلغاء كتم {user.first_name}")
    except Exception as e:
        await event.reply(f"❌ فشل إلغاء الكتم: {str(e)}")

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

@client.on(events.NewMessage(pattern=r'\.الغاء تثبيت'))
async def unpin_message(event):
    try:
        await event.client.unpin_message(event.chat_id)
        await event.reply("✅ تم إلغاء تثبيت الرسالة")
    except Exception as e:
        await event.reply(f"❌ فشل إلغاء التثبيت: {str(e)}")

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

@client.on(events.NewMessage(pattern=r'\.تعديل (.*)'))
async def edit_message(event):
    try:
        text = event.pattern_match.group(1)
        msg = await event.get_reply_message()
        if msg:
            await event.client.edit_message(event.chat_id, msg.id, text)
            await event.reply("✅ تم تعديل الرسالة")
        else:
            await event.reply("❌ قم بالرد على رسالة لتعديلها")
    except Exception as e:
        await event.reply(f"❌ فشل التعديل: {str(e)}")

# ----- أوامر الألعاب (م2) -----
@client.on(events.NewMessage(pattern=r'\.نرد'))
async def dice(event):
    num = random.randint(1, 6)
    await event.reply(f"🎲 نتيجة النرد: **{num}**")

@client.on(events.NewMessage(pattern=r'\.نكتة'))
async def joke(event):
    jokes = [
        "لماذا لم يتزوج الحاسوب؟ لأنه كان يبحث عن شريحة متوافقة 😂",
        "ماذا قال الجوال للحاسوب؟ لا تنسَ أن تشحن نفسك! 🔋",
        "لماذا ذهب المبرمج إلى الطبيب؟ لأنه كان يعاني من `SyntaxError` في حياته 😅",
        "ما الفرق بين المبرمج والطبيب؟ المبرمج يعالج الأخطاء والطبيب يعالج المرضى 🤓"
    ]
    await event.reply(random.choice(jokes))

@client.on(events.NewMessage(pattern=r'\.تويت'))
async def tweet(event):
    tweets = [
        "النجاح ليس نهائياً، والفشل ليس قاتلاً: الشجاعة للاستمرار هي ما يهم.",
        "كن التغيير الذي تريد رؤيته في العالم.",
        "الحياة ليست عن إيجاد الذات، الحياة عن خلق الذات.",
        "المستقبل لأولئك الذين يؤمنون بجمال أحلامهم."
    ]
    await event.reply(f"🐦 {random.choice(tweets)}")

@client.on(events.NewMessage(pattern=r'\.سؤال'))
async def random_question(event):
    questions = [
        "ما هو الشيء الذي كلما زاد نقص؟ (الجواب: العمر)",
        "ما هو الشيء الذي له عين ولا يرى؟ (الجواب: الإبرة)",
        "ما هو الشيء الذي يمشي بلا رجلين؟ (الجواب: الساعة)",
        "ما هو الشيء الذي تأكله ولا تستطيع أن تأكله؟ (الجواب: الصبر)"
    ]
    await event.reply(f"❓ {random.choice(questions)}")

@client.on(events.NewMessage(pattern=r'\.تخمين (\d+)'))
async def guess_number(event):
    try:
        guess = int(event.pattern_match.group(1))
        number = random.randint(1, 100)
        if guess == number:
            await event.reply(f"🎯 صحيح! الرقم هو {number}")
        elif guess < number:
            await event.reply(f"📈 الرقم أكبر من {guess}")
        else:
            await event.reply(f"📉 الرقم أصغر من {guess}")
    except Exception as e:
        await event.reply(f"❌ خطأ: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.حصان'))
async def horse_game(event):
    horses = ["🐎", "🐴", "🏇", "🐏", "🐕"]
    winner = random.choice(horses)
    await event.reply(f"🏁 سباق الخيول!\nالفائز: {winner}")

# ----- أوامر الذكاء الاصطناعي (م7) -----
@client.on(events.NewMessage(pattern=r'\.ترجم (.*)'))
async def translate_text(event):
    text = event.pattern_match.group(1)
    await event.reply(f"🌐 الترجمة التقريبية:\n{text}\n\n(سيتم تفعيل الترجمة الفعلية قريباً)")

@client.on(events.NewMessage(pattern=r'\.ذكي (.*)'))
async def ai_reply(event):
    question = event.pattern_match.group(1)
    replies = [
        f"🧠 سؤال ذكي: '{question}'\nجوابي: هذا سؤال مهم، لكنني في طور التعلم!",
        f"🧠 '{question}'\nجوابي: أحتاج إلى مزيد من البيانات للإجابة بدقة.",
        f"🧠 '{question}'\nجوابي: شكراً على سؤالك، سأجيب قريباً بعد التحديث."
    ]
    await event.reply(random.choice(replies))

@client.on(events.NewMessage(pattern=r'\.ملخص'))
async def summarize_text(event):
    msg = await event.get_reply_message()
    if msg and msg.text:
        text = msg.text
        summary = text[:150] + "..." if len(text) > 150 else text
        await event.reply(f"📝 الملخص:\n{summary}")
    else:
        await event.reply("❌ قم بالرد على نص لتلخيصه")

@client.on(events.NewMessage(pattern=r'\.تحليل'))
async def analyze_message(event):
    msg = await event.get_reply_message()
    if msg:
        analysis = f"📊 تحليل الرسالة:\n"
        analysis += f"• الطول: {len(msg.text)} حرف\n"
        analysis += f"• الكلمات: {len(msg.text.split())} كلمة\n"
        analysis += f"• التاريخ: {msg.date}\n"
        analysis += f"• المعرف: {msg.sender_id}\n"
        await event.reply(analysis)
    else:
        await event.reply("❌ قم بالرد على رسالة لتحليلها")

# ----- أوامر التاغ (م23) -----
@client.on(events.NewMessage(pattern=r'\.تاغ عام'))
async def tag_all(event):
    try:
        await event.reply("👥 جارٍ تاغ جميع الأعضاء...")
        participants = await event.client.get_participants(event.chat_id)
        mentions = []
        for p in participants:
            if p.username:
                mentions.append(f"@{p.username}")
        if mentions:
            chunks = [mentions[i:i+20] for i in range(0, len(mentions), 20)]
            for chunk in chunks:
                await event.reply(" ".join(chunk))
        else:
            await event.reply("❌ لا يوجد أعضاء لديهم يوزرات للتاغ")
    except Exception as e:
        await event.reply(f"❌ فشل التاغ: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.تاغ خاص (.*)'))
async def tag_special(event):
    text = event.pattern_match.group(1)
    try:
        participants = await event.client.get_participants(event.chat_id)
        mentions = []
        for p in participants[:10]:
            if p.username:
                mentions.append(f"@{p.username}")
        if mentions:
            await event.reply(f"📢 {text}\n{' '.join(mentions)}")
        else:
            await event.reply("❌ لا يوجد أعضاء لديهم يوزرات")
    except Exception as e:
        await event.reply(f"❌ فشل التاغ: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.منشن (.*)'))
async def mention_text(event):
    text = event.pattern_match.group(1)
    try:
        participants = await event.client.get_participants(event.chat_id)
        mentions = []
        for p in participants[:10]:
            mentions.append(f"[{p.first_name}](tg://user?id={p.id})")
        if mentions:
            await event.reply(f"{text}\n{' '.join(mentions)}", parse_mode='md')
        else:
            await event.reply("❌ لا يوجد أعضاء")
    except Exception as e:
        await event.reply(f"❌ فشل المنشن: {str(e)}")

# ----- أوامر الخطوط (م31) -----
@client.on(events.NewMessage(pattern=r'\.خط (.*)'))
async def fancy_text(event):
    text = event.pattern_match.group(1)
    fancy = ""
    for c in text:
        if 'a' <= c <= 'z':
            fancy += chr(ord(c) + 0x1D400)
        elif 'A' <= c <= 'Z':
            fancy += chr(ord(c) + 0x1D400)
        else:
            fancy += c
    await event.reply(f"✒️ خط مزخرف:\n{fancy}")

@client.on(events.NewMessage(pattern=r'\.عكسي (.*)'))
async def reverse_text(event):
    text = event.pattern_match.group(1)
    await event.reply(f"🔄 عكس النص:\n{text[::-1]}")

@client.on(events.NewMessage(pattern=r'\.كبير (.*)'))
async def big_text(event):
    text = event.pattern_match.group(1)
    await event.reply(f"🔠 نص كبير:\n{text.upper()}")

# ----- نظام النقاط (م32) -----
@client.on(events.NewMessage(pattern=r'\.رصيدي'))
async def my_balance(event):
    user_id = event.sender_id
    balance = user_balances.get(user_id, 0)
    await event.reply(f"💰 رصيدك الحالي: **{balance}** نقطة")

@client.on(events.NewMessage(pattern=r'\.تحويل (\d+) (?:@|)([\w]+)'))
async def transfer_points(event):
    try:
        amount = int(event.pattern_match.group(1))
        username = event.pattern_match.group(2)
        sender_id = event.sender_id
        user = await event.client.get_entity(username)
        receiver_id = user.id
        
        if sender_id == receiver_id:
            await event.reply("❌ لا يمكنك التحويل لنفسك")
            return
        
        if user_balances.get(sender_id, 0) < amount:
            await event.reply(f"❌ رصيدك غير كافٍ. رصيدك: {user_balances.get(sender_id, 0)}")
            return
        
        user_balances[sender_id] = user_balances.get(sender_id, 0) - amount
        user_balances[receiver_id] = user_balances.get(receiver_id, 0) + amount
        await event.reply(f"✅ تم تحويل **{amount}** نقطة إلى @{username}")
    except Exception as e:
        await event.reply(f"❌ فشل التحويل: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.هدية (\d+) (?:@|)([\w]+)'))
async def gift_points(event):
    try:
        amount = int(event.pattern_match.group(1))
        username = event.pattern_match.group(2)
        sender_id = event.sender_id
        user = await event.client.get_entity(username)
        receiver_id = user.id
        
        if sender_id == receiver_id:
            await event.reply("❌ لا يمكنك إرسال هدية لنفسك")
            return
        
        if user_balances.get(sender_id, 0) < amount:
            await event.reply(f"❌ رصيدك غير كافٍ. رصيدك: {user_balances.get(sender_id, 0)}")
            return
        
        user_balances[sender_id] = user_balances.get(sender_id, 0) - amount
        user_balances[receiver_id] = user_balances.get(receiver_id, 0) + amount
        await event.reply(f"🎁 تم إرسال **{amount}** نقطة كهدية إلى @{username}")
    except Exception as e:
        await event.reply(f"❌ فشل إرسال الهدية: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.توب'))
async def top_balance(event):
    if not user_balances:
        await event.reply("❌ لا يوجد مستخدمين لديهم نقاط بعد")
        return
    sorted_users = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)[:5]
    top_text = "🏆 **ترتيب الأغنياء:**\n\n"
    for i, (user_id, balance) in enumerate(sorted_users, 1):
        try:
            user = await event.client.get_entity(user_id)
            name = user.first_name or str(user_id)
            top_text += f"{i}. {name} ➥ {balance} نقطة\n"
        except:
            top_text += f"{i}. مستخدم ➥ {balance} نقطة\n"
    await event.reply(top_text)

# ----- أوامر إضافية -----
@client.on(events.NewMessage(pattern=r'\.اضافة نقاط (\d+) (?:@|)([\w]+)'))
async def add_points(event):
    try:
        amount = int(event.pattern_match.group(1))
        username = event.pattern_match.group(2)
        user = await event.client.get_entity(username)
        user_balances[user.id] = user_balances.get(user.id, 0) + amount
        await event.reply(f"✅ تم إضافة **{amount}** نقطة إلى @{username}")
    except Exception as e:
        await event.reply(f"❌ فشل الإضافة: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.اوامر'))
async def all_commands(event):
    text = """**ᯓ  سورس عبود - قائمة الأوامر الكاملة 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **.م1** ➥ أوامر الإدارة والكروبات
⎆ **.م2** ➥ أوامر الألعاب والترفيه
⎆ **.م3** ➥ الأوامر الأساسية والإعدادات
⎆ **.م4** ➥ أوامر متقدمة وإعدادات
⎆ **.م5** ➥ الأوامر الوقتية والمزامنة
⎆ **.م6** ➥ أوامر الإضافة والتفليش
⎆ **.م7** ➥ الذكاء الاصطناعي والذاكرة
⎆ **.م8** ➥ التخزين والأرشفة
⎆ **.م9** ➥ تحويل ورفع الملفات
⎆ **.م10** ➥ انتحال الهويات
⎆ **.م11** ➥ الهمسات والرسائل السرية
⎆ **.م12** ➥ ربط الواتساب
⎆ **.م13** ➥ أوقات الصلاة والأذكار
⎆ **.م14** ➥ النشر التلقائي والجدولة
⎆ **.م15** ➥ أوامر المطور الخاصة
⎆ **.م16** ➥ إنشاء ومغادرة المجموعات
⎆ **.م17** ➥ البث الصوتي والأذكار
⎆ **.م18** ➥ تحويل النص إلى صوت
⎆ **.م19** ➥ أوامر إضافية متنوعة
⎆ **.م20** ➥ البصمات الصوتية
⎆ **.م21** ➥ أوامر الافتارات
⎆ **.م22** ➥ أدوات التهكير المزحي
⎆ **.م23** ➥ التاغ والمنشن الجماعي
⎆ **.م24** ➥ حفظ الذاتية والإعدادات
⎆ **.م25** ➥ رفع ترفيهي ومضحك
⎆ **.م26** ➥ الاشتراك الإجباري للقنوات
⎆ **.م27** ➥ صيد اليوزرات والمعرفات
⎆ **.م28** ➥ تخصيص الكليشات والقوالب
⎆ **.م29** ➥ حماية الرسائل الخاصة
⎆ **.م30** ➥ تحميل الاستوريات
⎆ **.م31** ➥ الخطوط والأنماط التلقائية
⎆ **.م32** ➥ البنك وتجميع النقاط
⎆ **.م33** ➥ الحالات الوهمية والمزيفة
⎆ **.م34** ➥ البريد الإلكتروني المؤقت
⎆ **.م35** ➥ مراقبة الأشخاص والتتبع
⎆ **.م36** ➥ أوامر التسلية الإضافية
⎆ **.م37** ➥ أوامر التعيينات
⎆ **.م38** ➥ بوت التواصل والدعم
⎆ **.م39** ➥ أوامر المناسبات الدينية
⎆ **.م40** ➥ أوامر البلاغات
⎆ **.م41** ➥ تحديثات شاومي
⎆ **.م42** ➥ هدايا تليجرام (النجوم)
⎆ **.م43** ➥ أوامر المسابقات
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
 𓆩  سورس عبود - قنـاة السـورس 𓆪
 @SSSTlF"""
    await event.reply(text)

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
