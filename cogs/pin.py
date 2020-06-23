from discord.ext import commands
import discord
from extracommands import core


class Fun(commands.Cog):
    already_on = False

    def __init__(self, bot):
        self.bot = bot

    @core.command()
    async def pin(self, ctx, message: discord.Message):
        await message.pin()
        await ctx.send(f'pinned! -> {message.jump_url}')


def setup(bot):
    return bot.add_cog(Fun(bot))