import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord import ui
import os
from dotenv import load_dotenv
import pandas as pd
import asyncio
import time
import csv
import json
import requests
import datetime
from PIL import Image
import shutil
from io import BytesIO
import pprint
import re
from collections import defaultdict, deque
import wave

load_dotenv()

TOKEN = os.environ['token']
server = os.environ['server']
consoleChannel = os.environ['consoleChannel']

intents = discord.Intents.default()  # 適当に。
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await send_console("起動しました")


async def send_console(message):
    guild = client.get_guild(int(server))
    channel = guild.get_channel(int(consoleChannel))
    await channel.send(message)

try:
    client.run(TOKEN)
except Exception as e:
    send_console(e)
