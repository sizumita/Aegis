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
import sys
import asyncio
from extracommands import Bot


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('.')
        base.append(':')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['.', ':']))
    return base


class Aegis(Bot):
    prefixes = {}

    def __init__(self):
        super().__init__(_prefix_callable, help_command=PaginatedHelpCommand())

        self.db = db

        if os.path.exists('./prefixes.json'):
            with open('./prefixes.json', 'r') as f:
                self.prefixes = json.load(f)

        self.loop.create_task(self.rolling_presence())

    async def rolling_presence(self):
        await self.wait_until_ready()
        presences = ['Aegis - A discord Bot', 'help -> .help']
        i = 0
        while not self.is_closed():
            await self.change_presence(activity=discord.Game(name=presences[i]))
            await asyncio.sleep(5)

            if i == len(presences) - 1:
                i = 0
            else:
                i += 1

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.MissingRequiredArgument):
            await context.send('引数が足りません。')
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.CommandOnCooldown):
            await context.send('クールダウン中です。時間をおいて実行してください。')
        else:

            print('Ignoring exception in command {}:'.format(context.command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    async def close(self):
        await super().close()
        with open('prefixes.json', 'w', encoding='utf-8') as f:
            json.dump(self.prefixes, f, indent=4)

    async def check_alias(self, message):
        aliases = await Alias.query.where(Alias.user_id == message.author.id).gino.all()

        for alias in aliases:
            if message.content == alias.name:
                message.content = alias.command
                break

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
        try:
            await channel.send(embed=embed)
        except AttributeError:
            pass

    async def invoke_group(self, group):
        invoked_context = None
        for context in group.contexts:
            if invoked_context and invoked_context.pipe_contents:
                context.passed_pipe_content = '\n'.join(invoked_context.pipe_contents)
            await self.invoke(context)
            invoked_context = context
            await self.set_command_history(context)

    async def on_message(self, message):
        if message.author.bot:
            return

        message = await self.check_alias(message)

        _groups = []
        groups = await self.get_context_groups(message)
        for group in groups:
            _ = []
            for ctx in group.contexts:
                _.append(await check_command_permission(ctx))
            if all(_):
                _groups.append(group)

        for group in _groups:
            self.loop.create_task(self.invoke_group(group))

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
