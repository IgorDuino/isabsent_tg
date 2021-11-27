from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

main_teacher_menu = InlineKeyboardMarkup()

main_teacher_menu.add(
    InlineKeyboardButton(text="Добавить пропуск", callback_data="add_absent")
)

main_student_menu = InlineKeyboardMarkup()

main_student_menu.add(
    InlineKeyboardButton(text="Запланировать пропуск", callback_data="plan_absent")
)

choose_reason_menu = InlineKeyboardMarkup()

choose_reason_menu.add(
    InlineKeyboardButton(text="🤒 Болезнь", callback_data="reason_ill"),
    InlineKeyboardButton(text="👨‍👨‍👦 Семейные обстоятельства", callback_data="reason_family")
)
