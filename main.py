import logging
import datetime
import requests
import telebot
import secret
import texts
import tools
import menu

bot = telebot.TeleBot(secret.API_TOKEN)
base_url = 'http://localhost:5050/v1/'


class Absent:
    def __init__(self, tg_user_id):
        self.tg_user_id = tg_user_id
        self.student_code = None
        self.date = datetime.date.today()
        self.reason = None
        self.proof = None
        self.role = 'teacher'
        self.accept = False


class School:
    def __init__(self, school_name):
        self.school_name = school_name
        self.link = None


temp_absents = {}
temp_schools = {}


@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    data_find_by_tg = {
        "tg_user_id": message.chat.id,
    }
    response_find_by_tg = requests.get(url=base_url + 'school/find_by_code', json=data_find_by_tg)

    if response_find_by_tg.status_code == 200:
        user = response_find_by_tg.json()
        full_name = f"{user['surname']} {user['name']}"
        if user['type'] == 'teacher':
            msg = bot.send_message(message.chat.id, f'Вы успешно авторизовались как учитель {full_name}',
                                   reply_markup=menu.main_teacher_menu)
        elif user['type'] == 'student':
            msg = bot.send_message(message.chat.id,
                                   f"Здравствуйте, {user['name']}, Вы успешно авторизовались как ученик!")

    elif response_find_by_tg.status_code == 400:
        msg = bot.send_message(message.chat.id, f"Здравствуйте, я бот для отметки отсутствия в школе\n "
                                                f"Для авторизации введите свой код:")
        bot.register_next_step_handler(msg, auth_code)


@bot.message_handler(commands=['help'])
def help_(message: telebot.types.Message):
    data_find_by_tg = {
        "tg_user_id": str(message.chat.id),
    }
    response_find_by_tg = requests.get(url=base_url + 'school/find_by_code', json=data_find_by_tg)

    if response_find_by_tg.status_code == 200:
        user = response_find_by_tg.json()
        full_name = f"{user['surname']} {user['name']}"

        msg = bot.send_message(message.chat.id, texts.help_no_auth_users[user['type']])

    elif response_find_by_tg.status_code == 400:
        msg = bot.send_message(message.chat.id, f"Здравствуйте, я бот для отметки отсутствия в школе\n "
                                                f"Для авторизации введите свой код:")
        bot.register_next_step_handler(msg, auth_code)


@bot.message_handler(commands=['admin'])
def admin(message: telebot.types.Message):
    if message.chat.id in secret.list_of_admins_id:
        msg = bot.send_message(message.chat.id, 'Что тебе надобно, старче-адмэн', reply_markup=menu.main_admin_menu)
    else:
        msg = bot.send_message(message.chat.id, 'Вы не админ')


