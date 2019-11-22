import os
import aiohttp
import json
import io
import discord
import re
from discord.ext import commands
from cogs.utils.checks import check_command_permission
from cogs.utils.database import db, Alias
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

    async def rolling_presence(self):
        await self.wait_until_ready()
        presences = ['Aegis - A discord Bot', 'help -> .help', '']
        i = 0
        while not self.is_closed():
            break

    async def close(self):
        await super().close()
        with open('prefixes.json', 'w', encoding='utf-8') as f:
            json.dump(self.prefixes, f, indent=4)

    async def check_alias(self, message):
        aliases = await Alias.query.where(Alias.user_id == message.author.id).gino.all()
        prefix = [prefix for prefix in await self.get_prefix(message) if message.content.startswith(prefix)]
        if not prefix:
            return message

        all_content = message.content
        content = message.content.replace(prefix[0], '', 1)
        for alias in aliases:
            if content.startswith(alias.name):
                all_content = all_content.replace(alias.name, alias.command, 1)
                break
        message.content = all_content
        return message

    async def on_message(self, message):
        if message.author.bot:
            return

        message = await self.check_alias(message)

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
