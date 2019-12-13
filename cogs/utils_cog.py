from discord.ext import commands
from .utils.text import clean_mention
from extracommands import command, group
import asyncio


class Utils(commands.Cog):
    already_on = True

    def __init__(self, bot):
        self.bot = bot

    @command()
    async def reverse(self, ctx, *, text):
        """与えられたテキストを反転します。"""
        await ctx.send(clean_mention(text[::-1]))

    @command()
    async def echo(self, ctx, *, text):
        """与えられたテキストをメンションを無効化して表示します。"""
        await ctx.send(clean_mention(text))

    @command()
    async def grep(self, ctx, keyword, *, text):
        pass

    @command()
    async def wait(self, ctx, wait_time: int):
        """指定した秒数動作を停止します。"""
        await asyncio.sleep(wait_time)


def setup(bot):
    return bot.add_cog(Utils(bot))
