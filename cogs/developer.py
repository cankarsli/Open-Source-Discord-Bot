import os
import random
import traceback
import time
import asyncio
import discord
import sys
from discord.ext import commands, tasks
from git import Repo
import discord
import psutil
import os

import datetime

from discord import Embed, Member, Role, CategoryChannel, __version__, Activity, ActivityType

import random

class Owner(commands.Cog):
    """Owner"""
    def __init__(self, bot):
        self.bot = bot
        self.lock = False
        self.status.start()

    def cog_unload(self):
        self.status.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded\n-----")

    @tasks.loop(seconds=10)
    async def status(self):
      activity_guilds = Activity(name=f'{len(self.bot.guilds)} sunucu', type=ActivityType.watching)
      activity_help = Activity(name='-help', type=ActivityType.playing)
      activity_listening = Activity(name='Seni', type=ActivityType.listening)
      activity_list = [activity_help, activity_guilds, activity_listening]
      await self.bot.change_presence(activity=random.choice(activity_list))

    @status.before_loop
    async def before_printer(self):
      await self.bot.wait_until_ready()

    @commands.command(aliases=['disconnect'])
    @commands.is_owner()
    async def close(self, ctx):
        """
        Bot'u kapat
        """
        embed = discord.Embed(title = "Bot Offline... 👋", color = ctx.author.color)
        await ctx.send(embed = embed)
        await self.bot.logout()

    @commands.command(
        name='reload', description="Tüm/seçili cogları yenile!", aliases=['rl']
    )
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        '''
        Cog dosyalarını yenile
        '''
        if not cog:
            # Cog yok belirtilmedi ise hepsi yenilenir
            async with ctx.typing():
                embed = discord.Embed(
                    title="Coglar yenilendi.",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Yenilendi: `{ext}`",
                                value='\uFEFF',
                                inline=False
                            )
                        except Exception as e:
                            embed.add_field(
                                name=f"Yenileme başarısız: `{ext}`",
                                value=e,
                                inline=False
                            )
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            # Spesifik bir cog dosyasını yükle
            async with ctx.typing():
                embed = discord.Embed(
                    title="Cog yenilendi!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Yenileme başarısız: `{ext}`",
                        value="Böyle bir cog bulunmamakta.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Yenilendi: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Yenileme başarısız: `{ext}`",
                            value=desired_trace,
                            inline=False
                        )
                await ctx.send(embed=embed)

    @commands.command(
        name="ping",
        help="Ping değerini hesapla"
    )
    @commands.is_owner()
    async def ping(self, ctx):
        p = ctx.message.channel.permissions_for(ctx.message.guild.get_member(self.bot.user.id))
        if not p.send_messages:
            try:
                await ctx.message.author.send("🤔 Yorulmuş görünüyorsun. Ne yazık ki kanalda mesaj gönderme yetkim yok. Eğer bu yetkiyi verirsen sunucu üzerinde daha rahat cevap verebilirim.")
            except Exception:
                pass
            return
        t1 = time.perf_counter()
        msg = await ctx.send(f"⏳ hesaplanıyor...")
        t2 = time.perf_counter()
        rest = round((t2 - t1) * 1000)
        latency = round(self.bot.latency * 1000)
        await msg.edit(content=f'🏓 Pong! Gecikme: `{latency}` ms | REST API: `{rest}` ms')

    @commands.command(
        name="toggle", 
        help="Bir komutu devre dışı bırak veya aktif et"
    )
    @commands.is_owner()
    async def toggle(self, ctx, *, command):
        command = self.bot.get_command(command)

        if command is None:
            await ctx.send("Bu isimde bir komut bulamıyorum!")

        elif ctx.command == command:
            await ctx.send("Bu komutu devre dışı bırakamazsın!")

        else:
            command.enabled = not command.enabled
            ternary = "aktif" if command.enabled else "devre dışı"
            await ctx.send(embed = discord.Embed(description = f"{command.qualified_name} komutunu {ternary} hale getirdim!", color = 0x1ABC9C))

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, name: str):
        """ Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, name: str):
        """ Unloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command(
        name="update", 
        description="Automatically updates the bot from github!"
    )
    @commands.is_owner()
    async def update(self, ctx):
        await ctx.send("Beginning the update")
        async with ctx.typing():
            repo = Repo(os.getcwd())
            repo.git.fetch()
            repo.git.pull()

            # attempt to reload all commands
            await asyncio.sleep(5)
            await self.reload(ctx)

            await ctx.send("Update complete!")

def setup(bot):
    bot.add_cog(Owner(bot))
