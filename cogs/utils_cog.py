from discord.ext import commands
from .utils.text import clean_mention
from extracommands import command, group
import asyncio
import discord
import datetime


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

    @command()
    async def last_message(self, ctx):
        await ctx.send((await ctx.channel.history(limit=2).flatten())[-1].jump_url)

    @command()
    async def topic(self, ctx):
        await ctx.send(ctx.channel.topic)

    @command()
    async def invite(self, ctx):
        await ctx.send('https://discordapp.com/api/oauth2/authorize?'
                       'client_id=622926597351145485&permissions=84032&scope=bot')

    @command()
    async def guildname(self, ctx):
        await ctx.send(ctx.guild.name)

    @command()
    async def nickname(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await ctx.send(member.display_name)

    @command()
    @commands.guild_only()
    async def joined_at(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        await ctx.send(member.joined_at)

    @command()
    async def timer(self, ctx):
        if 'timer' not in ctx.pipe_data.keys():
            ctx.pipe_data['timer'] = datetime.datetime.now()
        else:
            now = datetime.datetime.now()
            await ctx.send(now.timestamp() - ctx.pipe_data['timer'].timestamp())
            del ctx.pipe_data['timer']

    @command()
    async def content(self, ctx, message: discord.Message):
        await ctx.send(message.clean_content)


def setup(bot):
    return bot.add_cog(Utils(bot))
