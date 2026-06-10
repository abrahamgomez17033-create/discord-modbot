import discord
from discord.ext import commands
import re
import asyncio

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_blacklist = set()
        self.invite_whitelist = set()
        self.mention_limit = 5
        self.spam_cache = {}
        self._load_config()

    def _load_config(self):
        cfg = self.bot.config
        self.mention_limit = getattr(cfg, "MENTION_LIMIT", 5)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild:
            return

        content = msg.content.lower()

        if self.word_blacklist and any(palabra in content for palabra in self.word_blacklist):
            await msg.delete()
            await msg.channel.send(f"{msg.author.mention} — contenido bloqueado.", delete_after=3)
            return

        invites = re.findall(r'(?:discord\.(?:gg|com/invite)/)\w+', content)
        if invites:
            for inv in invites:
                if inv not in self.invite_whitelist:
                    await msg.delete()
                    await msg.channel.send(f"{msg.author.mention} — no se permiten enlaces a otros servidores.", delete_after=3)
                    return

        if len(msg.mentions) > self.mention_limit:
            await msg.delete()
            await msg.channel.send(f"{msg.author.mention} — spam de menciones.", delete_after=3)
            return

        ahora = discord.utils.utcnow().timestamp()
        cache = self.spam_cache.get(msg.author.id, [])
        cache = [t for t in cache if ahora - t < 5]
        cache.append(ahora)
        self.spam_cache[msg.author.id] = cache
        if len(cache) > 5:
            await msg.channel.send(f"{msg.author.mention} — detectado spam. Silenciando 30s...", delete_after=3)
            muted = discord.utils.get(msg.guild.roles, name="Muted")
            if not muted:
                muted = await msg.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
            await msg.author.add_roles(muted)
            await asyncio.sleep(30)
            await msg.author.remove_roles(muted)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addbl(self, ctx, *, palabra):
        self.word_blacklist.add(palabra.lower())
        await ctx.send(f"⬛ `{palabra}` añadida a la lista negra.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removebl(self, ctx, *, palabra):
        self.word_blacklist.discard(palabra.lower())
        await ctx.send(f"⬜ `{palabra}` eliminada de la lista negra.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def allowinvite(self, ctx, codigo: str):
        self.invite_whitelist.add(codigo)
        await ctx.send(f"✅ `{codigo}` permitido.")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))