from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_teacher_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Добавить отсутствие ученика", callback_data="add_student_absent_by_teacher"))
    keyboard.add(
        InlineKeyboardButton(text="Отсутствия ученика", callback_data="show_student_absents"))
    keyboard.add(
        InlineKeyboardButton(text="Отсутствия класса", callback_data="show_class_absents"))

    return keyboard


def main_student_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Запланировать отсутствие", callback_data="add_student_absent_by_student"))
    keyboard.add(
        InlineKeyboardButton(text="Мои отсутствия", callback_data="my_absents"))
    return keyboard


def choose_day(prefix):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Сегодня", callback_data=f"choose_date_today_{prefix}"))
    keyboard.add(InlineKeyboardButton(text="Завтра", callback_data=f"choose_date_tomorrow_{prefix}"))
    keyboard.add(InlineKeyboardButton(text="Послезавтра", callback_data=f"choose_date_day_after_tomorrow_{prefix}"))
    keyboard.add(InlineKeyboardButton(text="Другая", callback_data=f"choose_date_other_{prefix}"))

    return keyboard


def choose_reason():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Семейные обстоятельства", callback_data="choose_reason_family"))
    keyboard.add(InlineKeyboardButton(text="Болезнь", callback_data="choose_reason_ill"))
    keyboard.add(InlineKeyboardButton(text="Мероприятие", callback_data="choose_reason_event"))
    keyboard.add(InlineKeyboardButton(text="Другая", callback_data="choose_reason_other"))

    return keyboard


def main_admin_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Загрузить список учеников из таблицы", callback_data="load_students_from_google"))
    keyboard.add(
        InlineKeyboardButton(text="Загрузить список учителей из таблицы", callback_data="load_teachers_from_google"))

    return keyboard


def choose_student(founded_students):
    keyboard = InlineKeyboardMarkup()
    for student in founded_students:
        full_name = f"{student['surname']} {student['name']}"
        keyboard.add(
            InlineKeyboardButton(text=full_name, callback_data=f"choose_student_{student['code']}"))
    keyboard.add(
        InlineKeyboardButton(text='Другой', callback_data=f"choose_student_nobody"))

    return keyboard
