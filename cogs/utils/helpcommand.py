import asyncio
import itertools

import discord
from discord.ext import commands
from .context import FakeContext
from .checks import check_command_permission
from .paginator import Pages


class HelpPaginator(Pages):
    title = None
    description = None

    def __init__(self, help_command, ctx, entries, *, per_page=4):
        super().__init__(ctx, entries=entries, per_page=per_page)
        self.ctx = ctx
        self.reaction_emojis.append(('\N{WHITE QUESTION MARK ORNAMENT}', self.show_bot_help))
        self.total = len(entries)
        self.help_command = help_command
        self.prefix = help_command.clean_prefix
        self.is_bot = False

    def get_bot_page(self, page):
        cog, description, commands = self.entries[page - 1]
        self.title = f'{cog} Commands'
        self.description = description
        return commands

    async def prepare_embed(self, entries, page, *, first=False):
        self.embed.clear_fields()
        self.embed.description = self.description
        self.embed.title = self.title

        if self.is_bot:
            value = (f'**コマンド名に打ち消し線が引かれているコマンドは実行できません!**\n実行したい場合は管理人に有効化を求めてください。\n'
                     f'さらにヘルプが必要であれば、 @すみどら#8923 まで。')
            self.embed.add_field(name='Support', value=value, inline=False)

        self.embed.set_footer(text=f'コマンドの詳細は"{self.prefix}help コマンド名" を使用してください。')

        for entry in entries:
            if await check_command_permission(FakeContext(entry.cog, entry, self.author, self.ctx.guild,
                                                          self.permissions, self.channel, self.ctx.bot)):
                signature = f'{entry.qualified_name} {entry.signature}'
            else:
                signature = f'~~{entry.qualified_name} {entry.signature}~~'

            if entry.short_doc:
                doc = entry.short_doc
                if isinstance(entry, commands.Group):
                    doc += f'\n詳しい詳細は`{self.prefix}help {entry.qualified_name}`で確認してください。'
            else:
                doc = "説明はありません。"

            self.embed.add_field(name=f'**{signature}**', value=doc, inline=False)

        if self.maximum_pages:
            self.embed.set_author(name=f'ページ {page}/{self.maximum_pages} ({self.total} commands)')

    async def show_help(self):
        """このメッセージを表示します"""

        self.embed.title = 'ページングヘルプ'
        self.embed.description = 'やあ！ヘルプページへようこそ。'

        messages = [f'{emoji} {func.__doc__}' for emoji, func in self.reaction_emojis]
        self.embed.clear_fields()
        self.embed.add_field(name='リアクションの意味は？', value='\n'.join(messages), inline=False)

        self.embed.set_footer(text=f'ページ {self.current_page} からジャンプしました。')
        await self.message.edit(embed=self.embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def show_bot_help(self):
        """Botの使い方を表示します。"""

        self.embed.title = 'Botを使用する'
        self.embed.description = 'やあ！ヘルプページへようこそ。'
        self.embed.clear_fields()

        entries = (
            ('<引数>', 'これは**必ず必要**という意味です。'),
            ('[引数]', 'これは**オプション**という意味です。'),
            ('[A|B]', 'これは**AもしくはB**ではなければいけないという意味です。'),
            ('[引数...]', 'これは引数が複数行という意味です。\n' \
                              'これらが基本です、しかし気をつけてください...\n' \
                              '__**括弧は必要ありません！**__')
        )

        self.embed.add_field(name='Botの使い方は？', value='Botの署名の読み取りは非常に簡単です。')

        for name, value in entries:
            self.embed.add_field(name=name, value=value, inline=False)

        self.embed.set_footer(text=f'ページ {self.current_page} からジャンプしました。')
        await self.message.edit(embed=self.embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())


class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'cooldown': commands.Cooldown(1, 3.0, commands.BucketType.member),
            'help': 'Bot、コマンド、カテゴリーのヘルプを表示します。'
        })

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        def key(c):
            return c.cog_name or '\u200bNo Category'

        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True, key=key)
        nested_pages = []
        per_page = 9
        total = 0

        for cog, commands in itertools.groupby(entries, key=key):
            commands = sorted(commands, key=lambda c: c.name)
            if len(commands) == 0:
                continue

            total += len(commands)
            actual_cog = bot.get_cog(cog)
            # get the description if it exists (and the cog is valid) or return Empty embed.
            description = (actual_cog and actual_cog.description) or discord.Embed.Empty
            nested_pages.extend((cog, description, commands[i:i + per_page]) for i in range(0, len(commands), per_page))

        # a value of 1 forces the pagination session
        pages = HelpPaginator(self, self.context, nested_pages, per_page=1)

        # swap the get_page implementation to work with our nested pages.
        pages.get_page = pages.get_bot_page
        pages.is_bot = True
        pages.total = total
        await pages.paginate()

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        pages = HelpPaginator(self, self.context, entries)
        pages.title = f'{cog.qualified_name} Commands'
        pages.description = cog.description

        await pages.paginate()

    def common_command_formatting(self, page_or_embed, command):
        page_or_embed.title = self.get_command_signature(command)
        if command.description:
            page_or_embed.description = f'{command.description}\n\n{command.help}'
        else:
            page_or_embed.description = command.help or 'ヘルプはありません...'

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour.blurple())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        pages = HelpPaginator(self, self.context, entries)
        self.common_command_formatting(pages, group)

        await pages.paginate()

