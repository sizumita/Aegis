from discord.ext import commands
from extracommands import core
import discord
from .utils.database import Alias as _Alias


class Alias(commands.Cog):
    already_on = True

    def __init__(self, bot):
        self.bot = bot

    @core.group(invoke_without_command=True)
    async def alias(self, ctx):
        """エイリアスの一覧を表示・作成・削除します。"""

    @alias.command(aliases=['new'])
    async def add(self, ctx, name, *, command):
        """エイリアスを作成します。名前にスペースを入れたい場合は"もしくは'で囲ってください。"""
        alias = await _Alias.query.where(_Alias.user_id == ctx.author.id).where(_Alias.name == name).gino.first()
        if alias:
            await alias.update(command=command).apply()
        else:
            await _Alias.create(user_id=ctx.author.id, name=name, command=command)

        await ctx.send(f'エイリアス:`{name}`は作成されました。')

    @alias.command(aliases=['del'])
    async def delete(self, ctx, *, name):
        """エイリアスを削除します。"""
        alias = await _Alias.query.where(_Alias.user_id == ctx.author.id).where(_Alias.name == name).gino.first()
        if not alias:
            await ctx.send('作成されていません。')
            return

        await alias.delete()
        await ctx.send('削除しました。')

    @alias.command(name='list')
    async def _list(self, ctx):
        """エイリアスの一覧を表示します。"""
        aliases = await _Alias.query.where(_Alias.user_id == ctx.author.id)\
            .where(_Alias.user_id == ctx.author.id).gino.all()
        description = ''
        for alias in aliases:
            description += f'`{alias.name}`: `{alias.command}`\n'
        embed = discord.Embed(title='エイリアス一覧', description=description)

        await ctx.send(embed=embed)


def setup(bot):
    return bot.add_cog(Alias(bot))
