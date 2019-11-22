from discord.ext import commands
import discord
from .utils.generating import draw_lines, draw_string


class Moji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def moji(self, ctx, *, text):
        """テキストを画像にして表示します。カスタム絵文字・ユニコード絵文字も使用可能です。複数行表示可能です。"""
        if '\n' in text:
            buffer = await draw_lines(ctx, text)
        else:
            buffer = await draw_string(ctx, text)

        await ctx.send(file=discord.File(buffer, filename='image.png'))

    @moji.command()
    async def discord(self, ctx, *, text):
        """Discordのロゴのフォントを使用します。英語・数字・記号のみ対応です。カスタム絵文字・ユニコード絵文字も使用可能です。複数行表示可能です。"""
        if '\n' in text:
            buffer = await draw_lines(ctx, text, font='./cogs/utils/otf/Uni Sans Heavy.otf')
        else:
            buffer = await draw_string(ctx, text, font='./cogs/utils/otf/Uni Sans Heavy.otf')

        await ctx.send(file=discord.File(buffer, filename='image.png'))


def setup(bot):
    return bot.add_cog(Moji(bot))
