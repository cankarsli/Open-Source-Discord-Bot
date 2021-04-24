import platform
from typing import Optional
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import datetime
import asyncio
import aiohttp
import random
import requests
import operator
import json
import time
import glob
import io
import os

from mcstatus import MinecraftServer

from PIL import Image


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.INVITE_LINK = "https://discord.com/api/oauth2/authorize?client_id=825738619553579010&permissions=470150262&scope=bot"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded\n-----")

    def mlengh(movie):
        lengh = str(movie.data['runtimes'])
        lenin = int(lengh.replace('[', '').replace("'", '').replace("]", ''))
        if lenin < 60:
            hours = 0
            minues = lenin
        hours = round(lenin/60)
        minues = (round(lenin % 60))
        mlengh.time = f"{hours} hours, {minues} minues"

    @commands.command(
        name="stats",
        aliases=['bot', 's'], 
        help="Bot bilgilerini göstermek için komut"
    )
    @has_permissions(manage_messages = True)
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))

        embed = discord.Embed(
            title=f"{self.bot.user.name} İstatistikler",
            description="\uFEFF",
            color=0xc042ff,
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Bot Versiyonu :", value=self.bot.version)
        embed.add_field(name="Python Versiyonu :", value=pythonVersion)
        embed.add_field(name="Discord.Py Versiyonu :", value=dpyVersion)
        embed.add_field(name="Toplam Sunucu :", value=serverCount)
        embed.add_field(name="Toplam Kullanıcı :", value=memberCount)
        embed.add_field(name="Geliştiriciler :", value="<@723625048392466563>")
        embed.add_field(name = "Davet Linki : ", value = f"[ Bana Tıkla ]({self.INVITE_LINK})")

        embed.set_footer(text=f"{self.bot.user.name}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(
        name="gunluk", 
        help="Günlük BTC/ETC bilgisi"
    )
    async def gunluk(self, ctx):
        r = requests.get(
            "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR,GBP,TRY"
        )
        r = r.json()
        usd = r["USD"]
        eur = r["EUR"]
        gbp = r["GBP"]
        tur = r["TRY"]
        em = discord.Embed(
            description=f"USD: `{str(usd)}$`\n\nEUR: `{str(eur)}€`\n\nGBP: `{str(gbp)}£`\n\nTRY: `{str(tur)}`", color=0xFFA200
        )
        em.set_author(
            name="Bitcoin",
            icon_url="https://cdn.pixabay.com/photo/2013/12/08/12/12/bitcoin-225079_960_720.png",
        )
        await ctx.send(embed=em)

        # Ethereum bilgisi
        r = requests.get(
            "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,GBP,TRY"
        )
        r = r.json()
        usd = r["USD"]
        eur = r["EUR"]
        gbp = r["GBP"]
        tur = r["TRY"]
        em = discord.Embed(
            description=f"USD: `{str(usd)}$`\n\nEUR: `{str(eur)}€`\n\nGBP: `{str(gbp)}£`\n\nTRY: `{str(tur)}`", color=0xFFA200
        )
        em.set_author(
            name="Ethereum",
            icon_url="https://cdn.discordapp.com/attachments/271256875205525504/374282740218200064/2000px-Ethereum_logo.png",
        )
        await ctx.send(embed=em)

    @commands.command(
        aliases=["bitcoin"], 
        name="btc", 
        help="Bitcoin bilgisi"
    )
    async def btc(self, ctx):
        #await ctx.message.delete()
        r = requests.get(
            "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR,GBP,TRY"
        )
        r = r.json()
        usd = r["USD"]
        eur = r["EUR"]
        gbp = r["GBP"]
        tur = r["TRY"]
        em = discord.Embed(
            description=f"USD: `{str(usd)}$`\n\nEUR: `{str(eur)}€`\n\nGBP: `{str(gbp)}£`\n\nTRY: `{str(tur)}`", color=0xFFA200
        )
        em.set_author(
            name="Bitcoin",
            icon_url="https://cdn.pixabay.com/photo/2013/12/08/12/12/bitcoin-225079_960_720.png",
        )
        await ctx.send(embed=em)

    @commands.command(
        aliases=["ethereum"], 
        name="eth", 
        help="Ethereum bilgisi"
    )
    async def eth(self, ctx):
        #await ctx.message.delete()
        r = requests.get(
            "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,GBP,TRY"
        )
        r = r.json()
        usd = r["USD"]
        eur = r["EUR"]
        gbp = r["GBP"]
        tur = r["TRY"]
        em = discord.Embed(
            description=f"USD: `{str(usd)}$`\n\nEUR: `{str(eur)}€`\n\nGBP: `{str(gbp)}£`\n\nTRY: `{str(tur)}`", color=0xFFA200
        )
        em.set_author(
            name="Ethereum",
            icon_url="https://cdn.discordapp.com/attachments/271256875205525504/374282740218200064/2000px-Ethereum_logo.png",
        )
        await ctx.send(embed=em)

    @commands.command(
        name="mcbilgi",
        help="Minecraft Serveri hakkında istatistikler",
        aliases=['mc']
    )
    async def mcbilgi(self, ctx, server_address, port=25565):
        online_embed = discord.Embed(
            title=f"{server_address} İstatistikler",
            description="**Yükleniyor...**",
            color=0x78d152
        )
        loading_message = await ctx.send(embed=online_embed)
        try:
            server = MinecraftServer(str(server_address), port)
            status = server.status()
            online = status.players.online
            max_players = status.players.max
            ping = round(status.latency)
            version = status.raw['version']['name']
            online_embed = discord.Embed(
                title=f"{server_address} İstatistikler",
                description="Server Aktif!",
                color=0x78d152
            )

            if version:
                online_embed.add_field(name="Server Versiyonu", value=version, inline=True)
            online_embed.add_field(name="Ping", value=f"{ping}ms", inline=True)
            online_embed.add_field(name="Aktif Oyuncu", value=f"{online}/{max_players}", inline=False)

            if online != 0:
                try:
                    names = ", ".join([user['name'] for user in server.status().raw['players']['sample']])
                    if online > 12:
                        names = names + "(Oyuncu sayısı fazla)"
                    if "§" not in names:
                        if names:
                            online_embed.add_field(name="Oyuncu İsimleri", value=f"{names}", inline=False)
                except KeyError:
                    pass

            await loading_message.edit(embed=online_embed)
        except (ConnectionRefusedError, OSError):
            offline_embed = discord.Embed(
                title=f"{server_address} İstatistikler",
                description="Server kapalı veya data alınamıyor.",
                color=0x78d152
            )
            await loading_message.edit(embed=offline_embed)

def setup(bot):
    bot.add_cog(General(bot))