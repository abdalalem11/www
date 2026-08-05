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

# ========== نظام النقاط المؤقت ==========
user_balances = {}

# ========== أمر القائمة الرئيسية ==========
@client.on(events.NewMessage(pattern=r'\.قائمة'))
async def main_menu(event):
    user = await event.get_sender()
    name = user.first_name or "المستخدم"
    text = f"""**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - قائمـة الأوامـر 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ مـرحبًــا {name}
⎆ اضغـط ع الامـر لـ رؤية التفاصيل
⎆ ضـع نقطة (.) بداية كل امـر :
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆"""
    
    buttons = []
    for i in range(1, 44):
        cmd = f".م{i}"
        if cmd in CMD_LIST:
            buttons.append([Button.inline(f"{cmd} ➥ {CMD_LIST[cmd]}", f"show_{cmd}")])
    
    await event.reply(text, buttons=buttons)

# ========== معالج الأزرار ==========
@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    
    if data.startswith("show_"):
        cmd = data.replace("show_", "")
        await event.answer(f"✅ تم اختيار {cmd}")
        if cmd == ".م1":
            await admin_menu(event)
        elif cmd == ".م2":
            await games_menu(event)
        elif cmd == ".م7":
            await ai_menu(event)
        elif cmd == ".م23":
            await tag_menu(event)
        elif cmd == ".م31":
            await fonts_menu(event)
        elif cmd == ".م32":
            await bank_menu(event)
        else:
            await event.edit(f"**الأمر:** {cmd}\n**الوصف:** {CMD_LIST.get(cmd, '')}\n\n📌 سيتم إضافة الأوامر الفرعية قريباً")
    
    elif data == "menu":
        await main_menu(event)

# ========== قوائم الأوامر الرئيسية ==========
@client.on(events.NewMessage(pattern=r'\.م1'))
async def admin_menu(event):
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
    if isinstance(event, events.CallbackQuery):
        await event.edit(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])
    else:
        await event.reply(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])

@client.on(events.NewMessage(pattern=r'\.م2'))
async def games_menu(event):
    text = """**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - أوامـر الألعـاب والترفيـه 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **.نرد** ➥ رمي النرد
⎆ **.نكتة** ➥ نكتة مضحكة
⎆ **.تويت** ➥ تغريدة عشوائية
⎆ **.سؤال** ➥ سؤال عشوائي
⎆ **.تخمين** ➥ لعبة تخمين الرقم
⎆ **.حصان** ➥ لعبة الحصان
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩 - قنـاة السـورس 𓆪
@SSSTlF"""
    if isinstance(event, events.CallbackQuery):
        await event.edit(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])
    else:
        await event.reply(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])

@client.on(events.NewMessage(pattern=r'\.م7'))
async def ai_menu(event):
    text = """**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - الذكـاء الاصطناعـي والذاكـرة 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **.ترجم** ➥ ترجمة النص
⎆ **.ذكي** ➥ سؤال الذكاء الاصطناعي
⎆ **.ملخص** ➥ تلخيص النص
⎆ **.تحليل** ➥ تحليل رسالة
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩 - قنـاة السـورس 𓆪
@SSSTlF"""
    if isinstance(event, events.CallbackQuery):
        await event.edit(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])
    else:
        await event.reply(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])

@client.on(events.NewMessage(pattern=r'\.م23'))
async def tag_menu(event):
    text = """**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - التاغ والمنشـن الجماعـي 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **.تاغ عام** ➥ تاغ جميع الأعضاء
⎆ **.تاغ خاص** ➥ تاغ مع نص مخصص
⎆ **.منشن** ➥ منشن مع نص
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩 - قنـاة السـورس 𓆪
@SSSTlF"""
    if isinstance(event, events.CallbackQuery):
        await event.edit(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])
    else:
        await event.reply(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])

@client.on(events.NewMessage(pattern=r'\.م31'))
async def fonts_menu(event):
    text = """**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - الخطـوط والأنمـاط التلقائيـة 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **.خط** ➥ تحويل النص لخط مزخرف
⎆ **.عكسي** ➥ عكس النص
⎆ **.كبير** ➥ تكبير النص
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩 - قنـاة السـورس 𓆪
@SSSTlF"""
    if isinstance(event, events.CallbackQuery):
        await event.edit(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])
    else:
        await event.reply(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])

