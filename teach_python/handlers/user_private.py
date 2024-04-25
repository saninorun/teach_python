from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import as_list, as_marked_section, Bold
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_products
from filters.chat_types import ChatTypeFilter

from kbrds.in_line import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(or_f(CommandStart(), F.text.lower().contains("привет")))
async def start_cmd(message: types.Message):
    await message.answer(
        text="Привет! Я виртуальный помощник! Что будем делать?",
        reply_markup=get_callback_btns(
            btns={"Нажми меня": "some_1"},
        ),
    )


@user_private_router.callback_query(F.data.startswith("some"))
async def counter(callback: types.CallbackQuery):
    number = int(callback.data.split("_")[-1])
    await callback.message.edit_text(
        text=f"Нажатий - {number}",
        reply_markup=get_callback_btns(btns={"Нажми еще раз": f"some_{number + 1}"}),
    )
