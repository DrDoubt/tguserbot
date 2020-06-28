import time
import random

from tg_userbot import CMD_HELP
from tg_userbot.events import register


@register(outgoing=True, pattern=r"^.flash (.*)")
async def flasher(event):
	if not event.text[0].isalpha() and event.text[0] in ("."):
		r = random.randint(1, 10000)
		text = event.pattern_match.group(1)
		if len(text.split(" ")) > 1:
			await event.edit("`Cannot flash file!`")
			return
		await event.edit(f"`Flashing` {text}.zip`...`")
		time.sleep(4)
		if r % 2 == 1:
			await event.edit(f"`Successfully flashed` {text}.zip`!`")
		elif r % 2 == 0:
			await event.edit(f"`Flashing` {text}.zip `failed successfully!`")
		
		

CMD_HELP.update({
    "flasher":
        ".flash <text>\
    \nUsage: Flash the .zip file."})