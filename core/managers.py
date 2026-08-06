async def edit_delete(event, text, time=5):
    try:
        msg = await event.edit(text)
        await asyncio.sleep(time)
        await msg.delete()
    except:
        pass

async def edit_or_reply(event, text):
    try:
        if event.out:
            return await event.edit(text)
        return await event.reply(text)
    except:
        return await event.reply(text)
