from util import *
from config import *
from funshi import *

import discord
from discord.ext import commands

import os

bot = commands.Bot(
    command_prefix="f.", 
    intents=discord.Intents.all(),
    guild_ids = verified_servers
)



@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    e = discord.Embed(description=error, color=discord.Color.red())
    await ctx.respond(embeds=[e], ephemeral=True)



def main():
    if (os.path.exists(FUNSHI)):
        print(FUNSHI)
    if (os.path.exists(FUNSHI_JSON)):
        print(FUNSHI_JSON)
    if (os.path.exists(BACKUP)):
        print(BACKUP)
    if (os.path.exists(BACKUP_JSON)):
        print(BACKUP_JSON)

    for i in cog_files:
        try:
            bot.load_extension(i)
        except Exception as err:
            print(err)
    


if __name__ == '__main__':
    main()
    bot.run(token)
    