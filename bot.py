from discord.ext import commands
import discord
import os
import json


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('!')
        base.append('?')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['!', '?']))
    return base


class Aegis(commands.Bot):
    prefixes = {}

    def __init__(self, **options):
        super().__init__(_prefix_callable, **options)

        if os.path.exists('./prefixes.json'):
            with open('./prefixes.json', 'r') as f:
                self.prefixes = json.load(f)

    async def logout(self):
        await super().logout()
        with open('prefixes.json', 'w', encoding='utf-8') as f:
            json.dump(self.prefixes, f, indent=4)
