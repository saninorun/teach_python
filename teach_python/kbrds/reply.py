from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,)
):
    keyboard = ReplyKeyboardBuilder()
    for index, text in enumerate(btns, start=0):
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, input_fields_placeholder=placeholder)

#
# start_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text="Меню"),
#             KeyboardButton(text="О магазине"),
#         ],
#         [
#             KeyboardButton(text="Варианты доставки"),
#             KeyboardButton(text="Варианты оплаты"),
#         ],
#     ],
#     resize_keyboard=True,
#     input_field_placeholder="Что будем делать?",
# )
#
# del_kbrds = ReplyKeyboardRemove()
#
# start_kb_2 = ReplyKeyboardBuilder()
# start_kb_2.add(
#     KeyboardButton(text="Меню"),
#     KeyboardButton(text="Варианты доставки"),
#     KeyboardButton(text="Варианты оплаты"),
#     KeyboardButton(text="О магазине"),
# )
