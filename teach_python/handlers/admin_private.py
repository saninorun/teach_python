from string import punctuation
from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product
from database.orm_query import (
    orm_add_product,
    orm_get_products,
    orm_delete_product,
    orm_get_product,
    orm_update_product,
    orm_get_categories,
    orm_get_info_pages,
    orm_change_banner_image,
)
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbrds.in_line import get_callback_btns
from kbrds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Я так, просто, посмотреть зашел...",
    placeholder="Выберите действие",
    sizes=(2,),
)


@admin_router.message(Command("admin"))
async def add_product(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text.lower().contains("ассортимент"))
async def starring_at_product(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session=session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    await message.answer(
        "Выберите категорию:", reply_markup=get_callback_btns(btns=btns)
    )


@admin_router.callback_query(F.data.startswith("category_"))
async def starring_at_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split("_")[-1]
    for product in await orm_get_products(
        session=session, category_id=int(category_id)
    ):
        await callback.message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
            reply_markup=get_callback_btns(
                btns={
                    "Удалить": f"delete_{product.id}",
                    "Изменить": f"change_{product.id}",
                }
            ),
        )
    await callback.answer()
    await callback.message.answer("Ок, вот список товаров.\nЧто делаем дальше?")


@admin_router.callback_query(F.data.lower().startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session=session, product_id=int(product_id))
    await callback.answer("Товар удален")
    await callback.message.answer("Ок, удалили товар")


# Для машины состояний (FSM)


############--микро FSM для загрузки исзенения банеров--############
class AddBaner(StatesGroup):
    image = State()


# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@admin_router.message(StateFilter(None), F.tex == "Добавить/Изменить банер")
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(
        f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}"
    )
    await state.set_state(AddBaner.image)


# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам:
# main, catalog, cart(для пустой корзины), about, payment, shipping


@admin_router.message(AddBaner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(
            f"Введите нормальное название страницы, например:\
                         \n{', '.join(pages_names)}"
        )
        return
    await orm_change_banner_image(session, for_page, image_id)
    await message.answer("Банер обновлен!")
    await state.clear()


#   Ловим некорректный ввод
@admin_router.message(AddBaner.image)
async def add_banner2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или отмена")


######################### FSM для дабавления/изменения товаров админом ###################


class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_for_update: Product | None = None

    texts = {
        "AddProduct:name": "Введите название заново",
        "AddProduct:description": "Введите описание заново",
        "AddProduct:category": "Выберете категорию заново",
        "AddProduct:price": "Введите стоимость заново",
        "AddProduct:image": "Этот стайт последний поэтому ...",
    }


@admin_router.callback_query(StateFilter(None), F.data.lower().startswith("change_"))
async def update_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]
    product_for_update = await orm_get_product(
        session=session,
        product_id=int(product_id),
    )
    AddProduct.product_for_update = product_for_update
    await callback.answer()
    await callback.message.answer(
        text="Введите название товара:", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter(None), F.text.lower().contains("добавить товар"))
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cansel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_update:
        AddProduct.product_for_update = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def cansel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer("Вы и так в начале!")
        return
    previous_step = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_step)
            await message.answer(
                f"Ок, вернулись к шагу \n{AddProduct.texts[previous_step]}"
            )
            return
        previous_step = step


@admin_router.message(AddProduct.name, or_f(F.text.lower(), F.text == "."))
async def add_name(message: types.Message, state: FSMContext) -> None:
    if message.text == ".":
        await state.update_data(name=AddProduct.product_for_update.name)
    else:
        await state.update_data(name=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.description, or_f(F.text.lower(), F.text == "."))
async def add_name(
    message: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    if message.text == ".":
        await state.update_data(description=AddProduct.product_for_update.description)
    else:
        if len(message.text) <= 4:
            await message.answer("Описание слишком коротко, введите заново.")
            return
        await state.update_data(description=message.text)

    categories = await orm_get_categories(session=session)
    btns = {category.name: str(category.id) for category in categories}
    await message.answer(
        "Выберите категорию", reply_markup=get_callback_btns(btns=btns)
    )
    await state.set_state(AddProduct.category)


@admin_router.callback_query(AddProduct.category)
async def category_choice(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if int(callback.data) in [
        category.id for category in await orm_get_categories(session=session)
    ]:
        await callback.answer()
        await state.update_data(category_id=int(callback.data))
        await callback.message.answer("Теперь введите цену товара")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer("Выберите категорию из кнопок")
        await callback.answer()


@admin_router.message(AddProduct.price, or_f(F.text.lower(), F.text == "."))
async def add_name(message: types.Message, state: FSMContext) -> None:
    if message.text == ".":
        await state.update_data(price=AddProduct.product_for_update.price)
    else:
        await state.update_data(price=float(message.text))
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(
    message: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    if message.text == ".":
        await state.update_data(image=AddProduct.product_for_update.image)
    else:
        await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    try:
        if AddProduct.product_for_update:
            await orm_update_product(
                session=session, product_id=AddProduct.product_for_update.id, data=data
            )
        else:
            await orm_add_product(session=session, data=data)
        await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
        await message.answer(str(data))
        await state.clear()
    except Exception as e:
        await message.answer(
            "Ошибка, что то не так, найдите кодера :)", reply_markup=ADMIN_KB
        )
        await state.clear()
    AddProduct.product_for_update = None
