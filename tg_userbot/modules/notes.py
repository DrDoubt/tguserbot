from tg_userbot import bot, CMD_HELP
from tg_userbot.events import register
from tg_userbot.modules.libs.get_id import get_id
import os.path
from os import path
import os

@register(outgoing=True, pattern="^\.save (\w+) (.*)")
async def save(mention):
    name = mention.pattern_match.group(1)
    text = mention.pattern_match.group(2)
    npath = "notes/" + name + ".txt"
    if not os.path.isdir("notes/"):
        os.makedirs("notes/")
    f=open(npath,"w+")
    f.write(text)
    await mention.edit(f"Successfully saved note `{name}`.\n"+
                       f"Type `.note {name}` to get it.")

@register(outgoing=True, pattern="^\.note (.*)")
async def note(mention):
    name = mention.pattern_match.group(1)
    npath = "notes/" + name + ".txt"
    if not path.exists(npath):
        return
    f=open(npath,"r+")
    await mention.edit(f.read())

@register(outgoing=True, pattern="^\.notes")
async def notes(mention):
    reply = "You have these notes:\n\n"
    allnotes = os.listdir("notes/")
    if not allnotes:
        reply = "You have no notes!"
    else:
        for n in allnotes:
            reply = reply + f"- {n.split('.')[0]}\n"
        reply = reply + "\nGet any of these notes by typing `.note <notename>`"
    await mention.edit(reply)