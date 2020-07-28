import os

from emoji import get_emoji_regexp
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from requests import get
from re import findall

from google_play_scraper import app
from google_play_scraper import exceptions as gpse
import asyncurban
from html import unescape
from googleapiclient.discovery import build
from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)
from search_engine_parser import GoogleSearch

from tg_userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, LANG, YOUTUBE_API_KEY
from tg_userbot.events import register

@register(outgoing=True, pattern="^\.currency (.*)")
async def _(event):  # calculates exchange rates, no clue why you would need it, but sure
    if not event.text[0].isalpha() and event.text[0] in ("."):
        if event.fwd_from:
            return
        input_str = event.pattern_match.group(1)
        input_sgra = input_str.split(" ")
        if len(input_sgra) == 3:
            try:
                number = float(input_sgra[0])
                currency_from = input_sgra[1].upper()
                currency_to = input_sgra[2].upper()
                request_url = "https://api.exchangeratesapi.io/latest?base={}".format(currency_from)
                current_response = get(request_url).json()
                if currency_to in current_response["rates"]:
                    current_rate = float(current_response["rates"][currency_to])
                    rebmun = round(number * current_rate, 2)
                    await event.edit("{} {} = {} {}".format(number, currency_from, rebmun, currency_to))
                else:
                    await event.edit("`This seems to be some alien currency, which I can't convert right now.`")
            except e:
                await event.edit(str(e))
        else:
            await event.edit("`Invalid syntax.`")
            return
            
@register(outgoing=True, pattern="^\.ud (.*)")
async def urban_dict(ud_e):
    """ For .ud command, fetch content from Urban Dictionary. """
    await ud_e.edit("`Processing...`")
    query = ud_e.pattern_match.group(1)
    urban_dict_helper = asyncurban.UrbanDictionary()
    try:
        urban_def = await urban_dict_helper.get_word(query)
    except asyncurban.WordNotFoundError:
        await ud_e.edit(f"Sorry, couldn't find any results for: {query}")
        return
    deflen = sum(len(i) for i in urban_def.definition)
    exalen = sum(len(i) for i in urban_def.example)
    meanlen = deflen + exalen
    if int(meanlen) >= 0:
        if int(meanlen) >= 4096:
            await ud_e.edit("`Output too large, sending as file.`")
            file = open("output.txt", "w+")
            file.write("Text: " + query + "\n\nMeaning: " +
                       urban_def.definition + "\n\n" + "Example: \n" +
                       urban_def.example)
            file.close()
            await ud_e.client.send_file(
                ud_e.chat_id,
                "output.txt",
                caption="`Output was too large, sent it as a file.`")
            if os.path.exists("output.txt"):
                os.remove("output.txt")
            await ud_e.delete()
            return
        await ud_e.edit("Text: **" + query + "**\n\nMeaning: **" +
                        urban_def.definition + "**\n\n" + "Example: \n__" +
                        urban_def.example + "__")
        if BOTLOG:
            await ud_e.client.send_message(
                BOTLOG_CHATID, "UrbanDictionary query for `" + query +
                "` executed successfully.")
    else:
        await ud_e.edit("No result found for **" + query + "**")

@register(outgoing=True, pattern="^\.play (.*)")
async def playstore(ps_e):
    """ For .play command, fetch content from Play Store. """
    await ps_e.edit("`Finding...`")
    query = ps_e.pattern_match.group(1)
    try:
        res = app(query)
    except gpse.NotFoundError:
        await ps_e.edit("Invalid package ID")
        return
    await ps_e.edit("**"+res["title"]+"**\n\nBy "+res["developer"]+"\n\nSummary: "+res['summary']+"\n\n[link]("+res["url"]+")")
    
@register(outgoing=True, pattern="^\.yt (.*)")
async def yt_search(yts):
    """ For .yt command, do a YouTube search from Telegram. """
    query = yts.pattern_match.group(1)
    result = ''

    if not YOUTUBE_API_KEY:
        await yts.edit(
            "`Error: YouTube API key missing! Add it to environment vars or config.env.`"
        )
        return

    await yts.edit("`Processing...`")

    full_response = await youtube_search(query)
    videos_json = full_response[1]

    for video in videos_json:
        title = f"{unescape(video['snippet']['title'])}"
        link = f"https://youtu.be/{video['id']['videoId']}"
        videoID = f"{video['id']['videoId']}"
        result += f"{title}\n{link}\n`{videoID}`\n\n"

    reply_text = f"**Search Query:**\n`{query}`\n\n**Results:**\n\n{result}"

    await yts.edit(reply_text)

async def youtube_search(query,
                         order="relevance",
                         token=None,
                         location=None,
                         location_radius=None):
    """ Do a YouTube search. """
    youtube = build('youtube',
                    'v3',
                    developerKey=YOUTUBE_API_KEY,
                    cache_discovery=False)
    search_response = youtube.search().list(
        q=query,
        type="video",
        pageToken=token,
        order=order,
        part="id,snippet",
        maxResults=10,
        location=location,
        locationRadius=location_radius).execute()

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append(search_result)
    try:
        nexttok = search_response["nextPageToken"]
        return (nexttok, videos)
    except HttpError:
        nexttok = "last_page"
        return (nexttok, videos)
    except KeyError:
        nexttok = "KeyError, try again."
        return (nexttok, videos)
        
