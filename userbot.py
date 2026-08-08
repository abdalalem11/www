# ================================================================
#                   تنصيب تلقائي عبر الجلسة (Auto Install)
# ================================================================

@client.on(events.NewMessage(pattern=r'^\.تنصيب جلسة$'))
async def auto_install_session(event):
    if not await is_owner(event):
        await event.reply("❌ هذا الأمر فقط لصاحب الحساب")
        return
    
    await event.reply("""
📥 **تنصيب تلقائي بالجلسة**

📌 أرسل جلسة تيليجرام المستخرجة في رسالة جديدة
⚠️ الجلسة تبدأ بـ `1` أو `2` وتكون طويلة

✧ **سورس عبود** ✧
""")
    
    global install_waiting, install_user_id, install_step
    install_waiting = True
    install_user_id = event.sender_id
    install_step = "auto_session"

@client.on(events.NewMessage(incoming=True))
async def handle_auto_session_input(event):
    global install_waiting, install_user_id, install_step
    
    if not install_waiting or event.sender_id != install_user_id or install_step != "auto_session":
        return
    
    if event.text.startswith('.'):
        return
    
    session_str = event.text.strip()
    
    if not session_str or len(session_str) < 20:
        await event.reply("❌ الجلسة غير صالحة! تأكد من نسخها كاملة")
        install_waiting = False
        install_step = "phone"
        return
    
    # محاولة الاتصال بالجلسة
    try:
        temp_client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await temp_client.connect()
        me = await temp_client.get_me()
        await temp_client.disconnect()
    except Exception as e:
        await event.reply(f"❌ الجلسة غير صالحة: {str(e)}")
        install_waiting = False
        install_step = "phone"
        return
    
    # حفظ الجلسة في الإعدادات
    CONFIG["session_string"] = session_str
    save_config()
    os.environ["SESSION_STRING"] = session_str
    
    await event.reply(f"""
✅ **تم التنصيب التلقائي بنجاح!**

📋 المعرف: `{me.id}`
📛 الاسم: {me.first_name}
🆔 اليوزر: @{me.username if me.username else 'لا يوجد'}

🔄 جاري إعادة التشغيل مع الجلسة الجديدة...

✧ **سورس عبود** ✧
""")
    
    install_waiting = False
    install_step = "phone"
    
    # إعادة تشغيل البوت
    try:
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
    except:
        # في حال تعذر إعادة التشغيل
        await event.reply("⚠️ تعذر إعادة التشغيل، أعد تشغيل البوت يدوياً")
