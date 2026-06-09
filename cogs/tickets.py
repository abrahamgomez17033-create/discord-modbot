import discord
from discord.ext import commands
import config

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def ticketpanel(self, ctx):
        embed = discord.Embed(
            title="🎫 Sistema de Tickets",
            description="Reacciona con 🎫 para abrir un ticket de soporte.",
            color=discord.Color.blue()
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎫")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        emoji = str(payload.emoji)

        if emoji == "🎫":
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return
            member = guild.get_member(payload.user_id)
            if not member:
                return

            category = discord.utils.get(guild.categories, name=config.TICKET_CATEGORY_NAME)
            if not category:
                category = await guild.create_category(config.TICKET_CATEGORY_NAME)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            for role_name in config.STAFF_ROLES:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            channel = await guild.create_text_channel(
                f"ticket-{member.name.lower()}",
                category=category,
                overwrites=overwrites
            )
            await channel.send(
                f"{member.mention} ticket abierto. Un moderador te atenderá pronto.\n"
                f"Reacciona con 🔒 para cerrar el ticket."
            )
            await channel.send("🔒")

        elif emoji == "🔒":
            channel = self.bot.get_channel(payload.channel_id)
            if not channel or not channel.name.startswith("ticket-"):
                return
            await channel.delete()

async def setup(bot):
    await bot.add_cog(Tickets(bot))