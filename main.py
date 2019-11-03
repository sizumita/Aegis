from bot import Aegis
import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

cogs = [f"cogs.{path[:-3]}" for path in os.listdir('./cogs')]

aegis = Aegis()

aegis.run(os.environ.get('TOKEN'))
