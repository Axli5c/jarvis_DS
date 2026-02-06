import discord
from discord.ext import commands

from config import SYSTEM_PROMPT
from services.gemini_service import GeminiService


class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, gemini: GeminiService):
        self.bot = bot
        self.gemini = gemini


    @commands.Cog.listener()
    async def on_ready(self):
        print("=" * 50)
        print("✅ БОТ ЗАПУЩЕН!")
        print(f"🤖 {self.bot.user.name}")
        print(f"📊 Серверов: {len(self.bot.guilds)}")
        print(SYSTEM_PROMPT)
        print("=" * 50)

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="Хочешь поболтать? \n Просто тегни меня",
            )
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return


        # Проверяем, личка или тегнули на сервере
        if self.bot.user and self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            # вырезаем имя бота в тексте
            user_question = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            if not user_question:
                response = await self.gemini.get_response(
                    message.channel.id,
                    'Пользователь тебя тегнул в чате но не задал вопроса, спроси у него что ему нужно',
                    message.author.display_name
                )
                return response

            async with message.channel.typing():
                response = await self.gemini.get_response(
                    message.channel.id,
                    user_question,
                    message.author.display_name
                )

            if not response:
                return

            if len(response) > 2000:
                chunks = [response[i:i + 1900] for i in range(0, len(response), 1900)]
                await message.reply(chunks[0])
                for chunk in chunks[1:]:
                    await message.channel.send(chunk)
            else:
                await message.reply(response)

        # важно, иначе команды не будут работать
        await self.bot.process_commands(message)
        return None


async def setup(bot: commands.Bot):
    gemini: GeminiService = bot.gemini  # мы положим его в bot в bot.py
    await bot.add_cog(EventsCog(bot, gemini))