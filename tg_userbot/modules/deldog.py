import asyncio
from datetime import datetime
import os
import requests
from tg_userbot import bot, CMD_HELP, BOTLOG, LANG
from tg_userbot.events import register

def progress(current, total):
    print("Downloaded {} of {}\nCompleted {}".format(current, total, (current / total) * 100))

@register(outgoing=True, pattern="^\.dog(.*)")
async def _(event):
    tmp_dir = "deldog_temp"
    if event.fwd_from:
        return
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    start = datetime.now()
    input_str = event.pattern_match.group(1)
    message = "Syntax: `.dog <text>`"
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.media:
            await event.edit("`Downloading file...`")
            downloaded_file_name = await bot.download_media(
                previous_message,
                tmp_dir,
                progress_callback=progress
            )
            print("sdfjds")
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            message = ""
            for m in m_list:
                message += m.decode("UTF-8") + "\r\n"
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message
    else:
        await event.edit("Syntax: `.dog <text>`")
    await event.edit("`Uploading...`")
    url = "https://del.dog/documents"
    r = requests.post(url, data=message.encode("UTF-8")).json()
    url = f"https://del.dog/{r['key']}"
    end = datetime.now()
    ms = (end - start).seconds
    if r["isUrl"]:
        nurl = f"https://del.dog/v/{r['key']}"
        await event.edit("Pasted to {} in {} seconds. [link]({}).".format(url, ms, nurl))
    else:
        await event.edit("Pasted to {} in {} seconds.".format(url, ms))
        
CMD_HELP.update({
    'deldog':
        "`.dog <text>`\
    \nUsage: Create a del.dog from text."})