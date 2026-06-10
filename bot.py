import os
import sys
import logging
import discord
from discord.ext import commands
import config
import database as db
import asyncio
from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("modbot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, help_command=None)

async def healthcheck(request):
    return web.Response(text="OK", status=200)

async def run_http():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    app.router.add_get("/health", healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 HTTP server escuchando en puerto {port}")

@bot.event
async def on_ready():
    try:
        await db.init_db()
        logger.info(f"✅ {bot.user} conectado a Discord ({len(bot.guilds)} servidores)")
        logger.info(f"🔧 Prefijo: {config.PREFIX}")
    except Exception as e:
        logger.error(f"Error en on_ready: {e}")
        raise

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Falta argumento requerido: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Argumento inválido: {error}")
    else:
        logger.error(f"Error en comando {ctx.command}: {error}")
        await ctx.send("❌ Ocurrió un error al ejecutar el comando.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Comandos del Bot", color=discord.Color.blue())
    embed.add_field(name="🛡️ Moderación", value=f"""
`{config.PREFIX}kick <user> [razón]`
`{config.PREFIX}ban <user> [razón]`
`{config.PREFIX}unban <id>`
`{config.PREFIX}mute <user> <tiempo> [razón]`
`{config.PREFIX}unmute <user>`
`{config.PREFIX}warn <user> [razón]`
`{config.PREFIX}warns <user>`
`{config.PREFIX}clearwarns <user>`
`{config.PREFIX}purge <cantidad>`
    """, inline=False)
    embed.add_field(name="🤖 AutoMod", value=f"""
`{config.PREFIX}addbl <palabra>`
`{config.PREFIX}removebl <palabra>`
`{config.PREFIX}allowinvite <codigo>`
    """, inline=False)
    embed.add_field(name="⚙️ Configuración", value=f"""
`{config.PREFIX}setlog <canal>`
`{config.PREFIX}setmuterole <rol>`
`{config.PREFIX}ticketpanel`
    """, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latencia: {round(bot.latency * 1000)}ms")

async def main():
    try:
        await run_http()
        async with bot:
            bot.config = config
            await bot.load_extension("cogs.moderation")
            await bot.load_extension("cogs.automod")
            await bot.load_extension("cogs.logging")
            await bot.load_extension("cogs.tickets")
            await bot.start(config.TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot detenido por usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())