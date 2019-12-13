from discord.ext import commands
import discord
from extracommands import core
from typing import Union
from .utils.database import Impression as DB_Impression
import datetime


class Impression(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        imp = await DB_Impression.query.where(DB_Impression.user_id == message.author.id).\
            where(DB_Impression.message_id == payload.message_id).\
            where(DB_Impression.type == f'reaction:{payload.emoji}').gino.first()
        if imp:
            return

        if message.author.id == payload.user_id:
            return
        if message.author.bot:
            return
        payload_user = self.bot.get_user(payload.user_id)
        if payload_user.bot:
            return

        await DB_Impression.create(
            user_id=message.author.id,
            count=1,
            type=f'reaction:{payload.emoji}',
            message_id=payload.message_id,
            timestamp=datetime.datetime.now().timestamp()
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        message: discord.Message = await self.bot.check_alias(message)

        context = await self.bot.get_context(message)
        if context.command:
            return

        for user in set(message.mentions):
            await DB_Impression.create(
                user_id=user.id,
                count=2,
                type=f'message',
                message_id=message.id,
                timestamp=datetime.datetime.now().timestamp()
            )

    @core.group(aliases=['imp'])
    async def impression(self, ctx, user: Union[discord.Member, discord.User] = None):
        if not user:
            user = ctx.author

        impressions = await DB_Impression.query.where(DB_Impression.user_id == user.id).gino.all()
        count = sum([imp.count for imp in impressions])
        await ctx.send(f'あなたのインプレッション数は{count}です。')


def setup(bot):
    return bot.add_cog(Impression(bot))

