from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Получить сертификат"),
            KeyboardButton(text="Получить пароль"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню"
)

gender = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="муж", callback_data="муж"),
            InlineKeyboardButton(text="жен", callback_data="жен"),
        ]
    ]
)

years = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data="first_year"),
            InlineKeyboardButton(text="2", callback_data="second_year"),
            InlineKeyboardButton(text="3", callback_data="third_year"),
        ],
        [
            InlineKeyboardButton(text="4", callback_data="four_year"),
            InlineKeyboardButton(text="5", callback_data="five_year"),
        ]
    ]
)

courses_year_1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Разработка игр и анимаций Kodu Game Lab", callback_data="Разработка игр и анимаций Kodu Game Lab")],
        [InlineKeyboardButton(text="Разработка игр и анимаций Scratch 1.0", callback_data="Разработка игр и анимаций Scratch 1.0")],
        [InlineKeyboardButton(text="Компьютерная грамотность 1.0", callback_data="Компьютерная грамотность 1.0")],
        [InlineKeyboardButton(text="Основы программирования Minecraft 1.0", callback_data="Основы программирования Minecraft 1.0")],
        [InlineKeyboardButton(text="ГОТОВО", callback_data="done")]
    ]
)

courses_year_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Основы программирования Minecraft 2.0", callback_data="Основы программирования Minecraft 2.0")],
        [InlineKeyboardButton(text="Разработка игр и анимаций Scratch 2.0", callback_data="Разработка игр и анимаций Scratch 2.0")],
        [InlineKeyboardButton(text="Компьютерная грамотность 2.0", callback_data="Компьютерная грамотность 2.0")],
        [InlineKeyboardButton(text="Маркетинг и упаковка продукта", callback_data="Маркетинг и упаковка продукта")],
        [InlineKeyboardButton(text="ГОТОВО", callback_data="done")]
    ]
)

courses_year_3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="HTML и CSS", callback_data="HTML и CSS")],
        [InlineKeyboardButton(text="Разработка игр Roblox", callback_data="Разработка игр Roblox")],
        [InlineKeyboardButton(text="Мобильные приложения Thunkable", callback_data="Мобильные приложения Thunkable")],
        [InlineKeyboardButton(text="3D моделирование Tinkercad", callback_data="3D моделирование Tinkercad")],
        [InlineKeyboardButton(text="ГОТОВО", callback_data="done")]
    ]
)

courses_year_4 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Язык программирования Python", callback_data="Язык программирования Python")],
        [InlineKeyboardButton(text="Разработка игр Unity. С#", callback_data="Разработка игр Unity. С#")],
        [InlineKeyboardButton(text="3D Моделирование Blender", callback_data="3D Моделирование Blender")],
        [InlineKeyboardButton(text="ГОТОВО", callback_data="done")]
    ]
)

courses_year_5 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Phyton 2.0", callback_data="Phyton 2.0")],
        [InlineKeyboardButton(text="Unity 2.0", callback_data="Unity 2.0")],
        [InlineKeyboardButton(text="Андроид разработка на Javа", callback_data="Андроид разработка на Javа")],
        [InlineKeyboardButton(text="ГОТОВО", callback_data="done")]
    ]
)


admin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Внести пароли"),
            KeyboardButton(text="Внести пользователей")
        ],
        [
            KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню"
)


done = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="ГОТОВО", callback_data="done")
        ]
    ]
)
gender = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="муж", callback_data="m"),
            InlineKeyboardButton(text="жен", callback_data="w"),
        ]
    ]
)
