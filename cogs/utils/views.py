from discord import Embed
GO_REACTION = "\N{BLACK RIGHT-POINTING TRIANGLE}"
BACK_REACTION = "\N{BLACK LEFT-POINTING TRIANGLE}"
STOP_REACTION = "\N{BLACK SQUARE FOR STOP}"


class ListView:
    page = 0
    embed = None
    message = None

    def __init__(self, ctx, title: str, description: str, data: list, per_page=4):
        """
        :param ctx: commands.Context
        :param title: str
        :param description: str
        :param data: [(name, value), (name, value), ...]
        :param per_page:
        """
        self.ctx = ctx
        self.title = title
        self.description = description
        self.data = data
        self.per_page = per_page
        self.bot = ctx.bot
        self.max_page = len(data) // per_page

    def create_embed(self):
        embed = Embed(title=self.title, description=self.description, color=0x00bfff)
        for entry in self.data[self.page: self.page + self.per_page]:
            embed.add_field(name=entry[0], value=entry[1], inline=False)

        self.embed = embed

    def check(self, reaction, member):
        if not member.id == self.ctx.author.id:
            return False

        if not str(reaction.emoji) in (GO_REACTION, BACK_REACTION):
            return False

        return True

    async def task(self):
        while not self.bot.is_closed():
            self.create_embed()

            if not self.message:
                self.message = await self.ctx.send(embed=self.embed)

            await self.ctx.message.add_reaction(BACK_REACTION)
            await self.ctx.message.add_reaction(GO_REACTION)
            await self.ctx.message.add_reaction(STOP_REACTION)

            reaction, member = await self.bot.wait_for('reaction_add', check=self.check, timeout=120)
            emoji = str(reaction.emoji)

            if emoji == GO_REACTION:
                if not self.page == self.max_page:
                    self.page += 4
            elif emoji == BACK_REACTION:
                if self.page:
                    self.page -= 4
            elif emoji == STOP_REACTION:
                await self.message.delete()
                return

    async def send(self):
        self.bot.loop.create_task(self.task())
