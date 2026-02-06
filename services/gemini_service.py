import asyncio
from collections import defaultdict
from google import genai
from google.genai import types
from googletrans import Translator

from config import GEMINI_API_KEY, SYSTEM_PROMPT


translator = Translator()

async def errMsg(error_type, e: Exception):
    translate = await translator.translate(str(e.message), src='en', dest='ru')

    return (f"❌ **Неизвестная ошибка**\n"
            f"📋 Описание: Произошла непредвиденная ошибка\n"
            f"📋 Код: {str(e.code)}\n \n"
            f"🔧 Тип ошибки: `{error_type}`\n\n"
            f"💬 Детали: {translate.text}\n\n"
            f"💬 Details: {translate.origin}"
            )


class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.conversations = defaultdict(list)

    async def get_response(self, channel_id: int, user_message: str, user_name: str) -> str:
        try:
            if not self.conversations[channel_id]:
                self.conversations[channel_id].append({
                    "role": "user",
                    "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{user_name}: {user_message}"}]
                })
            else:
                self.conversations[channel_id].append({
                    "role": "user",
                    "parts": [{"text": f"{user_name}: {user_message}"}]
                })

            if len(self.conversations[channel_id]) > 20:
                self.conversations[channel_id] = self.conversations[channel_id][-20:]

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=self.conversations[channel_id],
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    top_p=0.95,
                    max_output_tokens=2048,
                    safety_settings=[
                        types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='BLOCK_NONE'),
                        types.SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='BLOCK_NONE'),
                        types.SafetySetting(category='HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold='BLOCK_NONE'),
                        types.SafetySetting(category='HARM_CATEGORY_DANGEROUS_CONTENT', threshold='BLOCK_NONE')
                    ]
                )
            )

            ai_text = response.text or ""
            self.conversations[channel_id].append({"role": "model", "parts": [{"text": ai_text}]})
            return ai_text

        except Exception as e:
            error_type = type(e).__name__
            if error_type == 'ServerError':
                return 'Упс... Кажется я затупил, попробуй позже'
            else:
                return await errMsg(error_type, e)


    def clear_history(self, channel_id: int):
        self.conversations[channel_id].clear()