@client.on(events.NewMessage(pattern=r'\.م32'))
async def bank_menu(event):
    text = """**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - البنـك وتجميـع النقـاط 𓆪**
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ **.رصيدي** ➥ عرض الرصيد
⎆ **.تحويل** ➥ تحويل نقاط لشخص
⎆ **.هدية** ➥ إرسال هدية لشخص
⎆ **.توب** ➥ ترتيب الأغنياء
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
𓆩 - قنـاة السـورس 𓆪
@SSSTlF"""
    if isinstance(event, events.CallbackQuery):
        await event.edit(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])
    else:
        await event.reply(text, buttons=[[Button.inline("↩ رجوع للقائمة الرئيسية", "menu")]])

# ========== أوامر الإدارة (م1) ==========
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

# ========== أوامر الألعاب (م2) ==========
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
        "ما الفرق بين المبرمج والطبيب؟ المبرمج يعالج الأخطاء والطبيب يعالج المرضى 🤓",
    ]
    await event.reply(random.choice(jokes))

@client.on(events.NewMessage(pattern=r'\.تويت'))
async def tweet(event):
    tweets = [
        "النجاح ليس نهائياً، والفشل ليس قاتلاً: الشجاعة للاستمرار هي ما يهم.",
        "كن التغيير الذي تريد رؤيته في العالم.",
        "الحياة ليست عن إيجاد الذات، الحياة عن خلق الذات.",
        "المستقبل لأولئك الذين يؤمنون بجمال أحلامهم.",
    ]
    await event.reply(f"🐦 {random.choice(tweets)}")

@client.on(events.NewMessage(pattern=r'\.سؤال'))
async def random_question(event):
    questions = [
        "ما هو الشيء الذي كلما زاد نقص؟",
        "ما هو الشيء الذي له عين ولا يرى؟",
        "ما هو الشيء الذي يمشي بلا رجلين؟",
        "ما هو الشيء الذي تأكله ولا تستطيع أن تأكله؟",
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

# ========== أوامر الذكاء الاصطناعي (م7) ==========
@client.on(events.NewMessage(pattern=r'\.ترجم (.*)'))
async def translate_text(event):
    text = event.pattern_match.group(1)
    await event.reply(f"🌐 الترجمة التقريبية: {text} (هنا ستظهر الترجمة الفعلية عند ربطها بمكتبة ترجمة)")

@client.on(events.NewMessage(pattern=r'\.ذكي (.*)'))
async def ai_reply(event):
    question = event.pattern_match.group(1)
    await event.reply(f"🧠 رد الذكاء الاصطناعي: سؤالك '{question}' مهم جداً، لكنني حالياً في وضع التطوير! 🤖")

@client.on(events.NewMessage(pattern=r'\.ملخص'))
async def summarize_text(event):
    msg = await event.get_reply_message()
    if msg and msg.text:
        text = msg.text
        summary = text[:100] + "..." if len(text) > 100 else text
        await event.reply(f"📝 الملخص: {summary}")
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
        await event.reply(analysis)
    else:
        await event.reply("❌ قم بالرد على رسالة لتحليلها")

# ========== أوامر التاغ (م23) ==========
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
            # تقسيم إلى مجموعات لتجنب الطول الزائد
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

# ========== أوامر الخطوط (م31) ==========
@client.on(events.NewMessage(pattern=r'\.خط (.*)'))
async def fancy_text(event):
    text = event.pattern_match.group(1)
    fancy = "".join([chr(ord(c) + 0x1D400) if c.isalpha() else c for c in text])
    await event.reply(f"✒️ خط مزخرف:\n{fancy}")

@client.on(events.NewMessage(pattern=r'\.عكسي (.*)'))
async def reverse_text(event):
    text = event.pattern_match.group(1)
    await event.reply(f"🔄 عكس النص:\n{text[::-1]}")

@client.on(events.NewMessage(pattern=r'\.كبير (.*)'))
async def big_text(event):
    text = event.pattern_match.group(1)
    await event.reply(f"🔠 نص كبير:\n{text.upper()}")

# ========== نظام النقاط (م32) ==========
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

# ========== أمر الأوامر الكامل ==========
@client.on(events.NewMessage(pattern=r'\.اوامر'))
async def all_commands(event):
    text = """
**ᯓ 𝗧𝗲𝗽𝘁𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - قائمة الأوامر الكاملة 𓆪**
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
𓆩 - قناة السورس 𓆪
@SSSTlF
"""
    await event.reply(text)

# ========== أمر إضافة نقاط (للمطور) ==========
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
