import discord
from discord.ext import commands
import asyncio

class Polls(commands.Cog):
    """Oylama komutları"""
    def __init__(self, bot):
        self.bot = bot

    def __init__(self, bot):
        self.bot = bot
        self.emojis = [':regional_indicator_a:', ':regional_indicator_b:', ':regional_indicator_c:', ':regional_indicator_d:', ':regional_indicator_e:', ':regional_indicator_f:', ':regional_indicator_g:', ':regional_indicator_h:', ':regional_indicator_i:', ':regional_indicator_j:', ':regional_indicator_k:', ':regional_indicator_l:', ':regional_indicator_m:', ':regional_indicator_n:', ':regional_indicator_o:', ':regional_indicator_p:', ':regional_indicator_q:', ':regional_indicator_r:', ':regional_indicator_s:', ':regional_indicator_t:']
        self.emojisRxn = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹']

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded\n-----")

    @commands.command(
    pass_context=True,
    brief="Oylama başlat",
    help="Sunucunda oylama başlat",
    usage=f"poll <text-channel> [question]"
    )
    async def poll(self, ctx, channel : discord.TextChannel, *, question):
        if channel is None or question is None:
            em = discord.Embed(title = ":exclamation: Başarısız", color = 0xbf2828, description = "\n```{}nick @member/id yeni_isim```")
            em.add_field(name = 'Sebep:', value =f"Argümanlar doğru girilmedi")
            await ctx.send(embed = em)
            return
        else:
            toDel = [ctx.message]
            answers = []


            def check(message):
                return message.author == ctx.message.author and message.channel == ctx.message.channel and len(message.content) <= 100

            tellMeE = discord.Embed(title='Oylama', description=f'Diğer seçimleri yazabilirsin \nBaşlatmak için `başlat`\niptal etmek için `iptal`', color=0x34495E)
            tellMeE.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            timeoutE = discord.Embed(title='Oylama', description=f'Oylama süresi doldu :/\n Başka bir oylama başlatabilirsin `poll <question>`')
            timeoutE.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            for i in range(0, 20):
                toDel.append(await ctx.send(embed=tellMeE))

                try:
                    possibleChoice = await self.bot.wait_for('message', check=check, timeout=60.0)

                except asyncio.TimeoutError:
                    await ctx.send(embed=timeoutE)
                    break

                toDel.append(possibleChoice)
                
                if possibleChoice.clean_content.startswith('başlat'):
                    publish = True
                    break

                elif possibleChoice.clean_content.startswith('iptal'):
                    publish = False
                    break

                answers.append(possibleChoice.clean_content)
                tellMeE = discord.Embed(title='Oylama', description=f'Seçim {len(answers)} ({answers[i]}) kaydedildi !\nDiğer seçimleri yazabilirsin \nBaşlatmak için `başlat`\niptal etmek için `iptal`', color=0x34495E)
                tellMeE.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            try:
                await ctx.message.channel.delete_messages(toDel)
            except:
                pass

            if publish == True:
                pollEmbed = discord.Embed(title=f'*{question}*', color=0xF1C40F)
                pollEmbed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                pollEmbed.set_footer(text=f'{ctx.message.author} tarafından başlatıldı', icon_url=ctx.message.author.avatar_url)

                for i in range(0, len(answers)):
                    pollEmbed.add_field(name=f'{self.emojis[i]}', value=answers[i], inline=True)

                pollMsg = await channel.send(embed=pollEmbed)

                for i in range(0, len(answers)):
                    await pollMsg.add_reaction(self.emojisRxn[i])
            
            else:
                cancelE = discord.Embed(title='Oylama', description=f'{ctx.message.author} oylama iptal edildi', color=0xdb2218)
                cancelE.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                cancelE.set_footer(text=f'{ctx.message.author} tarafından', icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=cancelE, delete_after=5)


def setup(client):
    client.add_cog(Polls(client))