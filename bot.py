import os
import aiohttp
import json
import io
import discord
from discord.ext import commands
from cogs.utils.checks import check_command_permission
from cogs.utils.database import db, Alias, CommandHistory
from cogs.utils.helpcommand import PaginatedHelpCommand
import traceback


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

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.MissingRequiredArgument):
            await context.send('引数が足りません。')
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.CommandOnCooldown):
            await context.send('クールダウン中です。時間をおいて実行してください。')
        else:
            traceback.print_exc()

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

    async def set_command_history(self, context: commands.Context):
        await CommandHistory.create(user_id=context.author.id,
                                    command=self.get_command_full_name(context.command),
                                    channel_id=context.channel.id,
                                    guild_id=0 if context.guild else context.guild.id,
                                    timestamp=context.message.created_at.timestamp(),
                                    )
        channel = self.get_channel(583290964043366411)
        embed = discord.Embed(title=f'コマンド:{self.get_command_full_name(context.command)}',
                              description=f'guild={context.guild}\nユーザー{context.author}')
        if context.guild:
            embed.add_field(name='チャンネル', value=f'カテゴリー: {context.channel.category}: {context.channel.name}')
        embed.add_field(name='コマンド内容', value=f'`{context.message.content}`')
        embed.add_field(name='リンク', value=f'{context.channel.mention} [メッセージリンク]({discord.Message.jump_url})')
        await channel.send(embed=embed)

    async def on_message(self, message):
        if message.author.bot:
            return

        message = await self.check_alias(message)

        context = await self.get_context(message)
        if not context.command:
            return

        if await check_command_permission(context):
            await self.invoke(context)
            await self.set_command_history(context)

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
