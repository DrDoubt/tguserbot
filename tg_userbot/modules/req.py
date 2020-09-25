import time
import os
import subprocess

from tg_userbot import CMD_HELP
from tg_userbot.events import register

EMOJI_SUCCESS = "✔"
EMOJI_FAILURE = "❌"
EMOJI_INSTALLING = "⏳"
PIP_COMMAND = "python3 -m pip install {}"

@register(pattern=r"^\.req (.*)", outgoing=True)
async def req(event):
    reqs = event.pattern_match.group(1).split()
    message = f"Installing {len(reqs)} package(s):\n"
    success = 0
    for r in reqs:
        message = message + f"{EMOJI_INSTALLING} {r}\n"
        await event.edit(message)
        try:
            bout = subprocess.check_output(PIP_COMMAND.format(r).split())
            output = bout.decode('ascii')
            if f"Requirement already satisfied: {r}" in output:
                message = message.replace(f"{EMOJI_INSTALLING} {r}",f"{EMOJI_FAILURE} {r} (package already installed)")
            else:
                message = message.replace(f"{EMOJI_INSTALLING} {r}",f"{EMOJI_SUCCESS} {r}")
                success = success + 1
        except subprocess.CalledProcessError:
            message = message.replace(f"{EMOJI_INSTALLING} {r}",f"{EMOJI_FAILURE} {r}")
        await event.edit(message.rstrip())
    message = message.replace("Installing ",f"Installed {success}/")
    await event.edit(message.rstrip())

USAGE = "`.req `<package names>\
        \nUsage: installs (or attempts to install) the specified pip package names."

CMD_HELP.update({"req": USAGE})