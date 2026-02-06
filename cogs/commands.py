from discord.ext import commands
from services.gemini_service import GeminiService


class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, gemini: GeminiService):
        self.bot = bot
        self.gemini = gemini

    @commands.command(name="clear")
    async def clear_history(self, ctx: commands.Context):
        self.gemini.clear_history(ctx.channel.id)
        await ctx.send("🧹 История очищена!")

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        await ctx.send(f"Упомяни {self.bot.user.mention} + твой вопрос\nКоманды: `!clear` `!ping`")

    @commands.command(name="ping")
    async def ping_command(self, ctx: commands.Context):
        await ctx.send(f"🏓 {round(self.bot.latency * 1000)}ms")


async def setup(bot: commands.Bot):
    gemini: GeminiService = bot.gemini
    await bot.add_cog(CommandsCog(bot, gemini))