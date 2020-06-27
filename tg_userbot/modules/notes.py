from tg_userbot import bot, CMD_HELP
from tg_userbot.events import register
from tg_userbot.modules.libs.get_id import get_id
import os.path
from os import path
import os

@register(outgoing=True, pattern="^\.save (.*) (.*)")
async def save(mention):
    name = mention.pattern_match.group(1)
    text = mention.pattern_match.group(2)
    npath = "notes/" + name + ".txt"
    if not os.path.isdir("notes/"):
        os.makedirs("notes/")
    if path.exists(npath):
        await mention.edit(f"Note `{name}` already exists.")
    f=open(npath,"w+")
    f.write(text)
    await mention.edit(f"Successfully saved note `{name}`.\n"+
                       f"Type `.note {name}` to get it.")

@register(outgoing=True, pattern="^\.note (.*)")
async def note(mention):
    name = mention.pattern_match.group(1)
    npath = "notes/" + name + ".txt"
    if not path.exists(npath):
        await mention.edit(f"Note `{name}` doesn't exist.\n"+
                           f"Type `.save {name} <text> to create the note.")
    f=open(npath,"r+")
    await mention.edit(f.read())