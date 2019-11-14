from discord.ext import commands
import random
import numpy as np


class Teaming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def teaming(self, ctx, team_count: int, *, team_members):
        """チーム分け用コマンドです。サブコマンド無しだと指定した数のチームにメンションで指定したユーザーをランダムに振り分けます。"""
        members = ctx.message.mentions
        random.shuffle(members)

        if len(members) < team_count:
            await ctx.send('チームの数に対してユーザーの数が足りません。')
            return

        text = ""

        teams = np.array_split(members, team_count)
        for i, team in enumerate(teams, start=1):
            text += '`--- チーム{0} ---`\n{1}\n'.format(i, '\n'.join([user.mention for user in team]))

        await ctx.send(text)

    @teaming.command()
    async def voice(self, ctx, team_count: int):
        """コマンドを打ったユーザーが入っているボイスチャンネルにいるbot以外のユーザーを指定した数のチームに分けます。"""
        if not ctx.author.voice:
            await ctx.send('ボイスチャンネルに接続していません。')
            return

        voice_channel = ctx.author.voice.channel
        members = [member for member in voice_channel.members if not member.bot]
        random.shuffle(members)

        text = ""

        teams = np.array_split(members, team_count)
        for i, team in enumerate(teams, start=1):
            text += '`--- チーム{0} ---`\n{1}\n'.format(i, '\n'.join([user.mention for user in team]))

        await ctx.send(text)


def setup(bot):
    return bot.add_cog(Teaming(bot))