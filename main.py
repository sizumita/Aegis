from bot import Aegis
import os
from os.path import join, dirname
from dotenv import load_dotenv
import discord
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

aegis = Aegis()

cogs = [f"cogs.{path[:-3]}" for path in os.listdir('./cogs') if path.endswith('.py')]

for cog in cogs:
    aegis.load_extension(cog)


@aegis.command()
async def ping(ctx):
    await ctx.send('pong!')


async def setup():
    await aegis.db.set_bind(os.environ.get('DATABASE'))
    await aegis.db.gino.create_all()

aegis.loop.create_task(setup())

aegis.run(os.environ.get('TOKEN'))
