from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import as_list, as_marked_section, Bold
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_products
from filters.chat_types import ChatTypeFilter
from kbrds import reply

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(or_f(CommandStart(), F.text.lower().contains("привет")))
async def start_cmd(message: types.Message):
    await message.answer(
        text="Привет! Я виртуальный помощник! Что будем делать?",
        reply_markup=reply.get_keyboard(
            "Меню",
            "Варианты доставки",
            "Варианты оплаты",
            "О магазине",
            placeholder="Что будем делать?",
            sizes=(1, 2, 1),
        ),
    )


@user_private_router.message(or_f(Command("menu"), (F.text.lower().contains("меню"))))
async def cmd(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
        )
    await message.answer(
        text="Вот меню... Что делаем дальше?",
        reply_markup=reply.get_keyboard(
            "Меню",
            "Варианты доставки",
            "Варианты оплаты",
            "О магазине",
            placeholder="Что будем делать?",
            sizes=(1, 2, 1),
        ),
    )


@user_private_router.message(Command("about"))
async def cmd(message: types.Message):
    await message.answer(text="О нас")


@user_private_router.message(
    or_f(or_f(Command("payment"), (F.text.lower().contains("оплат"))))
)
async def cmd(message: types.Message):
    text = as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении картой/cash",
        "В заведении",
        marker="- ",
    )
    await message.answer(text=text.as_html())


@user_private_router.message(
    or_f(Command("shipping"), (F.text.lower().contains("доставк")))
)
async def cmd(message: types.Message):
    text = as_list(
        as_marked_section(
            Bold("Варианты доставки:"),
            "Курьер",
            "Самовынос (сейчас прибегу, заберу!)",
            "Покушаю у вас (сейчас прибегу!)",
            marker="- ",
        ),
        as_marked_section(
            Bold("Нельзя:"),
            "Почта",
            "Голуби",
            marker="- ",
        ),
        sep="\n---------------------\n",
    )
    await message.answer(text=text.as_html())


@user_private_router.message(F.text == "111")
async def cmd(message: types.Message):
    await message.answer(text="klashjdfklajshd")
