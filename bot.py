import logging
import asyncio
from os import getenv
from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
import redis.asyncio as aioredis
import json
import httpx

TOKEN = getenv("BOT_TOKEN")
REDIS_URL = getenv("REDIS_URL", "redis://redis:6379")
GATEWAY_URL = getenv("GATEWAY_URL", "http://gateway:8000")

dp = Dispatcher()

@dp.message(CommandStart())
async def start_message_handler(message: Message):
    await message.answer(f"{html.bold('Pipipupu')}")

@dp.message()
async def rag_answer(message: Message):
    url = f'{GATEWAY_URL}/tasks'
    load = {
        'user_id': message.from_user.id,
        'chat_id': message.chat.id,
        'text': message.text
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=load)

async def listen(bot: Bot):
    while True:
        try:
            redis = aioredis.from_url(REDIS_URL, decode_responses=True)
            pubsub = redis.pubsub()
            await pubsub.subscribe('results')

            logging.info("Connected to Redis and subscribed to 'results' channel")

            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    user_id = data['user_id']
                    result = data['result']
                    await bot.send_message(user_id, result, parse_mode=None)
        except Exception as e:
            logging.exception(f"Redis error: {e}")
            await asyncio.sleep(5)


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    task = asyncio.create_task(listen(bot))
    try:
        await dp.start_polling(bot)
    finally:
        task.cancel()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())