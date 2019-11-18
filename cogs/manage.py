from discord.ext import commands
from discord.ext.commands import Cog, Context, Bot, check
from .utils.checks import check_command_permission
from .utils.context import FakeContext
from .utils.database import is_exist, create, get, add_role, add_user, delete, \
    CommandPermission, delete_role, delete_user
from bot import Aegis
from typing import Union
import discord


def admin_only():
    def predicate(ctx):
        permissions: discord.Permissions = ctx.author.guild_permissions

        if not permissions.administrator:
            return False
        return True

    return check(predicate)


def can_change_permission(command):
    if command.cog_name == "Manage" or command.qualified_name == "help":
        return False
    return True


class Manage(Cog):
    def __init__(self, bot: Aegis):
        self.bot = bot

    def get_command(self, name):
        names = name.split(' ')
        try:
            command = self.bot.get_command(names.pop(0))
            if isinstance(command, commands.Group):
                for name in names:
                    command = command.get_command(name)
        except Exception:
            command = None

        return command

    @commands.command()
    async def usage(self, ctx):
        """このBOTの使用方法や設定方法などを表示します。"""

    @commands.group(aliases=['cmd'], invoke_without_command=True)
    @commands.guild_only()
    async def command(self, ctx: Context, *, command_name):
        """コマンドの有効化・無効化、表示用のコマンドです。
        引数にコマンド名を入れるとコマンドの詳細を表示します。"""
        command = self.get_command(command_name)

        if command is None:
            await ctx.send('そのようなコマンドはありません.')
            return

        can_use = await check_command_permission(
            FakeContext(command.cog, command, ctx.author, ctx.guild, ctx.author.guild_permissions, ctx.channel, ctx.bot
                        ))

        embed = discord.Embed(title='使用可能' if can_use else '使用不可能',
                              description=f"`{command.qualified_name} {command.signature}`\n{command.short_doc or ''}",
                              color=0x00bfff if can_use else 0xFF0000)
        embed.set_author(name=f'Command: {command.qualified_name}の詳細')

        if isinstance(command, commands.Group):
            embed.add_field(name='サブコマンド', value=f'`{", ".join(cmd.qualified_name for cmd in command.commands)}`',
                            inline=False)

        embed.set_footer(text='権限の変更は"admit"コマンドを使用してください')

        await ctx.send(embed=embed)

    @command.group(aliases=['allow'], invoke_without_command=True)
    @admin_only()
    async def enable(self, ctx: Context, *, command_name):
        """コマンドを有効化します。大文字から始めるとCogの名前とみなされ、そのCogのコマンドが全て有効化されます。（例: `cmd allow Math`）"""
        if not command_name[0].isupper():
            command = self.bot.get_command(command_name)

            if command is None:
                await ctx.send('そのようなコマンドはありません.')
                return

            if not can_change_permission(command):
                await ctx.send('そのコマンドは変更できません.')

            name = self.bot.get_command_full_name(command)
            if await is_exist(ctx.guild.id, name):
                await ctx.send('そのコマンドは有効化されています.')
                return

            await create(ctx.guild.id, name)
            await ctx.send(f'コマンド:{command.name}を有効化しました.')
        else:
            cog = self.bot.get_cog(command_name)

            if cog is None:
                await ctx.send('そのようなCogはありません。')
                return
            changed_commands = []

            for command in cog.get_commands():
                if not can_change_permission(command):
                    continue

                name = self.bot.get_command_full_name(command)
                if await is_exist(ctx.guild.id, name):
                    continue

                await create(ctx.guild.id, name)
                changed_commands.append(command)

            await ctx.send('コマンド:' + ','.join([f'`{_.qualified_name}`' for _ in changed_commands]) + 'を有効化しました。')

    @enable.command(name='all')
    async def enable_all(self, ctx):
        """全てのコマンドを有効化します。"""
        for command in self.bot.walk_commands():
            name = self.bot.get_command_full_name(command)
            if await is_exist(ctx.guild.id, name):
                continue

            await create(ctx.guild.id, name)

        await ctx.send('有効化されていないコマンドを全て有効化しました。')

    @command.group(aliases=['deny'], invoke_without_command=True)
    @admin_only()
    async def disable(self, ctx: Context, *, command_name):
        """コマンドを無効化します。設定した権限は初期化されます。
        大文字から始めるとCogの名前とみなされ、そのCogのコマンドが全て無効化されます（例: `cmd deny Math`）。"""

        if not command_name[0].isupper():

            command = self.bot.get_command(command_name)

            if command is None:
                await ctx.send('そのようなコマンドはありません.')
                return

            if not can_change_permission(command):
                await ctx.send('そのコマンドは変更できません。')

            name = self.bot.get_command_full_name(command)
            if not await is_exist(ctx.guild.id, name):
                await ctx.send('そのコマンドは有効化されていません。')
                return

            await delete(ctx.guild.id, name)
            await ctx.send(f'コマンド:{command.name}を無効化しました.')

        else:
            cog = self.bot.get_cog(command_name)

            if cog is None:
                await ctx.send('そのようなCogはありません。')
                return
            changed_commands = []

            for command in cog.get_commands():
                if not can_change_permission(command):
                    continue

                name = self.bot.get_command_full_name(command)
                if not await is_exist(ctx.guild.id, name):
                    continue

                await delete(ctx.guild.id, name)
                changed_commands.append(command)

            await ctx.send('コマンド:' + ','.join([f'`{_.qualified_name}`' for _ in changed_commands]) + 'を無効化しました。')

    @disable.command(name='all')
    async def disable_all(self, ctx):
        """全てのコマンドを無効化します。"""
        for command in self.bot.walk_commands():
            name = self.bot.get_command_full_name(command)
            if not await is_exist(ctx.guild.id, name):
                continue

            await delete(ctx.guild.id, name)

        await ctx.send('有効化されているコマンドを全て無効化しました。')

    @commands.group()
    @commands.guild_only()
    @admin_only()
    async def permit(self, ctx):
        """コマンドの権限を変更します。サブコマンドの指定が可能です。"""

    @permit.group()
    async def role(self, ctx, action, role: discord.Role, *, command_name):
        """役職を設定・解除します。役職のメンションまたはid、名前で指定可能です。
        actionが[set, add, new]で追加、[reset, remove, delete]で削除を行います。
        役職の名前に空白がある場合はクォーテーションで囲ってください。"""
        command = self.get_command(command_name)

        if command is None:
            await ctx.send('そのようなコマンドはありません.')
            return

        if action in ['set', 'add', 'new']:
            r = await add_role(ctx.guild.id, self.bot.get_command_full_name(command), role.id)
            if r is None:
                await ctx.send('コマンドが有効化されていません。')
                return
            elif not r:
                await ctx.send('すでに追加されています。')
                return

            await ctx.send(f'役職:`{role}`が追加されました。')

        elif action in ['reset', 'remove', 'delete', 'del']:
            r = await delete_role(ctx.guild.id, self.bot.get_command_full_name(command), role.id)

            if r is None:
                await ctx.send('コマンドが有効化されていません。')
                return
            elif not r:
                await ctx.send('追加されていません。')
                return

            await ctx.send(f'役職:`{role}`が削除されました。')

        else:
            await ctx.send('不明なactionです。')

    @permit.group()
    async def user(self, ctx, action, user: Union[discord.User, discord.Member], *, command_name):
        """役職を設定・解除します。役職のメンションまたはid、名前で指定可能です。
        actionが[set, add, new]で追加、[reset, remove, delete]で削除を行います。
        役職の名前に空白がある場合はクォーテーションで囲ってください。"""
        command = self.get_command(command_name)

        if command is None:
            await ctx.send('そのようなコマンドはありません.')
            return

        if action in ['set', 'add', 'new']:
            r = await add_user(ctx.guild.id, self.bot.get_command_full_name(command), user.id)
            if r is None:
                await ctx.send('コマンドが有効化されていません。')
                return
            elif not r:
                await ctx.send('すでに追加されています。')
                return

            await ctx.send(f'ユーザー:`{user}`が追加されました。')

        elif action in ['reset', 'remove', 'delete', 'del']:
            r = await delete_user(ctx.guild.id, self.bot.get_command_full_name(command), user.id)

            if r is None:
                await ctx.send('コマンドが有効化されていません。')
                return
            elif not r:
                await ctx.send('追加されていません。')
                return

            await ctx.send(f'ユーザー:`{user}`が削除されました。')

        else:
            await ctx.send('不明なactionです。')


def setup(bot):
    return bot.add_cog(Manage(bot))
