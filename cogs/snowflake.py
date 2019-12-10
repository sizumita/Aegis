import discord
import datetime

class SnowFlake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def timestamp(self,ctx,id:int):
        """指定されたIDから時刻情報を取得します。
        IDには、役職やメッセージ、チャンネルなどのIDを指定できます。"""
        if len(str(id)) != 18:
            await ctx.send("IDが不正です。")
            return

        obj = discord.Object(id)
        await ctx.send(obj.created_at)

def setup(bot):
    return bot.add_cog(SnowFlake(bot))
