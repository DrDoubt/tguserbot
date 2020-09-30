"""
 thx to @r4v4n4
"""

import random
import re

from tg_userbot import bot, CMD_HELP, GBAN_BOTS, GBANS
from tg_userbot.events import register
from tg_userbot.modules.user_info import get_user

@register(outgoing=True, pattern=r"^.scramble(\s+[\S\s]+|$)")
async def scramble_message(e):
    reply_message = await e.get_reply_message()
    text = e.pattern_match.group(1) or reply_message.text
    words = re.split(r"\s", text)
    scrambled = map(scramble_word, words)
    text = ' '.join(scrambled)
    await e.edit(text)


def scramble_word(word):
    if len(word) < 4:
        return word

    first_letter = word[0]
    last_letter = word[-1]
    middle_letters = list(word[1:-1])
    random.shuffle(middle_letters)

    return first_letter + ''.join(middle_letters) + last_letter

CMD_HELP.update({
    "scramble":
        ".scramble <text>\
    \nUsage: Scrambles text."})