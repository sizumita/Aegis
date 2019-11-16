from discord.ext import commands
import discord
keys = [
    '\N{REGIONAL INDICATOR SYMBOL LETTER A}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER D}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER G}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER J}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER M}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER P}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER S}',
    '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
]


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def vote(self, ctx, title, *choices):
        """投票を作成します。choicesには`選択肢をスペース区切りで入れてください。`"""
        embed = discord.Embed(title=title, color=0x00bfff)
        if len(choices) > 20:
            await ctx.send('選択肢は２０個までにしてください。')
            return

        using_emojis = []

        for key, choice in zip(keys, choices):
            embed.add_field(name=key, value=choice)
            using_emojis.append(key)

        msg = await ctx.send(embed=embed)
        for emoji in using_emojis:
            await msg.add_reaction(emoji)


def setup(bot):
    return bot.add_cog(Vote(bot))
