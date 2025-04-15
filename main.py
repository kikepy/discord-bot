import asyncio
import discord
from discord.ext import commands

from commands.music_commands import MusicCommands
from commands.utility_commands import UtilityCommands
from config.json_reader import TokenReader


json_config = TokenReader('config/config.json')
token = json_config.get_token()

if not token:
    print("Error: No se pudo obtener el token")
    exit()

#Configuracion del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Bot listo
@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} is ready!')

# Cargar los comandos
async def load_cogs():
    await bot.add_cog(UtilityCommands(bot))
    await bot.add_cog(MusicCommands(bot))

async def main():
    async with bot:
        await load_cogs()
        await bot.start(token)

asyncio.run(main())