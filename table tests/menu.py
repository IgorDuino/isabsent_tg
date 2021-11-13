from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

start = InlineKeyboardMarkup()

start.add(
    InlineKeyboardButton(text="🎓 Ученик", callback_data="student"),
    InlineKeyboardButton(text="🧑🏿‍🏫 Учитель", callback_data="teacher")
)
