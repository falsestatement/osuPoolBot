import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from os import environ
import json
import beatmap

load_dotenv()


def run_discord_bot():
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user} started')
        try:
            synced = await bot.tree.sync()
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(e)

    @bot.event
    async def on_message(message):
        if bot.user.mentioned_in(message):
            async with message.channel.typing():
                reference = await message.channel.fetch_message(message.reference.message_id)
                await message.channel.send("Generating pool...")
                beatmap.generate_pool(reference.content.split("\n"))
                await message.channel.send(file=discord.File("pool.txt"))

    @bot.tree.command(name="mapinfo")
    @app_commands.describe(map_url="osu! beatmap URL", mods="Mods you want to apply to this map")
    async def mapinfo(interaction: discord.Interaction, map_url: str, mods: str):
        async with interaction.channel.typing():
            await interaction.response.send_message(json.dumps(beatmap.getBeatmapInfo(beatmap.parseURL(map_url), beatmap.parseMods(mods)), indent=2), ephemeral=False)

    bot.run(environ["DISCORD_TOKEN"])
