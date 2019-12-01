from discord.ext import commands
from pathlib import Path
import discord
import json


class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactions = {}

        self.path = Path.cwd()/'jsons'/'reaction.json'
        if self.path.exists():
            with self.path.open() as f:
                self.reactions = json.load(f)

    def reaction_check(self, payload):
        if payload.message_id not in self.reactions.keys():
            return False
        if str(payload.emoji) not in self.reactions[payload.message_id].keys():
            return False
        if not payload.guild_id:
            return False
        return True

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not self.reaction_check(payload):
            return
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot:
            return
        role = guild.get_role(self.reactions[payload.message_id][str(payload.emoji)])
        if not role:
            return
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if not self.reaction_check(payload):
            return
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot:
            return
        role = guild.get_role(self.reactions[payload.message_id][str(payload.emoji)])
        if not role:
            return
        await member.remove_roles(role)

    @commands.command(name='reactionrole')
    async def reaction_role(self, ctx, message: discord.Message, *selects):
        """指定したメッセージにリアクションをつけたときにどの役職を付与する・消した時に剥奪するか設定できます。
        messageにはメッセージへのurl、selectsには `絵文字 付与する役職名 絵文字 付与する役職名`と入力してください。"""
        payload = {}
        selects = list(selects)
        if len(selects) % 2:
            await ctx.send('対応しない絵文字もしくは役職があります。')
            return

        while selects:
            emoji = self.bot.get_emoji(selects.pop(0))
            role_name = selects.pop(0)
            role = discord.utils.get(ctx.guild.roles, name=role_name)

            if not role:
                await ctx.send(f'{role_name}という名前の役職はありません。')
                return
            elif not emoji:
                await ctx.send(f'不明な絵文字が渡されました。botが入っていないサーバーの絵文字の可能性があります。')
                return
            payload[str(emoji)] = role.id
            try:
                await message.add_reaction(emoji)
            except Exception:
                pass

        self.reactions[message.id] = payload

        with self.path.open('w') as f:
            json.dump(self.reactions, f)

        await ctx.send('完了しました。')


def setup(bot):
    return bot.add_cog(Reaction(bot))
