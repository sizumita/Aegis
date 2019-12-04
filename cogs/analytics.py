from discord.ext import commands
import discord
import datetime
from .utils.database import VisitMemberAnalytics


class Analytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        await VisitMemberAnalytics.create(
            user_id=member.id,
            type='join',
            guild_id=member.guild.id,
            timestamp=member.joined_at.timestamp()
        )

    @commands.Cog.listener()
    async def on_member_left(self, member: discord.Member):
        if member.bot:
            return

        await VisitMemberAnalytics.create(
            user_id=member.id,
            type='remove',
            guild_id=member.guild.id,
            timestamp=datetime.datetime.now().timestamp()
        )


def setup(bot):
    bot.add_cog(Analytics(bot))
