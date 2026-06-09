import discord
from discord.ext import commands
import database as db

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No especificada"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} ha sido expulsado. Razón: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No especificada"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} ha sido baneado. Razón: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="No especificada"):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"✅ {user.mention} ha sido desbaneado.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, cantidad: int):
        await ctx.channel.purge(limit=cantidad + 1)
        msg = await ctx.send(f"🧹 {cantidad} mensajes eliminados.")
        await msg.delete(delay=3)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason="No especificada"):
        cfg = await db.get_config(ctx.guild.id)
        role = None
        if cfg and cfg["mute_role_id"]:
            role = ctx.guild.get_role(cfg["mute_role_id"])
        if not role:
            role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
            for ch in ctx.guild.channels:
                await ch.set_permissions(role, send_messages=False, speak=False)

        await member.add_roles(role, reason=reason)

        await db.set_config(ctx.guild.id, mute_role_id=role.id)
        await ctx.send(f"🔇 {member.mention} silenciado. Razón: {reason}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if role and role in member.roles:
            await member.remove_roles(role)
        await ctx.send(f"🔊 {member.mention} ya puede hablar.")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No especificada"):
        await db.add_warn(ctx.guild.id, member.id, ctx.author.id, reason)
        warns = await db.get_warns(ctx.guild.id, member.id)
        await ctx.send(f"⚠️ {member.mention} advertido. Razón: {reason} (Total: {len(warns)})")

    @commands.command()
    async def warns(self, ctx, member: discord.Member):
        warns = await db.get_warns(ctx.guild.id, member.id)
        if not warns:
            await ctx.send(f"✅ {member.mention} no tiene advertencias.")
            return
        msg = f"**Advertencias de {member}**\n"
        for w in warns:
            mod = ctx.guild.get_member(w["moderator_id"])
            mod_name = mod.display_name if mod else "Desconocido"
            msg += f"`#{w['id']}` {w['reason']} — por {mod_name} ({w['timestamp']})\n"
        await ctx.send(msg)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, member: discord.Member):
        await db.clear_warns(ctx.guild.id, member.id)
        await ctx.send(f"✅ Advertencias de {member.mention} eliminadas.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, channel: discord.TextChannel):
        await db.set_config(ctx.guild.id, log_channel=channel.id)
        await ctx.send(f"📝 Canal de logs configurado a {channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setmuterole(self, ctx, role: discord.Role):
        await db.set_config(ctx.guild.id, mute_role_id=role.id)
        await ctx.send(f"🔇 Rol de mute configurado a {role.mention}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))