@register(outgoing=True, pattern="^\.ytv (.*)")
async def yt_video(ytv):
    """ For .play command, fetch content from Play Store. """
    await ytv.edit("`Finding...`")
    query = ytv.pattern_match.group(1)
    ydl = YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    with ydl:
        result = ydl.extract_info(
            'http://www.youtube.com/watch?v='+query,
            download=False # We just want to extract the info
        )

    if 'entries' in result:
        # Can be a playlist or a list of videos
        video = result['entries'][0]
    else:
        # Just a video
        video = result

    video_url = video['title']
    video_up = video['uploader']
    video_l = video['like_count']
    video_dl = video['dislike_count']
    video_v = video['view_count']
    video_desc = video['description']
    if video_l == None:
        video_l = "∞"
    if video_dl == None:
        video_dl = "∞"
    if video_v == None:
        video_v = "∞"
    if video_desc == None:
        video_desc = "none"
    ans_data = f"**{video_url}**\n\nBy {video_up}\n\n__{video_v} views, {video_l} likes and {video_dl} dislikes__\n\nDescription:\n{video_desc}"
    if len(ans_data) > 1024:
        ans_data = ans_data[0:1024] + "..."
    await ytv.edit(ans_data)
    
    
@register(outgoing=True, pattern=r"^\.google (.*)")
async def gsearch(q_event):
    await q_event.edit("`Processing...`")
    match = q_event.pattern_match.group(1)
    page = findall(r"page=\d+", match)
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
    except IndexError:
        page = 1
    search_args = (str(match), int(page))
    gsearch = GoogleSearch()
    gresults = await gsearch.async_search(*search_args)
    msg = ""
    for i in range(len(gresults["links"])):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"[{title}]({link})\n`{desc}`\n\n"
        except IndexError:
            break
    await q_event.edit("**Search Query:**\n`" + match + "`\n\n**Results:**\n" +
                       msg,
                       link_preview=False)
                       

@register(outgoing=True, pattern=r"^\.tts(?: |$)([\s\S]*)")
async def text_to_speech(query):  # text to speech
    if not query.text[0].isalpha() and query.text[0] in ("."):
        textx = await query.get_reply_message()
        message = query.pattern_match.group(1)
        if message:
            pass
        elif textx:
            message = textx.text
        else:
            await query.edit("`Give a text or reply to a message for Text-to-Speech!`")
            return
        try:
            gTTS(message, LANG)
        except AssertionError:
            await query.edit('The text is empty.\nNothing left to speak after pre-precessing, tokenizing and cleaning.')
            return
        except ValueError:
            await query.edit('Language is not supported.')
            return
        except RuntimeError:
            await query.edit('Error loading the languages dictionary.')
            return
        tts = gTTS(message, LANG)
        tts.save("k.mp3")
        with open("k.mp3", "rb") as audio:
            linelist = list(audio)
            linecount = len(linelist)
        if linecount == 1:
            tts = gTTS(message, LANG)
            tts.save("k.mp3")
        with open("k.mp3", "r"):
            await query.client.send_file(query.chat_id, "k.mp3", voice_note=True)
            os.remove("k.mp3")
            if BOTLOG:
                await query.client.send_message(BOTLOG_CHATID, "tts of `" + message + "` executed successfully!")
            await query.delete()


@register(outgoing=True, pattern=r"^\.trt(?: |$)([\s\S]*)")
async def translateme(trans):  # translator
    if not trans.text[0].isalpha() and trans.text[0] in ("."):
        translator = Translator()
        textx = await trans.get_reply_message()
        message = trans.pattern_match.group(1)
        if message:
            pass
        elif textx:
            message = textx.text
        else:
            await trans.edit("`Give a text or reply to a message to translate!`")
            return
        try:
            reply_text = translator.translate(deEmojify(message), dest=LANG)
        except ValueError:
            await trans.edit("Invalid destination language.")
            return
        source_lan = LANGUAGES[f'{reply_text.src.lower()}']
        transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
        reply_text = f"From **{source_lan.title()}**\nTo **{transl_lan.title()}:**\n\n{reply_text.text}"
        await trans.edit(reply_text)
        if BOTLOG:
            await trans.client.send_message(BOTLOG_CHATID,
                                            f"Translated some {source_lan.title()} stuff to {transl_lan.title()} just now.")


def deEmojify(inputString):  # removes emojis for safe string handling
    return get_emoji_regexp().sub(u'', inputString)


CMD_HELP.update({
    'scrapers':
        '`.currency <amount> <from> <to>`\
         \nUsage: Converts various currencies for you.\
         \n\n`.ud <text>`\
         \nUsage: Does a search on Urban Dictionary.\
         \n\n`.yt <text>`\
         \nUsage: Does a search on YouTube.\
         \n\n`.ytv <videoID>`\
         \nUsage: Shows YouTube video informations.\
         \n\n`.google <text>`\
         \nUsage: Does a search on Google.\
         \n\n`.play <packageID>`\
         \nUsage: Does a search on Play Store. \
         \n\n`.tts <text> [or reply]`\
         \nUsage: Translates text to speech for the default language which is set.\nUse .lang <text> to set language for your TTS.\
         \n\n`.trt <text> [or reply]`\
         \nUsage: Translates text to the default language which is set.'})
