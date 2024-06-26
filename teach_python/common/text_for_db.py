from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ["Еда", "Напитки"]

description_for_info_pages = {
    "main": "Добро пожаловать",
    "about": "Пиццерия такая-то\nРежим работы круглосуточно",
    "payment": as_marked_section(
        Bold("Варианты оплаты"),
        "Картой в боте",
        "При получении наличными",
        "В заведении",
        marker="🔔",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Варианты доставки"),
            "Курьер",
            "Самовынос",
            "В заведении",
            marker="🍦",
        ),
        as_marked_section(
            Bold("Нельзя"),
            "Почта",
            "Голуби",
            marker="❌",
        ),
        sep="\n-------------------------------\n",
    ).as_html(),
    "catalog": "Категории",
    "cart": "В корзине ничего нет",
}
