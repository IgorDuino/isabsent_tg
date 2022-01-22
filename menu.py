from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(user):
    """Returns the main menu needed for this user"""
    if user.role == 'teacher':
        return main_teacher_menu()
    else:
        return main_student_menu()


def main_teacher_menu():
    """Returns the main menu for the teacher"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Добавить отсутствие ученика", callback_data="add_student_absent_by_teacher"))
    keyboard.add(
        InlineKeyboardButton(text="Отсутствия ученика", callback_data="show_student_absents"))
    keyboard.add(
        InlineKeyboardButton(text="Отсутствия класса", callback_data="show_class_absents"))

    return keyboard


def main_student_menu():
    """Returns the main menu for the student"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Запланировать отсутствие", callback_data="add_student_absent_by_student"))
    keyboard.add(
        InlineKeyboardButton(text="Мои отсутствия", callback_data="my_absents"))
    return keyboard


def choose_day(prefix):
    """Returns the date selection menu"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Сегодня", callback_data=f"choose_date_today_{prefix}"))
    keyboard.add(InlineKeyboardButton(text="Завтра", callback_data=f"choose_date_tomorrow_{prefix}"))
    keyboard.add(InlineKeyboardButton(text="Послезавтра", callback_data=f"choose_date_day_after_tomorrow_{prefix}"))
    keyboard.add(InlineKeyboardButton(text="Другая", callback_data=f"choose_date_other_{prefix}"))

    return keyboard


def choose_reason():
    """Returns the menu for selecting the reason"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Семейные обстоятельства", callback_data="choose_reason_family"))
    keyboard.add(InlineKeyboardButton(text="Болезнь", callback_data="choose_reason_ill"))
    keyboard.add(InlineKeyboardButton(text="Мероприятие", callback_data="choose_reason_event"))
    keyboard.add(InlineKeyboardButton(text="Другая", callback_data="choose_reason_other"))

    return keyboard


def main_admin_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Список школ", callback_data="school_admin_menu"))
    keyboard.add(
        InlineKeyboardButton(text="Добавить школу", callback_data="add_new_school"))
    keyboard.add(
        InlineKeyboardButton(text="Выйти", callback_data="start"))
    return keyboard


def school_admin_menu(school_name):
    keyboard = InlineKeyboardMarkup()
    # keyboard.add(
    #     InlineKeyboardButton(text="Найти класс", callback_data=f"find_class_{school_name}"))
    keyboard.add(
        InlineKeyboardButton(text="Ссылка на таблицу", callback_data=f"table_link_{school_name}"))
    keyboard.add(
        InlineKeyboardButton(text="Загрузить список учеников из таблицы ⬇️",
                             callback_data=f"load_students_from_google_{school_name}"))
    keyboard.add(
        InlineKeyboardButton(text="Загрузить список учителей из таблицы ⬇️",
                             callback_data=f"load_teachers_from_google_{school_name}"))
    keyboard.add(
        InlineKeyboardButton(text="Ученики",
                             callback_data=f"get_students_{school_name}"))
    keyboard.add(
        InlineKeyboardButton(text="Удалить школу 🗑️",
                             callback_data=f"delete_school_{school_name}"))
    keyboard.add(
        InlineKeyboardButton(text="Назад ◀️",
                             callback_data=f"main_admin_menu"))

    return keyboard


def school_admin_table_link_menu(school_name):
    keyboard = InlineKeyboardMarkup()
    # keyboard.add(
    #     InlineKeyboardButton(text="Изменить ссылку", callback_data=f"set_new_table_link_{school_name}"))
    keyboard.add(
        InlineKeyboardButton(text="Назад ◀️", callback_data=f"main_admin_menu"))

    return keyboard


def choose_student(founded_students, prefix):
    keyboard = InlineKeyboardMarkup()
    for student in founded_students:
        full_name = f"{student['surname']} {student['name']}"
        keyboard.add(
            InlineKeyboardButton(text=full_name, callback_data=f"choose_student_{student['code']}_{prefix}"))
    keyboard.add(
        InlineKeyboardButton(text='Другой', callback_data=f"choose_student_nobody_{prefix}"))

    return keyboard


def admin_school_list(school_names_list):
    keyboard = InlineKeyboardMarkup()
    if len(school_names_list) > 0:
        for school_name in school_names_list:
            keyboard.add(
                InlineKeyboardButton(text=school_name, callback_data=f"admin_select_school_{school_name}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Добавить школу", callback_data="add_new_school"))
    keyboard.add(
        InlineKeyboardButton(text="Назад ◀️", callback_data=f"main_admin_menu"))

    return keyboard


def teacher_accept_request(by):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Одобрить ✅", callback_data=f"approve_request_{by}"))
    keyboard.add(
        InlineKeyboardButton(text="Отклонить ❌", callback_data=f"reject_request_{by}"))
    return keyboard
