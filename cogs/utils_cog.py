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
        await ctx.send(clean_mention(text[::-1]))

    @command()
    async def echo(self, ctx, *, text):
        await ctx.send(clean_mention(text))

    @command()
    async def grep(self, ctx, keyword, *, text):
        pass

    @command(receive_pipe=False)
    async def wait(self, ctx, wait_time: int):
        await asyncio.sleep(wait_time)


def setup(bot):
    return bot.add_cog(Utils(bot))
