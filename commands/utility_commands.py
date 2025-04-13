# File: commands/utility_commands.py
from discord.ext import commands
import random

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command()
    async def coinflip(self, ctx):
        result = random.choice(['Heads', 'Tails'])
        await ctx.send(f'You flipped: {result}')