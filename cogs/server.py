import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import MissingPermissions, BadArgument
from datetime import datetime
from discord import Embed, Member
from discord.utils import find, get
from cogs._json import read_json
import cogs
import time
import random
import asyncio
from typing import Optional
import urllib

from discord.ext.commands.cooldowns import *

import cogs._json

class Server(commands.Cog):
    """Sunucu komutları"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded\n-----")

    @commands.command(
        name="prefix",
        aliases=["changeprefix", "setprefix", "setprefixto"],
        help="Sunucunda bot ile etkileşime geçmek prefix ayarla",
        usage="[prefix]",
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx, *, prefix="py."):
        await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(embed = discord.Embed(title = "Prefix değiştirildi", description = f"Prefix `{prefix}` olarak ayarlandı. Tekrar değiştirmek için `{prefix}prefix [prefix]` olarak komutu kullanabilirsin", color = 0x11FA74))

    @commands.command(
    name='resetprefix',
    aliases=['rp'],
    help="Prefix sıfırla"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def resetprefix(self, ctx):
        await self.bot.config.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send(embed = discord.Embed(description = "Prefix sıfırlandı ( - )"))

    @commands.command(
        name="userinfo", 
        help="Kullanıcı bilgilerini gösterir"
    )
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author

        show_roles = ', '.join(
            [f"<@&{x.id}>" for x in sorted(user.roles, key=lambda x: x.position, reverse=True) if x.id != ctx.guild.default_role.id]
        ) if len(user.roles) > 1 else 'None'

        embed = discord.Embed(color = 0xc042ff)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="Tam Ad", value=user, inline=True)
        embed.add_field(name="Kullanıcı Adı", value=user.nick if hasattr(user, "nick") else "Yok", inline=True)
        embed.add_field(name="Roller", value=show_roles, inline=False)
        embed_values = {
            "En Yüksek Rolü": user.top_role.name,
            "Oluşturulduğu Tarihi": user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'),
            "Katıldığı Tarih": user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S')
        }
        for n, v in embed_values.items():
            embed.add_field(name=n, value=v, inline=True)
        await ctx.send(embed=embed)

    @commands.command(
        name="serverinfo", 
        help="Sunucu bilgilerini gösterir"
    )
    async def serverinfo(self, ctx):
        role_count = len(ctx.guild.roles)
        emoji_count = len(ctx.guild.emojis)
        channel_count = len([x for x in ctx.guild.channels if isinstance(x, discord.channel.TextChannel)])
        embed = discord.Embed(timestamp=ctx.message.created_at, color = 0xc042ff)
        embed_values = {
            "Sunucu İsmi (ID)": (f"{ctx.guild.name} ({ctx.guild.id})", False),
            "Üye Sayısı": (ctx.guild.member_count, True),
            "Yazı Kanalları": (str(channel_count), True),
            "Bölge": (ctx.guild.region, True),
            "Güvenlik Seviyesi": (str(ctx.guild.verification_level), True),
            "En Yüksek Rol": (ctx.guild.roles[-1], True),
            "Rol Sayısı": (str(role_count), True),
            "Emote Sayısı": (str(emoji_count), True),
            "Kuruluş Tarihi": (ctx.guild.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), True)
        }
        for n, v in embed_values.items():
            embed.add_field(name=n, value=v[0], inline=v[1])
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(
        name="bugreport",
        help="Bug Report",
    )
    @commands.cooldown(1, 25, commands.BucketType.user)
    async def bugreport(self, ctx, *, suggestion):
        em = discord.Embed(title = "Report Gönderildi!", color = discord.Color.red())
        await ctx.send(embed = em)
        embed = discord.Embed(title = "Bir bug tespit edildi", color = discord.Color.red())
        embed.add_field(name = "Kim Tarafından:", value = f"`{ctx.author.name}`")
        embed.add_field(name = "Server:", value = f"`{ctx.guild.name}`")
        embed.add_field(name = "Report: ", value = f"`{suggestion}`")
        embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
        # sending it to the support server
        guild = self.bot.get_guild(827915229551132682)
        # sending it in the channel
        for channel in guild.channels:
            if channel.id == 827921939951517696:
                await channel.send(embed = embed)

    def convert(self, time):
        pos = ["s","m","h","d"]

        time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2

        return val * time_dict[unit]

    @commands.command(
        name="giveaway",
        aliases=['gw'], 
        help="Sunucunda insanlara çekiliş düzenle"
    )
    @commands.has_permissions(administrator = True)
    async def giveaway(self, ctx):
        embed = discord.Embed(title = "Çekiliş Zamanı!", description = "Hadi çekilişi başlatalım. Ayarları yapmak için her soruda 15 saniyen var!", color = 0xE67E22)
        await ctx.send(embed = embed)

        questions = ["Hangi kanalda yapılacak? 1/3",
                    "Çekiliş ne kadar sürecek? (s|m|h|d) 2/3",
                    "Çekilişi kazanana ne verilecek? 3/3"]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i in questions:
            await ctx.send(i)

            try:
                msg = await self.bot.wait_for('message', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                embed = discord.Embed(title = "Zamanında cevaplamadın", description = 'Bir daha ki sefere daha hızlı yap', color = 0xdb2218)
                await ctx.send(embed = embed)
                return
            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"Çekişişin yapılacağı kanal seçilmedi.Bir daha ki sefere bu şekilde yap {ctx.channel.mention}")
            return

        channel = self.bot.get_channel(c_id)

        time = self.convert(answers[1])
        if time == -1:
            embed = discord.Embed(title = "Doğru şekilde cevaplamadın", description = "(s|m|h|d) tarzında kullan! Örnek : 10s [10 Saniye]", color = 0xdb2218)
            await ctx.send()
            return
        elif time == -2:
            embed = discord.Embed(title = "Zaman biçimi sayı ile belirtilmelidir", description = "Tekrar dene", color = 0xdb2218)
            await ctx.send(embed = embed)
            return

        prize = answers[2]
        

        await ctx.send(f"Çekiliş {channel.mention} kanalında ve {answers[1]} sürecek!")

        embed = discord.Embed(title = "Çekiliş!", description = f"{prize}", color = 0xc042ff)
        embed.add_field(name = "Başlatan :", value = ctx.author.mention)
        embed.set_footer(text = f"{answers[1]} içinde sona erecek!")
        my_msg = await channel.send(embed = embed)

        await my_msg.add_reaction("🎉")

        await asyncio.sleep(time)

        new_msg = await channel.fetch_message(my_msg.id)

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))
        winner = random.choice(users)

        if len(users) == 0:
            em = discord.Embed(title = ':warning: Çekiliş Başarısız', color = ctx.author.color)
            em.add_field(name = "Sebep :", value = "Kimse katılmadı")
            await channel.send(embed = em)
            return
        

        newembed = discord.Embed(title = "Çekiliş!", description = f"{prize}", color = 0xF1C40F)
        newembed.add_field(name = "Başlatan :", value = ctx.author.mention)
        newembed.add_field(name = "Kazanan :", value = f"{winner.mention}")
        newembed.set_footer(text = f"{answers[1]} içinde sona erecek!")
        await my_msg.edit(embed = newembed)
        await channel.send(f"Tebrikler! {winner.mention}. {prize} ödülünü kazandın!")
        prizembed = discord.Embed(title = f"Tebrikler!", description = f"Merhaba {winner.mention}, **{ctx.guild.name}** sunucusunda yapılan çekilişte **{prize}** ödülünü kazandın!", color = 0xF1C40F)
        await winner.send(embed = prizembed)

    @giveaway.error
    async def giveaway_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title = ":no_entry: Çekiliş Başarısız!", color = 0xdb2218)
            embed.add_field(name = "Sebep :", value = "`Yönetici izni gerekiyor!`")
            await ctx.send(embed = embed)

    @commands.command(
        name="reroll",
        help="Çekilişi yeniden yap"
    )
    @has_permissions(manage_guild = True)
    async def reroll(self,ctx, channel : discord.TextChannel, id_ : int):
        try:
            new_msg = await channel.fetch_message(id_)
        except:
            await ctx.send("ID yanlış girildi.\nBir sonraki seferde kanalı etiketledikten sonra ID etiketleyin!")
            return

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))

        winner = random.choice(users)
        await channel.send(f"Tebrikler! Kazanan : {winner.mention}!")

    @reroll.error
    async def reroll_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title = ":exclamation: Yeniden çekme işlemi başarısız!", color = 0xdb2218)
            embed.add_field(name = "Sebep :", value = "`Sunucuyu kontrol edebilme yetkisi lazım!`")
            await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Server(client))