def send_absent(absent: Absent):
    date_add_new_absent = {
        "code": absent.student_code,
        "date": str(absent.date),
        "reason": tools.translate_reason(absent.reason)
    }
    response_add_new_absent = requests.post(url=base_url + 'student/absent', json=date_add_new_absent)
    return response_add_new_absent


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: telebot.types.CallbackQuery):
    if call.data == 'add_student_absent_by_teacher':
        temp_absents[str(call.from_user.id)] = Absent(call.from_user.id)
        msg = bot.edit_message_text(f'Выберите ученика. Напишите имя или фамилию частично', call.from_user.id,
                                    call.message.id)
        bot.register_next_step_handler(msg, choose_student)

    elif call.data == 'choose_student_nobody':
        msg = bot.edit_message_text(f'Напишите имя или фамилию частично', call.from_user.id,
                                    call.message.id)
        bot.register_next_step_handler(msg, choose_student)

    elif call.data.startswith('choose_student_'):
        code = call.data.split('choose_student_')[1]
        temp_absents[str(call.from_user.id)].student_code = code

        data_find_student = {
            "code": code
        }
        response_find_student = requests.get(url=base_url + 'student', json=data_find_student)
        student = response_find_student.json()

        full_name = f"{student['surname']} {student['name']}"

        msg = bot.edit_message_text(f'Выбран ученик: {full_name}\nВыберите дату',
                                    call.from_user.id,
                                    call.message.id, reply_markup=menu.choose_date)

    elif call.data == 'choose_date_other':
        msg = bot.edit_message_text(f'Напишите дату в формате 2021-12-05',
                                    call.from_user.id,
                                    call.message.id)

        bot.register_next_step_handler(msg, choose_date_other)

    elif call.data.startswith('choose_date_'):
        date = call.data.split('choose_date_')[1]
        day = datetime.timedelta(days=1)
        if date == 'today':
            date = datetime.date.today()
        elif date == 'tomorrow':
            date = datetime.date.today() + day
        elif date == 'day_after_tomorrow':
            date = datetime.date.today() + day + day

        temp_absents[str(call.from_user.id)].date = str(date)
        msg = bot.edit_message_text(f'Выберите причину отсутствия', call.from_user.id, call.message.id,
                                    reply_markup=menu.choose_reason)

    elif call.data == 'choose_reason_other':
        msg = bot.edit_message_text('Напшите причину:', call.from_user.id, call.message.id)
        bot.register_next_step_handler(msg, choose_reason_other)

    elif call.data.startswith('choose_reason_'):
        reason = call.data.split('choose_reason_')[1]
        temp_absents[str(call.from_user.id)].reason = reason
        response = send_absent(temp_absents[str(call.from_user.id)])
        if response.status_code == 201:
            msg = bot.send_message(call.from_user.id, 'Запись успешно добавлена!', reply_markup=menu.main_teacher_menu)
        elif response.status_code == 400:
            msg = bot.send_message(call.from_user.id, 'В эту дату данный ученик уже имеет запись об отсутствии',
                                   reply_markup=menu.main_teacher_menu)

    elif call.data == 'load_students_from_google':
        msg = bot.edit_message_text(f'Напишите название школы', call.from_user.id, call.message.id)
        bot.register_next_step_handler(msg, admin_choose_school_to_load_students_from_google)

    elif call.data == 'load_teachers_from_google':
        msg = bot.edit_message_text(f'Напишите название школы', call.from_user.id, call.message.id)
        bot.register_next_step_handler(msg, admin_choose_school_to_load_teachers_from_google)

    elif call.data == 'add_school':
        msg = bot.edit_message_text(f'Название школы', call.from_user.id, call.message.id)
        bot.register_next_step_handler(msg, admin_add_school_name)

    elif call.data == 'school_list':
        response_get_schools = requests.get(base_url + 'schools')
        msg = bot.edit_message_text(response_get_schools.text, call.from_user.id, call.message.id,
                                    reply_markup=menu.main_admin_menu)


def admin_choose_school_to_load_students_from_google(message: telebot.types.Message):
    data_load_students_from_google = {
        "school_name": message.text
    }
    response_load_students_from_google = requests.post(base_url + 'school/students',
                                                       json=data_load_students_from_google)
    msg = bot.send_message(message.chat.id, f'Код: {response_load_students_from_google.status_code}',
                           reply_markup=menu.main_admin_menu)


def admin_add_school_link(message: telebot.types.Message):
    temp_schools[str(message.chat.id)].link = message.text
    data_add_school = {
        "school_name": temp_schools[str(message.chat.id)].school_name,
        "link": message.text
    }
    response_add_school = requests.post(base_url + 'school',
                                        json=data_add_school)
    msg = bot.send_message(message.chat.id, f'Код: {response_add_school.status_code}',
                           reply_markup=menu.main_admin_menu)


def admin_add_school_name(message: telebot.types.Message):
    temp_schools[str(message.chat.id)] = School(message.text)
    msg = bot.send_message(message.chat.id, 'Ссылка на таблицу:')
    bot.register_next_step_handler(msg, admin_add_school_link)


