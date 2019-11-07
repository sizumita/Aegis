from discord.ext import commands
from discord.ext.commands import Cog, Context, Bot, check
from .utils.checks import check_command_permission
from .utils.context import FakeContext
from .utils.database import is_exist, create, get, add_role, add_user, delete
from bot import Aegis
import discord


def admin_only():
    """A :func:`.check` that indicates this command must only be used in a
    guild context only. Basically, no private messages are allowed when
    using the command.

    This check raises a special exception, :exc:`.NoPrivateMessage`
    that is inherited from :exc:`.CheckFailure`.
    """

    def predicate(ctx):
        permissions: discord.Permissions = ctx.author.guild_permissions

        if not permissions.administrator:
            return False
        return True

    return check(predicate)


class Manage(Cog):
    def __init__(self, bot: Aegis):
        self.bot = bot

    @commands.command()
    async def usage(self, ctx):
        """このBOTの使用方法や設定方法などを表示します。"""

    @commands.group(aliases=['cmd'], invoke_without_command=True)
    @commands.guild_only()
    async def command(self, ctx: Context, *command_names):
        """コマンドの有効化・無効化、表示用のコマンドです。
        引数にコマンド名を入れるとコマンドの詳細を表示します。"""
        command_names = list(command_names)
        command = self.bot.get_command(command_names.pop(0))
        if isinstance(command, commands.Group):
            for name in command_names:
                command = command.get_command(name)

        if command is None:
            await ctx.send('そのようなコマンドはありません.')
            return

        can_use = await check_command_permission(
            FakeContext(command.cog, command, ctx.author, ctx.guild, ctx.author.guild_permissions, ctx.channel))

        embed = discord.Embed(title='使用可能' if can_use else '使用不可能',
                              description=f"`{command.qualified_name} {command.signature}`\n{command.short_doc or ''}",
                              color=0x00bfff if can_use else 0xFF0000)
        embed.set_author(name=f'Command: {command.qualified_name}の詳細')
        if isinstance(command, commands.Group):
            embed.add_field(name='サブコマンド', value=f'`{", ".join(cmd.qualified_name for cmd in command.commands)}`',
                            inline=False)

        await ctx.send(embed=embed)

    @command.command(aliases=['allow'])
    @admin_only()
    async def enable(self, ctx: Context, command_name: str):
        """コマンドを有効化します。"""
        command = self.bot.get_command(command_name)

        if command is None:
            await ctx.send('そのようなコマンドはありません.')
            return

        name = self.bot.get_command_full_name(command)
        if await is_exist(ctx.guild.id, name):
            await ctx.send('そのコマンドは有効化されています。')
            return

        await create(ctx.guild.id, name)

    @command.command(aliases=['deny'])
    @admin_only()
    async def disable(self, ctx: Context, command_name: str):
        """コマンドを無効化します。設定した権限は初期化されます。"""

        command = self.bot.get_command(command_name)

        if command is None:
            await ctx.send('そのようなコマンドはありません.')
            return

        name = self.bot.get_command_full_name(command)
        if not await is_exist(ctx.guild.id, name):
            await ctx.send('そのコマンドは有効化されていません。')
            return

        await delete(ctx.guild.id, name)


def setup(bot):
    return bot.add_cog(Manage(bot))
