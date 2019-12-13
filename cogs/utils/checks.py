from .database import CommandPermission
from discord.ext.commands import check
import discord


async def check_command_permission(context):
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

    #  manage系、ヘルプコマンドだった場合
    if context.command.name == 'help':
        return True

    elif context.cog:
        if context.cog.qualified_name == 'Manage':
            return True

    p: CommandPermission = await CommandPermission.query.where(CommandPermission.id == context.guild.id) \
        .where(CommandPermission.name == context.bot.get_command_full_name(context.command)).gino.first()

    #  ない場合
    if not p:

        if getattr(context.cog, 'already_on', False):
            p = await CommandPermission.create(id=context.guild.id,
                                               name=context.bot.get_command_full_name(context.command))
        else:
            return False

    if context.author.guild_permissions.administrator:
        return True

    #  制限なしの場合
    if not p.roles and not p.users:
        return True

    checks = []

    if p.roles:
        is_id_in = any(True for i in context.author.roles if str(i.id) in p.roles)

        checks.append(is_id_in)

    if p.users:
        checks.append(True if str(context.author.id) in p.users else False)

    return any(checks)


def admin_only():
    def predicate(ctx):
        permissions: discord.Permissions = ctx.author.guild_permissions

        if not permissions.administrator:
            return False
        return True

    return check(predicate)


def safety():
    """CommandPermissionがあってかつ何も設定されていないときにadminしか実行できないようにする"""

    async def predicate(ctx):
        p: CommandPermission = await CommandPermission.query.where(CommandPermission.id == ctx.guild.id) \
            .where(CommandPermission.name == ctx.bot.get_command_full_name(ctx.command)).gino.first()
        if not p:
            return False

        if not p.users and not p.roles:
            permissions: discord.Permissions = ctx.author.guild_permissions

            if not permissions.administrator:
                return False

        return True

    return check(predicate)
