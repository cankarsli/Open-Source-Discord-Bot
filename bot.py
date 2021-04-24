import discord
import contextlib
from discord.ext import commands, tasks
import random
from itertools import cycle
import os
import logging
import platform
import datetime
from pathlib import Path
import json
import cogs
from cogs._json import read_json
from discord import Color

import io

import textwrap
from traceback import format_exception

from utils.mongo import Document
from utils.util import clean_code, Pag

import motor.motor_asyncio

from discord.ext.commands import CommandNotFound

cwd = Path(__file__).parents[0]
cwd = str(cwd)
#print(f"{cwd}\n-----")

async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or("-")(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        if not data or "prefix" not in data:
            return commands.when_mentioned_or("-")(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or("-")(bot, message)

bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    owner_id="owner_id here",
)

secret_file = json.load(open(cwd+'/settings/data.json'))
bot.config_token = secret_file['token']
bot.connection_url = secret_file['mongo']
logging.basicConfig(level=logging.INFO)
bot.remove_command('help')

bot.cwd = cwd
bot.version = 'Build 0.11.26'

bot.colors = {
  'WHITE': 0xFFFFFF,
  'AQUA': 0x1ABC9C,
  'GREEN': 0x2ECC71,
  'SECOND_GREEN': 0x11FA74,
  'BLUE': 0x3498DB,
  'PURPLE': 0x9B59B6,
  'LUMINOUS_VIVID_PINK': 0xE91E63,
  'GOLD': 0xF1C40F,
  'ORANGE': 0xE67E22,
  'RED': 0xE74C3C,
  'SECOND_RED': 0xdb2218,
  'NAVY': 0x34495E,
  'DARK_AQUA': 0x11806A,
  'DARK_GREEN': 0x1F8B4C,
  'DARK_BLUE': 0x206694,
  'DARK_PURPLE': 0x71368A,
  'DARK_VIVID_PINK': 0xAD1457,
  'DARK_GOLD': 0xC27C0E,
  'DARK_ORANGE': 0xA84300,
  'DARK_RED': 0x992D22,
  'DARK_NAVY': 0x2C3E50,
  'BOT_COLOR': 0xc042ff
}
bot.color_list = [c for c in bot.colors.values()]

@bot.event
async def on_ready():
  print(f'\n-----\n{bot.user.name} - {bot.user.id} Çalışıyor\n-----')

  bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
  bot.db = bot.mongo['clustername']
  bot.config = Document(bot.db, 'config')
  print("Database tanımlanıyor\n-----")
  for document in await bot.config.get_all():
    return

@bot.event
async def on_message(message):
    # Ignore messages sent by yourself
    if message.author.bot:
        return

    # Whenever the bot is tagged, respond with its prefix
    if message.content.startswith(f"<@!{bot.user.id}>") and \
        len(message.content) == len(f"<@!{bot.user.id}>"
    ):
        data = await bot.config.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = "-"
        else:
            prefix = data["prefix"]
        await message.channel.send(embed = discord.Embed(description = f"Sunucunun prefixi : `{prefix}`", delete_after=15, color = 0xc042ff))

    await bot.process_commands(message)
    
@bot.command(name="eval", aliases=["exec"])
@commands.is_owner()
async def _eval(ctx, *, code):
    code = clean_code(code)

    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message,
    }

    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
            )

            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"
    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))

    pager = Pag(
        timeout=100,
        entries=[result[i : i + 2000] for i in range(0, len(result), 2000)],
        length=1,
        prefix="```py\n",
        suffix="```",
    )

    await pager.start(ctx)

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, CommandNotFound):
    embed = discord.Embed(title=":exclamation: Hata", description=f'Böyle bir komut bulunmadı. İsterseniz help komutunu deneyebilirsiniz', color = 0xdb2218)
    await ctx.send(embed=embed)

  elif isinstance(error, commands.MissingPermissions):
    embed = discord.Embed(title = ":exclamation: Hata", description='Bu komutu kullanmak için yetkin yok!', color = 0xdb2218)
    await ctx.send(embed = embed)

  elif isinstance(error, commands.MissingRequiredArgument):
    embed = discord.Embed(title = ":exclamation: Hata", description='Komutu eksik bir şekilde girdiniz. Help komutu ile doğru kullanımını kontrol ediniz.', color = 0xdb2218)
    await ctx.send(embed = embed)
    
  elif isinstance(error, commands.DisabledCommand):
    embed = discord.Embed(title = ":exclamation: Hata", description='Komut şuanlık devre dışı bırakılmış durumda.', color = 0xdb2218)
    await ctx.send(embed = embed)

  elif isinstance(error, commands.MemberNotFound):
    embed = discord.Embed(title = ":exclamation: Hata", description = "Kullanıcı bulunamadı.", color = 0xdb2218)
    await ctx.send(embed = embed)

  elif isinstance(error, commands.NotOwner):
    embed = discord.Embed(title = ":exclamation: Hata", description = "Bu komutu sadece geliştirici kullanabilir.", color = 0xdb2218)
    await ctx.send(embed = embed)

  elif isinstance(error, commands.CommandOnCooldown):
    embed = discord.Embed(title = ":exclamation: Hata", description = 'Komutu tekrar kullanmak şu kadar beklemelisin : {:.2f}s'.format(error.retry_after), color = 0xdb2218)
    await ctx.send(embed = embed)

  raise error

if __name__ == '__main__':
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

bot.run(bot.config_token)
