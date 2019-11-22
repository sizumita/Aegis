import io
import re
import aiohttp
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from discord.ext import commands
from emoji import UNICODE_EMOJI
import discord


def resize(image: Image.Image, height=None):
    x = height / image.height
    return image.resize((int(image.width * x), int(image.height * x)))


def split_text(ctx, text: str):
    """
    :param ctx:
    :param text:
    :return: text [discord.Emoji, str, Tuple]
    """
    text_list = []
    while text:
        if text[0] in UNICODE_EMOJI:
            text_list.append((text[0],))
            text = text.replace(text[0], '', 1)
            continue

        if match := re.match('^<:.+:([0-9]+)>', text):
            emoji = ctx.bot.get_emoji(int(match.groups()[0]))
            if emoji:
                text_list.append(emoji)
                text = text.replace(f'<:{emoji.name}:{emoji.id}>', '', 1)
                continue

        elif match := re.match('^<a:.+:([0-9]+)>', text):
            emoji = ctx.bot.get_emoji(int(match.groups()[0]))
            if emoji:
                text_list.append(emoji)
                text = text.replace(f'<a:{emoji.name}:{emoji.id}>', '', 1)
                continue

        if not text_list:
            text_list.append(text[0])
            text = text.replace(text[0], '', 1)
            continue

        if isinstance(text_list[-1], str):
            text_list[-1] += text[0]
            text = text.replace(text[0], '', 1)
        else:
            text_list.append(text[0])
            text = text.replace(text[0], '', 1)

    return text_list


def to_bytes(image):
    output_buffer = io.BytesIO()
    image.save(output_buffer, "png")
    output_buffer.seek(0)
    return output_buffer


def get_draw(image, font, size):
    draw = ImageDraw.Draw(image)
    draw.font = ImageFont.truetype(font, size)
    return image, draw


async def get_unicode_emoji(emoji: str, h: int):
    # idから絵文字を取得
    code = f"{ord(emoji):x}"

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(f'https://bot.mods.nyc/twemoji/{code}.png') as response:
            image = Image.open(io.BytesIO(await response.read()))
    width, height = image.size
    persent = h / height
    image = image.resize((int(width * persent), h))
    return image


async def get_unique_emoji(emoji: discord.Emoji, h: int):
    # idから絵文字を取得

    if emoji.animated:
        image = Image.open(io.BytesIO(await emoji.url.read()))
        image.seek(0)
    else:
        image = Image.open(io.BytesIO(await emoji.url.read()))

    width, height = image.size
    persent = h / height
    image = image.resize((int(width * persent), h))
    return image


async def get_text(text, font='./cogs/utils/otf/CP Font.otf', size=100,
                   border="#23272A", border_width=1.2, color='#7289DA', background="",):
    image = Image.new("RGBA", (len(text) * size, int(size * 1.25)), background or (0, 0, 0, 0))
    image, draw = get_draw(image, font, size)

    w, h = draw.font.getsize(text)
    image = image.crop((0, 0, w, int(size * 1.25)))

    image, draw = get_draw(image, font, size)

    pos = (np.array(image.size) - np.array(draw.font.getsize(text))) / 2.
    bw = border_width

    draw.text(pos - (-bw, -bw), text, border)
    draw.text(pos - (-bw, +bw), text, border)
    draw.text(pos - (+bw, -bw), text, border)
    draw.text(pos - (+bw, +bw), text, border)

    draw.text(pos, text, fill=color)

    return image


async def draw(ctx: commands.Context, _text, **kwargs):
    size = kwargs.get('size', 100)
    text_list = split_text(ctx, _text)
    image_list = []
    for text in text_list:
        if isinstance(text, str):
            image_list.append(resize(await get_text(text, **kwargs), size))
            continue

        if isinstance(text, tuple):
            image_list.append(resize(await get_unicode_emoji(text[0], size), size))
            continue

        if isinstance(text, discord.Emoji):
            image_list.append(resize(await get_unique_emoji(text, size), size))

    image = Image.new('RGBA', (sum([i.width for i in image_list]), image_list[0].height), (0, 0, 0, 0))
    i = 0
    for img in image_list:
        image.paste(img, (i, 0))
        i += img.width

    return image


async def draw_string(ctx, _text, **kwargs):
    return to_bytes(await draw(ctx, _text, **kwargs))


async def draw_lines(ctx, _text, **kwargs):
    texts = _text.split('\n')
    images = []
    for text in texts:
        images.append(await draw(ctx, text, **kwargs))
    image = Image.new('RGBA', (sum([i.width for i in images]), sum([i.height for i in images])), (0, 0, 0, 0))
    h = 0
    for img in images:
        image.paste(img, (0, h))
        h += img.height

    return to_bytes(image)
