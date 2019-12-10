import discord
from discord.ext import commands


class SnowFlake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def timestamp(self, ctx, id: int):
        """指定されたIDから時刻情報を取得します。
        IDには、役職やメッセージ、チャンネルなどのIDを指定できます。"""
        if not 17 <= len(str(id)) <= 18:
            await ctx.send("IDが不正です。")
            return

        await ctx.send(discord.utils.snowflake_time(id))


def setup(bot):
    return bot.add_cog(SnowFlake(bot))
