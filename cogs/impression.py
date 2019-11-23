from discord.ext import commands
import discord
from .utils.database import Impression as DB_Impression


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

        await DB_Impression.create(
            user_id=message.author.id,
            count=1,
            type=f'reaction:{payload.emoji}',
            message_id=payload.message_id,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        message: discord.Message = await self.bot.check_alias(message)

        context = await self.bot.get_context(message)
        if context.command:
            return

        for user in message.mentions:
            await DB_Impression.create(
                user_id=user.id,
                count=2,
                type=f'message',
                message_id=message.id,
            )


def setup(bot):
    return bot.add_cog(Impression(bot))

