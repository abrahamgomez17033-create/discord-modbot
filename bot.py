import os
import discord
from discord.ext import commands
import config
import database as db
import asyncio
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, help_command=None)

async def healthcheck(request):
    return web.Response(text="ok")

async def run_http():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

@bot.event
async def on_ready():
    await db.init_db()
    print(f"✅ {bot.user} conectado a Discord ({len(bot.guilds)} servidores)")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Comandos del Bot", color=discord.Color.blue())
    embed.add_field(name="🛡️ Moderación", value="""
`!kick <user> [razón]`
`!ban <user> [razón]`
`!unban <id>`
`!mute <user> <tiempo> [razón]`
`!unmute <user>`
`!warn <user> [razón]`
`!warns <user>`
`!clearwarns <user>`
`!purge <cantidad>`
    """, inline=False)
    embed.add_field(name="🤖 AutoMod", value="""
`!addbl <palabra>`
`!removebl <palabra>`
`!allowinvite <codigo>`
    """, inline=False)
    embed.add_field(name="⚙️ Configuración", value="""
`!setlog <canal>`
`!setmuterole <rol>`
`!ticketpanel`
    """, inline=False)
    await ctx.send(embed=embed)

async def main():
    await run_http()
    async with bot:
        bot.config = config
        await bot.load_extension("cogs.moderation")
        await bot.load_extension("cogs.automod")
        await bot.load_extension("cogs.logging")
        await bot.load_extension("cogs.tickets")
        await bot.start(config.TOKEN)

asyncio.run(main())