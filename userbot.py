from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession
import asyncio
import os

API_ID = int(os.environ.get('API_ID', 38532428))
API_HASH = os.environ.get('API_HASH', 'bd13b721c96184649dbbce14de78147d')
PHONE_NUMBER = os.environ.get('PHONE_NUMBER', '+966540049081')
SESSION_STRING = os.environ.get('userbot_session')

if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient('userbot_session', API_ID, API_HASH)

@client.on(events.NewMessage(pattern='^.help$', outgoing=True))
async def help_cmd(event):
    text = """🧠 **الأوامر المتاحة**:
`.info` - معلومات حسابك
`.stats` - عدد المحادثات
`.read` - تعيين الكل مقروء
`.purge` - حذف 50 رسالة
`.join` + رابط - الانضمام لقناة
`.leave` - مغادرة المجموعة
`.users` - عدد الأعضاء
`.admins` - قائمة المدراء
`.block` + ID - حظر مستخدم
`.unblock` + ID - إلغاء الحظر"""
    await event.edit(text)

@client.on(events.NewMessage(pattern='^.info$', outgoing=True))
async def info_cmd(event):
    me = await client.get_me()
    text = f"👤 **حسابك**:\n- الاسم: {me.first_name}\n- المعرف: @{me.username or 'بدون'}\n- ID: `{me.id}`"
    await event.edit(text)

@client.on(events.NewMessage(pattern='^.stats$', outgoing=True))
async def stats_cmd(event):
    dialogs = await client.get_dialogs()
    await event.edit(f"📊 **المحادثات**: {len(dialogs)}")

@client.on(events.NewMessage(pattern='^.read$', outgoing=True))
async def read_all_cmd(event):
    await event.edit('🔄 جارٍ...')
    for dialog in await client.get_dialogs():
        if dialog.unread_count:
            await client.send_read_acknowledge(dialog.id)
    await event.edit('✅ تم تعيين الكل مقروء')

@client.on(events.NewMessage(pattern='^.purge(?: (\\d+))?$', outgoing=True))
async def purge_cmd(event):
    limit = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else 50
    await event.edit(f'🔄 جارٍ حذف {limit}...')
    count = 0
    async for msg in client.iter_messages(event.chat_id, limit=limit):
        if msg.id != event.id:
            await msg.delete()
            count += 1
            await asyncio.sleep(0.2)
    await event.edit(f'✅ تم حذف {count}')

@client.on(events.NewMessage(pattern='^.join (.*)$', outgoing=True))
async def join_cmd(event):
    link = event.pattern_match.group(1)
    await event.edit('🔄 جارٍ الانضمام...')
    try:
        entity = await client.join_channel(link)
        await event.edit(f'✅ تم الانضمام إلى: {entity.title}')
    except Exception as e:
        await event.edit(f'❌ فشل: {str(e)[:50]}')

@client.on(events.NewMessage(pattern='^.leave$', outgoing=True))
async def leave_cmd(event):
    await event.edit('🔄 جارٍ المغادرة...')
    await client.delete_dialog(event.chat_id)
    await event.delete()

@client.on(events.NewMessage(pattern='^.users$', outgoing=True))
async def users_cmd(event):
    try:
        total = await client.get_participants(event.chat_id)
        await event.edit(f'👥 عدد الأعضاء: {len(total)}')
    except Exception as e:
        await event.edit(f'❌ فشل: {str(e)[:50]}')

@client.on(events.NewMessage(pattern='^.admins$', outgoing=True))
async def admins_cmd(event):
    try:
        admins = await client.get_participants(event.chat_id, filter=types.ChannelParticipantsAdmins())
        text = "👑 **المدراء**:\n" + "\n".join([f"- {u.first_name}" for u in admins[:10]])
        await event.edit(text)
    except Exception as e:
        await event.edit(f'❌ فشل: {str(e)[:50]}')

@client.on(events.NewMessage(pattern='^.block (\\d+)$', outgoing=True))
async def block_cmd(event):
    user_id = int(event.pattern_match.group(1))
    try:
        await client(functions.contacts.BlockRequest(id=user_id))
        await event.edit(f'🚫 تم حظر {user_id}')
    except Exception as e:
        await event.edit(f'❌ فشل: {str(e)[:50]}')

@client.on(events.NewMessage(pattern='^.unblock (\\d+)$', outgoing=True))
async def unblock_cmd(event):
    user_id = int(event.pattern_match.group(1))
    try:
        await client(functions.contacts.UnblockRequest(id=user_id))
        await event.edit(f'✅ تم إلغاء حظر {user_id}')
    except Exception as e:
        await event.edit(f'❌ فشل: {str(e)[:50]}')

async def main():
    await client.start(phone=PHONE_NUMBER)
    me = await client.get_me()
    print(f'✅ تم تشغيل UserBot بنجاح')
    print(f'👤 المالك: {me.first_name} (ID: {me.id})')
    print('📌 الأوامر تبدأ بـ (.) نقطة - اكتب .help')
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
