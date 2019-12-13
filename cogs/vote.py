from discord.ext import commands
import discord
from extracommands import core
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


class VoteData:
    def __init__(self, message, secret=False):
        self.message = message,
        self.secret = secret

    async def add_reaction(self, emoji):
        pass

    #  TODO: 処理書く


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.votes = {}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id in self.votes.keys():
            await self.votes[payload.message_id].add_reaction(str(payload.emoji))

    @core.group(invoke_without_command=True)
    @commands.guild_only()
    async def vote(self, ctx, title, *choices):
        """投票を作成します。choicesには`選択肢をスペース区切りで入れてください。`"""
        embed = discord.Embed(title=title, color=0x00bfff)
        if len(choices) > 20:
            await ctx.send('選択肢は２０個までにしてください。')
            return

        using_emojis = []

        for key, choice in zip(keys, choices):
            embed.add_field(name=key, value=choice, inline=False)
            using_emojis.append(key)

        msg = await ctx.send(embed=embed)
        for emoji in using_emojis:
            await msg.add_reaction(emoji)

    @vote.command()
    async def secret(self, ctx, title, *choices):
        """誰が投票したのかわからなくする秘匿投票用のコマンドです。choicesには`選択肢をスペース区切りで入れてください。`"""


def setup(bot):
    return bot.add_cog(Vote(bot))
