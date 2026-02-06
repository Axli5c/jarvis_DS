import discord
from discord.ext import commands

from config import DISCORD_TOKEN
from services.gemini_service import GeminiService


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.emojis = True


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.gemini = GeminiService()

    async def setup_hook(self):
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.commands")


bot = MyBot()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)