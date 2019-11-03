from bot import Aegis
import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

cogs = [f"cogs.{path[:-3]}" for path in os.listdir('./cogs')]

aegis = Aegis()


async def setup():
    await aegis.db.set_bind(os.environ.get('DATABASE'))
    await aegis.db.gino.create_all()

aegis.loop.create_task(setup())

aegis.run(os.environ.get('TOKEN'))
