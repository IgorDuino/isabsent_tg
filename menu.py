from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

main_teacher_menu = InlineKeyboardMarkup()

main_teacher_menu.add(
    InlineKeyboardButton(text="Добавить отсутствие ученика", callback_data="add_student_absent_by_teacher"))
# main_teacher_menu.add(
#     InlineKeyboardButton(text="Отсутствия ученика", callback_data="show_student_absents"))
# InlineKeyboardButton(text="Отсутствия класса", callback_data="show_class_absents"),

main_student_menu = InlineKeyboardMarkup()

main_student_menu.add(
    InlineKeyboardButton(text="Запланировать отсутствие", callback_data="add_student_absent_by_student"))
main_student_menu.add(
    InlineKeyboardButton(text="Мои отсутствия", callback_data="my_absents"))

choose_date = InlineKeyboardMarkup()
choose_date.add(InlineKeyboardButton(text="Сегодня", callback_data="choose_date_today"))
choose_date.add(InlineKeyboardButton(text="Завтра", callback_data="choose_date_tomorrow"))
choose_date.add(InlineKeyboardButton(text="Послезавтра", callback_data="choose_date_day_after_tomorrow"))
choose_date.add(InlineKeyboardButton(text="Другая", callback_data="choose_date_other"))

choose_reason = InlineKeyboardMarkup()
choose_reason.add(InlineKeyboardButton(text="Семейные обстоятельства", callback_data="choose_reason_family"))
choose_reason.add(InlineKeyboardButton(text="Болезнь", callback_data="choose_reason_ill"))
choose_reason.add(InlineKeyboardButton(text="Мероприятие", callback_data="choose_reason_event"))
choose_reason.add(InlineKeyboardButton(text="Другая", callback_data="choose_reason_other"))

main_admin_menu = InlineKeyboardMarkup()
main_admin_menu.add(
    InlineKeyboardButton(text="Загрузить список учеников из таблицы", callback_data="load_students_from_google"))
main_admin_menu.add(
    InlineKeyboardButton(text="Загрузить список учителей из таблицы", callback_data="load_teachers_from_google"))
