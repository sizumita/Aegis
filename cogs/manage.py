from discord.ext import commands
from .utils.database import CommandPermission
import discord


class ManageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not ctx.guild:
            return True

        permissions: discord.Permissions = ctx.author.guild_permissions

        if not permissions.administrator:
            return False

        return True

    @commands.group(aliases=['cmd'], invoke_without_command=True)
    @commands.guild_only()
    async def command(self, ctx: commands.Context, command_name):
        """コマンドの有効化・無効化、表示用のコマンドです。
        引数にコマンド名を入れるとコマンドの詳細を表示します。"""

    @command.command(name='all')
    async def _all(self, ctx):
        """全てのコマンドを表示します。"""

    @command.command(aliases=['allow'])
    async def enable(self, ctx, command_name):
        """コマンドを有効化します。"""

    @command.command(aliases=['deny'])
    async def disable(self, ctx, command_name):
        """コマンドを無効化します。設定した権限は初期化されます。"""

    @commands.group(aliases=['permit'])
    @commands.guild_only()
    async def permission(self, ctx):
        """コマンドの権限を変更します。"""


def setup(bot):
    return bot.add_cog(ManageCog(bot))
