import os
import aiohttp
import json
import io
import discord
from discord.ext import commands

from cogs.utils.checks import check_command_permission
from cogs.utils.database import db
from cogs.utils.helpcommand import PaginatedHelpCommand


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('.')
        base.append(':')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['.', ':']))
    return base


class Aegis(commands.Bot):
    prefixes = {}

    def __init__(self):
        super().__init__(_prefix_callable, help_command=PaginatedHelpCommand())

        self.db = db

        if os.path.exists('./prefixes.json'):
            with open('./prefixes.json', 'r') as f:
                self.prefixes = json.load(f)

    async def logout(self):
        await super().logout()
        with open('prefixes.json', 'w', encoding='utf-8') as f:
            json.dump(self.prefixes, f, indent=4)

    async def on_message(self, message):

        if message.author.bot:
            return
        context = await self.get_context(message)
        if not context.command:
            return

        if await check_command_permission(context):
            await self.invoke(context)

    @staticmethod
    def get_command_full_name(command: commands.Command):
        name = f'{command.cog_name}.'
        _command = command.parent
        while _command:
            name += f'{_command.qualified_name}.'
            _command = _command.parent

        name += command.qualified_name

        return name

    @staticmethod
    async def get_json(url):
        async with aiohttp.ClientSession() as session:
            r = await session.get(url)

        return await r.json()

    @staticmethod
    async def get_image(url):
        async with aiohttp.ClientSession() as session:
            r = await session.get(url)

        buffer = io.BytesIO(await r.read())
        buffer.seek(0)
        return discord.File(fp=buffer, filename='image.png')
