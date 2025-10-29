import logging
import asyncio
from os import getenv
from aiogram import Bot, Dispatcher, html 
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties


TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()

@dp.message(CommandStart())
async def start_message_handler(message:Message):
    await message.answer(f"{html.bold("Pipipupu")}")

@dp.message()
async def some_stuff(message:Message):
    await message.answer("pupupipipi")

async def main():
    bot = Bot(token=TOKEN, default = DefaultBotProperties(parse_mode="HTML"))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())