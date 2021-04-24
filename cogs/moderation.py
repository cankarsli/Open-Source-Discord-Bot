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
from io import BytesIO
from typing import Optional

import re

from utils.converters import GetFetchUser

import cogs._json

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {'h': 3600, 's': 1, 'm': 60, 'd': 86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(f"{value} geçerli bir zaman biçimi değil! Geçerli zaman biçimleri : h|m|s|d ")
            except ValueError:
                raise commands.BadArgument(f"{key} bir sayı değil!")
        return time

class Moderation(commands.Cog):
    """Moderasyon Komutları"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded\n-----")

    @commands.command(
        name="anons",
        help='Belirli kanalda anons yap'
    )
    @commands.has_permissions(manage_channels = True)
    async def anons(self,ctx, channel : discord.TextChannel, *, msg = None):
        if channel == None:
            em = discord.Embed(title = ":exclamation: Başarısız", color = 0xbf2828)
            em.add_field(name = 'Sebep:', value =f"Kanal belirtilmedi")
            await ctx.send(embed = em)
        else:
            embed = discord.Embed(color = 0xF1C40F)
            embed.add_field(name = "Anons:", value = f"`{msg}`")
            embed.set_footer(text = f"{ctx.author.name} tarafından")
            await channel.send(embed = embed)

    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.command(
        name="clear", 
        aliases = ["temizle"], 
        help="Mesajları temizle"
    )
    @has_permissions(manage_messages = True)
    async def clear(self, ctx, amount = 1):
        em = discord.Embed(title= f"{amount} mesaj silindi", color = 0x11FA74)
        em.add_field(name ="Kim tarafından temizlendi :", value = f"{ctx.author.mention}")
        await ctx.channel.purge(limit = amount + 1)
        await ctx.channel.send(embed = em, delete_after=3.5)

    @commands.command(
        name="lock", 
        aliases=['kilitle'], 
        help="Yazı kanalını kilitle"
    )
    @has_permissions(manage_channels = True)
    async def lock(self, ctx, *, reason = "Sebep belirtilmedi"):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages = False, read_messages = True)
        em = discord.Embed(title = f":white_check_mark: Kanal kilitlendi!", color = 0x11FA74)
        em.add_field(name = "**Sorumlu Moderator :**", value = f"`{ctx.author.name}`")
        em.add_field(name = "**Sebep :**", value = f"`{reason}`")
        await ctx.channel.send(embed = em)

    @commands.command(
        name="unlock", 
        aliases=['kilitkaldır'], 
        help="Yazı kanalının kilidini kaldır"
    )
    @has_permissions(manage_channels = True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages = True, read_messages = True)
        em = discord.Embed(title = f":white_check_mark: Kanal kilidi kaldırıldı!", color = 0x11FA74)
        em.add_field(name = "**Sorumlu Moderator :**", value = f"`{ctx.author.name}`")
        await ctx.channel.send(embed = em)

    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.command(
        name="slowmode", 
        aliases=['slow'], 
        help="Yazı kanalında yavaş modu aktif eder (Oto 5 - Kapatmak için 0)"
    )
    @has_permissions(manage_channels = True)
    async def slowmode(self, ctx, amount = 5, *, reason = "Sebep belirtilmedi"):
        if amount > 6000:
            embed = discord.Embed(title = ":exclamation: Hata", description="6000'den düşük olmalıdır!", color = 0xdb2218)
            await ctx.channel.send(embed = embed)
            
            return

        await ctx.channel.edit(slowmode_delay=amount)
        em = discord.Embed(title = ":white_check_mark: Yavaş Mod ayarlandı!", color = 0x11FA74)
        em.add_field(name = "**Sorumlu Moderator :**", value = f"`{ctx.author.name}`")
        em.add_field(name = "**Sebep :**", value = f"`{reason}`")
        em.add_field(name=  "Açıklama", value = f"Artık spam yapılmayacak\n {ctx.author.mention} diğer türlü 'lock' komutunu kullanabilirsiniz", inline = False)
        em.add_field(name = "Yavaş Mod", value = f"`{amount} saniye`")
        await ctx.send(embed = em)

    @commands.command(
        name="mute", 
        help="Üyeyi susturun", 
        aliases=['sustur'],
        usage="<user> [reason]"
    )
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, user: Member, *, reason = "Sebep belirtilmedi"):
        role = get(ctx.guild.roles, name="Muted")
        if user == None:
                embed = discord.Embed(title = ":exclamation: Başarısız", color= 0xdb2218)
                embed.add_field(name = "Sebep:", value = "Susturulması için birisini etiketle!")
                await ctx.send(embed = embed)
                return
        if not role:
            try:
                createrole = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(createrole, send_messages=False)
            except:
                return await ctx.send(f"Üzgünüm {ctx.author.mention} `Muted` isimli rolü oluşturmak için yetkim yok.")
        else:
            await user.add_roles(role)
            return await ctx.send(embed=Embed(title="Muted", description=f"Hey {ctx.author.mention} başaralı bir şekilde {user} isimli kullanıcının susturdun", color = 0x11FA74))
            await user.add_roles(createrole)
            return await ctx.send(embed=Embed(title="Muted", description=f"Hey {ctx.author.mention} başarlı bir şekilde {user} isimli kullanıcıyı susturdun", color = 0x11FA74))
                
    @commands.command(
        name="unmute", 
        help="Üyenin susturmasını kaldır", 
        aliases=['susturmakaldır'], 
        usage="<user> [reason]"
    )
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, user: Member):
        if user == ctx.author:
            return await ctx.send(f"Üzgünüm {ctx.author.mention} kendini muteleyemezsin!")
        role = get(ctx.guild.roles, name="Muted")
        if not role:
            return await ctx.send(f"Üzgünüm {ctx.author.mention} burda `Muted` isminde rol bulunmamakta!")
        if not find(lambda role: role.name == "Muted", user.roles):
            embed = discord.Embed(title = ":exclamation: Başarısız", description = f"{ctx.author.mention}, üzgünüm kullanıcı susturulmamış!", color= 0xdb2218)
            return await ctx.send(embed = embed)
        await user.remove_roles(role)
        return await ctx.send(embed=Embed(title="Mute Kaldırıldı", description=f"Hey {ctx.author.mention} başarlı bir şekilde {user} isimli kullanıcının susturmasını kaldırdın.", color = 0x11FA74))

    @commands.command(
        aliases=['gizle'], 
        name="hide", 
        help='Kanalı diğer kullanıcılara gizler (Yetkililer görebilir)',
        usage="<text-channel>"
    )
    @commands.has_permissions(manage_channels=True)
    async def hide(self, ctx, channel : discord.TextChannel=None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.read_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        em = discord.Embed(title = f":white_check_mark: Oda gizlendi!", color = 0x11FA74)
        em.add_field(name = "**Sorumlu Moderator :**", value = f"`{ctx.author.name}`")
        await ctx.send(embed = em)

    @commands.command(
        aliases=['göster'], 
        name="show", 
        help='Kanalın diğer kullanıcılara olan gizlenmesini kaldır',
        usage="<text-channel>"
    )
    @commands.has_permissions(manage_channels=True)
    async def show(self, ctx, channel : discord.TextChannel=None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.read_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        em = discord.Embed(title = f":white_check_mark: Odanın gizliliği kaldırıldı!", color = 0x11FA74)
        em.add_field(name = "**Sorumlu Moderator :**", value = f"`{ctx.author.name}`")
        await ctx.send(embed = em)

    @commands.command(
        name="ban",
        help="Sunucudan birini yasakla"
    )
    @has_permissions(ban_members = True)
    async def ban(self, ctx, member : discord.Member = None, *, reason = "Sebep belirtilmedi"):
        try:
            if member == None:
                embed = discord.Embed(title = ":exclamation: Başarısız", color= 0xdb2218)
                embed.add_field(name = "Sebep:", value = "Banlanması için birisini etiketle!")
                await ctx.send(embed = embed)
                return
            if member == ctx.author:
                em = discord.Embed(title = ':exclamation: Başarısız', color = 0xdb2218)
                em.add_field(name = 'Sebep:', value = f"Kendini banlayamazsın ;-;")
                await ctx.send(embed=  em)
                return

            try:
                await member.send(f"{ctx.guild.name} sunucusundan yasaklandın\nSebep: `{reason}`\nYetkili: `{ctx.author.name}`")
            except:
                pass

            await member.ban(reason = reason)
            em = discord.Embed(title = f"Başarılı!", color = 0x11FA74, description = f"{member.name} başarıyla sunucudan yasaklandı")
            em.add_field(name = "Sebep: ", value = f"`{reason}\n`")
            em.add_field(name = "**Moderator**:", value = f"`{ctx.author.name}`")
            em.set_footer(text = f"Görüşürüz {member.name}!")
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)

        except:
            await ctx.channel.send(embed = discord.Embed(description = f"{member.mention} moderator yada admin!", color = 0xdb2218))


    @commands.command(
        name="banlist",
        help='Sunucudaki yasaklananlar listesi'
    )
    @commands.has_permissions(kick_members = True)
    @commands.bot_has_permissions(ban_members = True)
    async def banlist(self, ctx):
        users = await ctx.guild.bans()
        if len(users) > 0:
            msg = f'`{"ID":21}{"İsim":25} Sebep\n'
            for entry in users:
                userID = entry.user.id
                userName = str(entry.user)
                if entry.user.bot:
                    username = '🤖' + userName
                reason = str(entry.reason)
                msg += f'{userID:<21}{userName:25} {reason}\n'
            embed = discord.Embed(color=0xe74c3c)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(text=f'Server: {ctx.guild.name}')
            embed.add_field(name='Banlananlar', value=msg + '`', inline=True)
            await ctx.send(embed=embed)
        else:
            em = discord.Embed(title = f"Bilgilendirme", description = f"Banlanan kimse yok!", color = 0xF1C40F)
            await ctx.send(embed = em)

    @commands.command(
        name="unban",
        help="Sunucundan yasaklanan birisinin yasağını kaldır"
    )
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, user: GetFetchUser, *, reason="Sebep belirtilmedi"):
            if user == None:
                embed = discord.Embed(title = ":exclamation: Başarısız", color= 0xdb2218)
                embed.add_field(name = "Sebep:", value = "Banın kaldırılması için birisini etiketle!")
                await ctx.send(embed = embed)
                return
            await ctx.guild.unban(user=user, reason = reason)
            em = discord.Embed(title = f"Başarılı!", color = 0x11FA74, description = f"{user} başarıyla sunucu yasağı kaldırıldı")
            em.add_field(name = "Sebep: ", value = f"`{reason}\n`")
            em.add_field(name = "**Moderator**:", value = f"`{ctx.author.name}`")
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)

    @commands.command(
        name="kick",
        help="Atılacak kişiyi yazın",
        aliases=['at']
    )
    @commands.guild_only()
    @has_permissions(ban_members = True)
    async def kick(self, ctx, member : discord.Member = None, *, reason = "Sebep belirtilmedi"):
        try:
            if member == None:
                embed = discord.Embed(title = ":exclamation: Başarısız", color= 0xdb2218)
                embed.add_field(name = "Sebep:", value = "Atılması için birisini etiketle!")
                await ctx.send(embed = embed)
                return
            if member == ctx.author:
                em = discord.Embed(title = ':exclamation: Başarısız', color = 0xdb2218)
                em.add_field(name = 'Sebep:', value = f"Kendini atamazsın ;-;")
                await ctx.send(embed=  em)
                return
            try:
                await member.send(f"{ctx.guild.name} sunucusundan atıldın\nSebep: `{reason}`\nYetkili: `{ctx.author.name}`")
            except:
                pass
            await member.kick(reason = reason)
            em = discord.Embed(title = f"Başarılı!", description = f"{member.name} başarıyla sunucudan atıldı", color = 0x11FA74)
            em.add_field(name = "Sebep: ", value = f"`{reason}\n`")
            em.add_field(name = "**Moderator**:", value = f"`{ctx.author.name}`")
            em.set_footer(text = f"Görüşürüz {member.name}!")
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)

        except:
            await ctx.channel.send(embed = discord.Embed(description = f"{member.mention} moderator yada admin!", color = 0xdb2218))

    @commands.command(
        name="nick",
        help="Üyenin kullanıcı adını değiştirin",
        usage="nick <@member/id> yeni_isim"
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member:discord.Member=None, *, nick=None):
        if member is None or nick is None:
            await ctx.send(embed = discord.Embed(description = "Eksiksiz doldurduğunuzdan emin olun :\n```{}nick @member/id yeni_isim```".format(ctx.prefix), color = 0xdb2218))
            return
        try:
            await member.edit(nick=nick)
            em = discord.Embed(title = f"Başarılı!", color = 0x11FA74, description = "{} adlı kullanıcının kullanıcı adı değiştirildi".format(member.name))
            em.add_field(name = "**Kim Tarafından**:", value = f"`{ctx.author.name}`")
            em.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = em)
        except discord.Forbidden:
            await ctx.channel.send(embed = discord.Embed(description = f"Bunu yapmak için yetkim yok!", color = 0xdb2218))
            
def setup(client):
    client.add_cog(Moderation(client))