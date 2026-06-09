import discord
from discord.ext import commands
import database as db

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        cfg = await db.get_config(guild.id)
        if cfg and cfg["log_channel"]:
            return guild.get_channel(cfg["log_channel"])
        return None

    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if msg.author.bot or not msg.guild:
            return
        ch = await self.get_log_channel(msg.guild)
        if not ch:
            return
        embed = discord.Embed(
            title="Mensaje eliminado",
            description=f"**Autor:** {msg.author} ({msg.author.mention})\n**Canal:** {msg.channel.mention}\n**Contenido:** {msg.content[:500]}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        ch = await self.get_log_channel(before.guild)
        if not ch:
            return
        embed = discord.Embed(
            title="Mensaje editado",
            description=f"**Autor:** {before.author} ({before.author.mention})\n**Canal:** {before.channel.mention}\n**Antes:** {before.content[:500]}\n**Después:** {after.content[:500]}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch = await self.get_log_channel(member.guild)
        if not ch:
            return
        embed = discord.Embed(
            title="Miembro entró",
            description=f"{member.mention} — `{member.id}`",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ch = await self.get_log_channel(member.guild)
        if not ch:
            return
        embed = discord.Embed(
            title="Miembro salió",
            description=f"{member} — `{member.id}`",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        ch = await self.get_log_channel(guild)
        if not ch:
            return
        embed = discord.Embed(
            title="Usuario baneado",
            description=f"{user} — `{user.id}`",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow()
        )
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        ch = await self.get_log_channel(guild)
        if not ch:
            return
        embed = discord.Embed(
            title="Usuario desbaneado",
            description=f"{user} — `{user.id}`",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        await ch.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logging(bot))