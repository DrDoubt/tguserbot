import time
import random

from tg_userbot import CMD_HELP, VIRUS
from tg_userbot.events import register

@register(outgoing=True, pattern=r"^.infect")
async def infect(event):
	if not event.text[0].isalpha() and event.text[0] in ("."):
		replymsg = await event.get_reply_message()
		if replymsg:
			if replymsg.sender.id == event.sender.first_name:
				await event.edit("Decided to end your life? I won't let you.")
				return
			rf=open("patients.txt", "r", encoding="utf-8")
			read=rf.read()
			rf.close()
			if f"[{replymsg.sender.first_name}](tg://user?id={replymsg.sender.id})" in read:
				await event.edit(f"{replymsg.sender.first_name} was already infected by you or someone you merged patients with!")
				return
			f=open("patients.txt","a+", encoding="utf-8")
			f.write(f"[{replymsg.sender.first_name}](tg://user?id={replymsg.sender.id})\n")
			f.close()
			await replymsg.reply(f"{replymsg.sender.first_name}, you are now infected with the {VIRUS}!")
			await event.delete()
		else:
			await event.edit("I don't know whom to infect!")
		
@register(outgoing=True, pattern=r"^.infstats")
async def infected(event):
	if not event.text[0].isalpha() and event.text[0] in ("."):
		rf=open("patients.txt", "r", encoding="utf-8")
		read=rf.read()
		rf.close()
		reply = f"List of people infected with the {VIRUS}:\n{read}"
		await event.edit(reply[0:4090])

CMD_HELP.update({
    "disease":
        ".infect\
    \nUsage: Infect someone\
	.infstats\
    \nUsage: Stats on the people you infected"})