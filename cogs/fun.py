from discord.ext import commands
import discord
from extracommands import core


class Fun(commands.Cog):
    already_on = True

    def __init__(self, bot):
        self.bot = bot

    @core.command()
    async def ping(self, ctx):
        await ctx.send('pong!')

    @core.command()
    async def cat(self, ctx):
        """猫の画像を表示します。"""
        json = await self.bot.get_json('https://aws.random.cat/meow')
        url = json['file'].replace('\\', '')
        await ctx.send(url)

    @core.command()
    async def dog(self, ctx):
        """犬の画像を表示します。"""
        json = await self.bot.get_json('https://dog.ceo/api/breeds/image/random')
        url = json['message'].replace('\\', '')
        await ctx.send(url)

    @core.command()
    async def fox(self, ctx):
        """狐の画像を表示します。"""
        json = await self.bot.get_json('https://randomfox.ca/floof/')
        url = json['image'].replace('\\', '')
        await ctx.send(url)

    @core.command('yesno')
    @commands.cooldown(2, 20)
    async def yes_no(self, ctx):
        """
        YesかNoで答えてくれます。
        １万回に１回、maybeが返ることもあるらしい。
        """
        json = await self.bot.get_json('https://yesno.wtf/api')
        answer = json['answer']
        url = json['image']
        embed = discord.Embed(title=answer)
        embed.set_image(url=url)
        await ctx.send(embed=embed)


def setup(bot):
    return bot.add_cog(Fun(bot))
