import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeAllPrivateChats
from dotenv import load_dotenv
from database.engine import create_db, drop_db, session_maker
from handlers.admin_private import admin_router
from handlers.user_grups import user_group_router
from handlers.user_private import user_private_router
from middlewares.db import DataBaseSession

load_dotenv()

# ALLOWED_UPDATES = ("message", "edited_message", 'callback_query')

bot = Bot(
    token=os.getenv("TELEGRAM_BOT"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
bot.my_admins_list = []

dp = Dispatcher()
dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)


async def on_startup(bot: Bot):
    run_param = False
    if run_param:
        await drop_db()
    await create_db()


async def on_shutdoun(bot):
    print("Бот лёг!!!")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdoun)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(
        drop_pending_updates=True
    )  # Удаляет все сообщения, которые были отправлены боту в момент когда он был не на связи с телеграм
    # await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    # await bot.set_my_commands(
    #     commands=private, scope=BotCommandScopeAllPrivateChats()
    # )  # Создание меню для бота

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