def admin_choose_school_to_load_teachers_from_google(message: telebot.types.Message):
    data_load_students_from_google = {
        "school_name": message.text
    }
    response_load_students_from_google = requests.post(base_url + 'school/teachers',
                                                       json=data_load_students_from_google)
    msg = bot.send_message(message.chat.id, f'Код: {response_load_students_from_google.status_code}',
                           reply_markup=menu.main_admin_menu)


def choose_date_other(message: telebot.types.Message):
    if tools.validate_date(message.text):
        temp_absents[str(message.chat.id)].date = message.text
        msg = bot.send_message(message.chat.id, f'Выберите причину отсутствия', reply_markup=menu.choose_reason)
    else:
        msg = bot.send_message(message.chat.id, f'Неккоретный формат даты. Напишите дату в формате 2021-12-05')
        bot.register_next_step_handler(msg, choose_date_other)


def choose_reason_other(message: telebot.types.Message):
    temp_absents[str(message.chat.id)].reason = message.text
    response = send_absent(temp_absents[str(message.chat.id)])
    if response.status_code == 201:
        msg = bot.send_message(message.chat.id, 'Запись успешно добавлена!', reply_markup=menu.main_teacher_menu)
    elif response.status_code == 400:
        msg = bot.send_message(message.chat.id, 'В эту дату данный ученик уже имеет запись об отсутствии',
                               reply_markup=menu.main_teacher_menu)


def choose_student(message: telebot.types.Message):
    data_find_students = {
        "tg_user_id": message.chat.id,
        "name": message.text
    }
    response_find_students = requests.get(url=base_url + 'teacher/students_by_name', json=data_find_students)

    if response_find_students.status_code == 200:
        founded_students = response_find_students.json()['students']

        inline_keyboard = telebot.types.InlineKeyboardMarkup()
        for student in founded_students:
            full_name = f"{student['surname']} {student['name']}"
            inline_keyboard.add(
                telebot.types.InlineKeyboardButton(text=full_name, callback_data=f"choose_student_{student['code']}"))
        inline_keyboard.add(
            telebot.types.InlineKeyboardButton(text='Другой', callback_data=f"choose_student_nobody"))

        msg = bot.send_message(message.chat.id, f'Выберите из списка:', reply_markup=inline_keyboard)


def auth_code(message: telebot.types.Message):
    data_find_by_code = {
        "code": message.text,
    }
    response_find_by_code = requests.get(url=base_url + 'school/find_by_code', json=data_find_by_code)

    if response_find_by_code.status_code == 200:
        user = response_find_by_code.json()
        full_name = f"{user['surname']} {user['name']}"
        class_name = user['class_name']
        school_name = user['school_name']

        data_auth_tg = {
            "code": message.text,
            "tg_user_id": message.chat.id
        }

        if user['type'] == 'teacher':
            response_th_auth = requests.post(url=base_url + 'teacher/tg_auth', json=data_auth_tg)
            msg = bot.send_message(message.chat.id,
                                   f'Вы успешно авторизовались как учител {class_name} класса - {full_name}',
                                   reply_markup=menu.main_teacher_menu)
        elif user['type'] == 'student':
            response_th_auth = requests.post(url=base_url + 'student/tg_auth', json=data_auth_tg)
            # msg = bot.send_message(message.chat.id, f'Вы успешно авторизовались как ученик {full_name}',
            #                        reply_markup=menu.main_student_menu)
            msg = bot.send_message(message.chat.id,
                                   f"{user['name']}, пока нет возможности авторизоваться ученикам. Если Вы учитель, "
                                   f"то проверьте код и введите повторно")
            bot.register_next_step_handler(msg, auth_code)

    else:
        msg = bot.send_message(message.chat.id, f'Пользователя с таким кодом несуществует. Проверьте код и '
                                                f'отправьте его заного. Если это не помогает напишите @igorduino')
        bot.register_next_step_handler(msg, auth_code)


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.infinity_polling()
