import json
import os

import discord
from discord.ext import commands

from cogs.utils.database import db, CommandPermission


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('!')
        base.append('?')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['!', '?']))
    return base


async def check_command_permission(context: commands.Context):
    """
    権限周りについて:
        DMの場合確実に有効
        CommandPermissionがなければそもそも有効化されていない
        作成されていて、かつroles、users、permissionsが空であれば誰でも使える

    :param context: commands.Context
    :return: bool
    """

    #  DMの場合
    if not context.guild:
        return True

    p: CommandPermission = await CommandPermission.query.where(CommandPermission.id == context.guild.id) \
        .where(CommandPermission.name == context.command.name).gino.first()

    #  ない場合
    if not p:
        return False

    #  制限なしの場合
    if not p.roles and not p.users and not p.permissions:
        return True

    checks = []

    if p.roles:
        is_id_in = any(True for i in context.author.roles if str(i.id) in p.roles)

        checks.append(is_id_in)

    if p.users:
        checks.append(True if str(context.author.id) in p.users else False)

    if p.permissions:
        has_permission = any([True for value in p.permissions.split(',')
                              if discord.Permissions(int(value)).is_subset(context.author.guild_permissions)
                              ])

        checks.append(has_permission)

    return any(checks)


class Aegis(commands.Bot):
    prefixes = {}

    def __init__(self, **options):
        super().__init__(_prefix_callable, **options)

        self.db = db

        if os.path.exists('./prefixes.json'):
            with open('./prefixes.json', 'r') as f:
                self.prefixes = json.load(f)

    async def logout(self):
        await super().logout()
        with open('prefixes.json', 'w', encoding='utf-8') as f:
            json.dump(self.prefixes, f, indent=4)

    async def on_message(self, message):
        if message.author.bot:
            return

        context = await self.get_context(message)
        if not context:
            return

        if await check_command_permission(context):
            await self.invoke(context)
