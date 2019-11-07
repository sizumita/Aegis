import discord


class FakeContext(discord.abc.Messageable):
    async def _get_channel(self):
        return self.channel

    def __init__(self, cog, command, author, guild, permissions, channel):
        self.guild = guild
        self.cog = cog
        self.command = command
        self.permissions = permissions
        self.author = author
        self.channel = channel
