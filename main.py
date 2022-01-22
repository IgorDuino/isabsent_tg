import datetime
import requests
import telebot
import secret
import texts
import tools
import menu

bot = telebot.TeleBot(secret.API_TOKEN)
base_url = 'http://isabsent.tk/v1/'

list_of_admins_id = [759634381, 902729981]


class Absent:
    def __init__(self, by):
        self.by = by
        self.accept = False
        self.tg_user_id = None
        self.student_code = None
        self.date = datetime.date.today()
        self.reason = None
        self.proof = None


class User:
    def __init__(self):
        self.name = 'Name'
        self.surname = 'Surname'
        self.patronymic = 'Patronymic'
        self.class_name = 'Class'
        self.school_name = 'School'
        self.role = 'Role'
        self.tg_user_id = 0

    @property
    def full_name(self):
        return f'{self.name} {self.patronymic}'.title()


class School:
    def __init__(self, school_name):
        self.school_name = school_name
        self.link = None


temp_absents = {}
temp_schools = {}


def auth_by_code(tg_user_id, code):
    user: User = get_user(tg_user_id, code)

    if not user:
        return False

    # Just for annotation of type
    user: User = user

    request_body = {
        "code": code,
        "tg_user_id": tg_user_id
    }

    response_tg_auth = requests.post(url=base_url + f'{user.role}/tg_auth', json=request_body)

    return {"user": user, "response": response_tg_auth}


def get_user(tg_user_id, code=None):
    request_body = {}
    if code:
        request_body["code"] = str(code)
    else:
        request_body["tg_user_id"] = int(tg_user_id)

    response_find_by_code = requests.get(url=base_url + 'school/find_by_code', params=request_body)

    if response_find_by_code.status_code == 200:
        user_data = response_find_by_code.json()
        user = User()

        user.name = user_data.get('name')
        user.Surname = user_data.get('surname')
        user.patronymic = user_data.get('patronymic')
        user.class_name = user_data.get('class_name')
        user.school_name = user_data.get('school_name')
        user.role = user_data.get('type')
        user.tg_user_id = user_data.get('tg_user_id')

        return user
    else:
        return False


def auth_by_code_message(message: telebot.types.Message):
    chat_id = message.chat.id
    code = str(message.text)

    if code.startswith('/'):
        # Sending a request to re-write the command
        msg = bot.send_message(message.chat.id, texts.step_handler_command_error)
        return

    auth_by_code_res = auth_by_code(message.chat.id, code)
    if not auth_by_code_res:

        msg = bot.send_message(message.chat.id, texts.error)
    else:
        if auth_by_code_res["response"].status_code == 200:
            bot.send_message(chat_id, texts.welcome_text(auth_by_code_res['user']))


def send_absent(absent: Absent):
    if absent.accept:
        if absent.student_code is None:
            data_add_new_absent = {
                "tg_user_id": absent.by,
                "date": str(absent.date),
                "reason": tools.translate_reason(absent.reason)
            }
        else:
            data_add_new_absent = {
                "code": absent.student_code,
                "date": str(absent.date),
                "reason": tools.translate_reason(absent.reason)
            }

        response_add_new_absent = requests.post(url=base_url + 'student/absent', json=data_add_new_absent)
        print(data_add_new_absent)
        print(response_add_new_absent.json())
        return response_add_new_absent.status_code
    else:
        student = get_user(absent.by)
        teachers_list = get_teachers_list(student.school_name)
        # TODO: Переделать когда будет API метод по получению учителя по названию класса
        for teacher in teachers_list:
            if teacher['class_name'] == student.class_name:
                if teacher['tg_user_id']:
                    # replace_dict = {
                    #     "ill": 'Болезнь'
                    # }
                    msg_to_teacher = bot.send_message(teacher['tg_user_id'],
                                                      texts.new_request_from_student.format(date=str(absent.date),
                                                                                            reason=absent.reason),
                                                      reply_markup=menu.teacher_accept_request(absent.by))
                    return 999
        return 998


def get_school_list():
    response_get_schools = requests.get(url=base_url + 'schools')
    if response_get_schools.status_code == 200:
        return response_get_schools.json()['schools']
    else:
        return []


def get_teachers_list(school_name):
    get_teacher_list_data = {
        "school_name": school_name
    }
    response_get_schools = requests.get(url=base_url + 'school/teachers', params=get_teacher_list_data)
    if response_get_schools.status_code == 200:
        return response_get_schools.json()['teachers']
    else:
        return []


def get_list_students(school_name):
    get_students_data = {
        "school_name": school_name
    }
    response_load_students_from_google = requests.get(base_url + 'school/students',
                                                      params=get_students_data)

    if response_load_students_from_google.status_code == 200:
        return response_load_students_from_google.json()['students']
    else:
        return []


def admin_add_school_link(message: telebot.types.Message):
    temp_schools[str(message.chat.id)].link = message.text
    data_add_school = {
        "school_name": temp_schools[str(message.chat.id)].school_name,
        "link": message.text
    }
    response_add_school = requests.post(base_url + 'school',
                                        json=data_add_school)
    msg = bot.send_message(message.chat.id, f'Код: {response_add_school.status_code}',
                           reply_markup=menu.main_admin_menu())


def admin_add_school_name(message: telebot.types.Message):
    temp_schools[str(message.chat.id)] = School(message.text)
    msg = bot.send_message(message.chat.id, 'Ссылка на таблицу:')
    bot.register_next_step_handler(msg, admin_add_school_link)


@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    chat_id = message.chat.id
    user = get_user(chat_id)

    if not user:
        msg = bot.send_message(chat_id, texts.first_text, parse_mode='html')
        bot.register_next_step_handler(msg, auth_by_code_message)

    else:
        bot.send_message(chat_id, texts.welcome_text(user), reply_markup=menu.main_menu(user))


@bot.message_handler(commands=['help'])
def help_(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'help')


@bot.message_handler(commands=['admin'])
def admin(message: telebot.types.Message):
    if message.chat.id in list_of_admins_id:
        msg = bot.send_message(message.chat.id, texts.main_admin_menu, reply_markup=menu.main_admin_menu())
    else:
        msg = bot.send_message(message.chat.id, 'Вы не админ')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: telebot.types.CallbackQuery):
    if call.data == 'add_student_absent_by_teacher':
        absent = Absent(call.from_user.id)
        absent.accept = True
        temp_absents[str(call.from_user.id)] = absent

        msg = bot.edit_message_text(f'Выберите ученика. Напишите имя или фамилию частично', call.from_user.id,
                                    call.message.id)
        bot.register_next_step_handler(msg, choose_student, 'addAbsent')

    if call.data == 'add_student_absent_by_student':
        absent = Absent(call.from_user.id)
        temp_absents[str(call.from_user.id)] = absent

        msg = bot.edit_message_text(texts.choose_date_from_student,
                                    call.from_user.id,
                                    call.message.id, reply_markup=menu.choose_day('addAbsent'))

    elif call.data == 'main_admin_menu':
        msg = bot.edit_message_text(texts.main_admin_menu,
                                    call.from_user.id,
                                    call.message.id,
                                    reply_markup=menu.main_admin_menu())
    elif call.data == 'school_admin_menu':
        school_list = get_school_list()
        school_names_list = []
        for school in school_list:
            school_names_list.append(school["school_name"])

        msg = bot.edit_message_text(texts.all_schools_text.format(count=len(school_names_list)),
                                    call.from_user.id,
                                    call.message.id,
                                    reply_markup=menu.admin_school_list(school_names_list))

    elif call.data == 'show_student_absents':
        msg = bot.edit_message_text(f'Выберите ученика. Напишите имя или фамилию частично', call.from_user.id,
                                    call.message.id)
        bot.register_next_step_handler(msg, choose_student, "studentAbsents")

    elif call.data == 'show_class_absents':
        msg = bot.edit_message_text('Выберите дату',
                                    call.from_user.id,
                                    call.message.id, reply_markup=menu.choose_day('classAbsents'))

    elif call.data == 'choose_reason_other':
        msg = bot.edit_message_text('Напишите причину:', call.from_user.id, call.message.id)
        bot.register_next_step_handler(msg, choose_reason_other)

    elif call.data == 'add_new_school':
        msg = bot.edit_message_text('Название школы:', call.from_user.id, call.message.id)
        bot.register_next_step_handler(msg, admin_add_school_name)

    elif call.data.startswith('get_students_'):
        school_name = call.data.split('get_students_')[1]

        students_list = get_list_students(school_name)

        msg = bot.edit_message_text(str(students_list),
                                    call.from_user.id,
                                    call.message.id,
                                    reply_markup=menu.main_admin_menu())

    elif call.data.startswith('table_link_'):
        school_name = call.data.split('table_link_')[1]
        link = 'link'
        # TODO: Переделать этот метод когда появится соответствующий запрос в API
        school_list = get_school_list()
        for school in school_list:
            if school["school_name"] == school_name:
                link = school["link"]
        msg = bot.edit_message_text(link,
                                    call.from_user.id,
                                    call.message.id,
                                    reply_markup=menu.school_admin_table_link_menu(school_name))

    elif call.data.startswith('choose_student_nobody_'):
        prefix = call.data.split('choose_student_nobody_')[1]
        msg = bot.edit_message_text(f'Напишите имя или фамилию частично', call.from_user.id,
                                    call.message.id)
        bot.register_next_step_handler(msg, choose_student, prefix)

    elif call.data.startswith('choose_student_'):
        choose_student_call(call)

    elif call.data.startswith('choose_date_other_'):
        msg = bot.edit_message_text(f'Напишите дату в формате 2021-12-05',
                                    call.from_user.id,
                                    call.message.id)
        prefix = call.data.split('_')[-1]
        bot.register_next_step_handler(msg, choose_date_other, prefix)

    elif call.data.startswith('choose_date_'):
        prefix = call.data.split('_')[-1]
        choose_date(call, prefix)

    elif call.data.startswith('choose_reason_'):
        reason = call.data.split('choose_reason_')[1]
        temp_absents[str(call.from_user.id)].reason = reason
        response = send_absent(temp_absents[str(call.from_user.id)])
        if response == 201:
            msg = bot.edit_message_text('Запись успешно добавлена!', call.from_user.id, call.message.id,
                                        reply_markup=menu.main_teacher_menu())
        elif response == 400:
            msg = bot.edit_message_text('В эту дату данный ученик уже имеет запись об отсутствии',
                                        call.from_user.id, call.message.id,
                                        reply_markup=menu.main_teacher_menu())
        elif response == 999:
            msg = bot.edit_message_text('Запись отправлена Классному Руководителю на одобрение',
                                        call.from_user.id, call.message.id,
                                        reply_markup=menu.main_student_menu())
        elif response == 998:
            msg = bot.edit_message_text('Запись не может быть отправлена Классному Руководителю'
                                        ' (\nОбратись к нему лично, чтобы выяснить в чем дело',
                                        call.from_user.id, call.message.id,
                                        reply_markup=menu.main_student_menu())

    elif call.data.startswith('load_students_from_google_'):
        school_name = call.data.split('load_students_from_google_')[1]

        data_load_students_from_google = {
            "school_name": school_name
        }
        response_load_students_from_google = requests.post(base_url + 'school/students',
                                                           json=data_load_students_from_google)
        msg = bot.edit_message_text(f'Код: {response_load_students_from_google.status_code}',
                                    call.from_user.id,
                                    call.message.id,
                                    reply_markup=menu.main_admin_menu())

    elif call.data.startswith('load_teachers_from_google_'):
        school_name = call.data.split('load_teachers_from_google_')[1]

        data_load_students_from_google = {
            "school_name": school_name
        }
        response_load_students_from_google = requests.post(base_url + 'school/teachers',
                                                           json=data_load_students_from_google)
        msg = bot.edit_message_text(f'Код: {response_load_students_from_google.status_code}',
                                    call.from_user.id,
                                    call.message.id,
                                    reply_markup=menu.main_admin_menu())

    elif call.data.startswith('admin_select_school_'):
        school_name = call.data.split('admin_select_school_')[1]

        msg = bot.edit_message_text(texts.admin_school_menu.format(school_name=school_name),
                                    call.from_user.id,
                                    call.message.id,
                                    reply_markup=menu.school_admin_menu(school_name))
    elif call.data.startswith('approve_request_'):
        by_student_tg_id = call.data.split('approve_request_')[1]

        absent = temp_absents[by_student_tg_id]
        absent.accept = True
        response_send_absent = send_absent(absent)

        if response_send_absent == 201:
            msg = bot.send_message(by_student_tg_id,
                                   'Ваш учитель одобрил отсутствие!',
                                   reply_markup=menu.main_student_menu())

            msg = bot.send_message(call.from_user.id,
                                   'Запись успешно добавлена!',
                                   reply_markup=menu.main_teacher_menu())

        elif response_send_absent == 400:
            msg = bot.send_message(by_student_tg_id,
                                   'Учитель одобрил твоё отсутствие, но в эту дату у тебя уже стоит отсутствие, '
                                   'поэтому оно не было рассмотрено',
                                   reply_markup=menu.main_student_menu())

            msg = bot.send_message(call.from_user.id,
                                   'В эту дату данный ученик уже имеет запись об отсутствии',
                                   reply_markup=menu.main_teacher_menu())

    elif call.data.startswith('reject_request_'):
        by_student_tg_id = call.data.split('reject_request_')[1]

        msg = bot.send_message(by_student_tg_id,
                               'Ваш учитель отклонил отсутствие :(',
                               reply_markup=menu.main_student_menu())


def show_student_absents(code: str, name: str, call: telebot.types.CallbackQuery):
    request_query = {
        "code": code
    }
    response = requests.get(f'{base_url}student/absents', params=request_query).json()
    if len(response['absents']) == 0:
        msg = bot.edit_message_text(f'Студент {name} не пропускает', call.from_user.id, call.message.id,
                                    reply_markup=menu.main_teacher_menu())
    else:
        absent_student_print_list = [f'Пропуски студента {name}']
        for absent in response['absents']:
            absent_student_print_list.append(f"{absent['date']}: {absent['reason']}")
        msg = bot.edit_message_text("\n".join(absent_student_print_list), call.from_user.id, call.message.id,
                                    reply_markup=menu.main_teacher_menu())


def show_class_absents_for_current_teacher(date: str,
                                           message: telebot.types.Message = None,
                                           call: telebot.types.CallbackQuery = None):
    if message is not None:
        request_query = {
            "date": date,
            "tg_user_id": message.from_user.id
        }
        response = requests.get(f'{base_url}teacher/absents', params=request_query).json()
        if len(response['absents']) == 0:
            msg = bot.send_message(message.chat.id, f'На {date} пропусков нет',
                                   reply_markup=menu.main_teacher_menu())
        else:
            absent_student_print_list = [f'Пропуски на {date}']
            for absent in response['absents']:
                request_query = {
                    "code": absent['code']
                }
                student = requests.get(f'{base_url}student', params=request_query).json()
                absent_student_print_list.append(f"{student['name']} {student['surname']}: {absent['reason']}")
            msg = bot.send_message(message.chat.id, "\n".join(absent_student_print_list),
                                   reply_markup=menu.main_teacher_menu())
    if call is not None:
        request_query = {
            "date": date,
            "tg_user_id": call.from_user.id
        }
        response = requests.get(f'{base_url}teacher/absents', params=request_query).json()
        if len(response['absents']) == 0:
            msg = bot.edit_message_text(f'На {date} пропусков нет', call.from_user.id, call.message.id,
                                        reply_markup=menu.main_teacher_menu())
        else:
            absent_student_print_list = [f'Пропуски на {date}']
            for absent in response['absents']:
                request_query = {
                    "code": absent['code']
                }
                student = requests.get(f'{base_url}student', params=request_query).json()
                absent_student_print_list.append(f"{student['name']} {student['surname']}: {absent['reason']}")
            msg = bot.edit_message_text("\n".join(absent_student_print_list), call.from_user.id, call.message.id,
                                        reply_markup=menu.main_teacher_menu())


def choose_date_other(message: telebot.types.Message, prefix):
    if tools.validate_date(message.text):
        if prefix == 'addAbsent':
            temp_absents[str(message.chat.id)].date = message.text
            msg = bot.send_message(message.chat.id, f'Выберите причину отсутствия', reply_markup=menu.choose_reason())
        elif prefix == 'classAbsents':
            show_class_absents_for_current_teacher(message=message, date=message.text)
    else:
        msg = bot.send_message(message.chat.id, f'Некорректный формат даты. Напишите дату в формате 2021-12-05')
        bot.register_next_step_handler(msg, choose_date_other, prefix)


def choose_date(call, prefix):
    date = call.data.split('choose_date_')[1]
    date = date.split('_' + prefix)[0]
    day = datetime.timedelta(days=1)
    if date == 'today':
        date = datetime.date.today()
    elif date == 'tomorrow':
        date = datetime.date.today() + day
    elif date == 'day_after_tomorrow':
        date = datetime.date.today() + day + day

    if prefix == 'addAbsent':
        temp_absents[str(call.from_user.id)].date = str(date)
        msg = bot.edit_message_text(f'Выберите причину отсутствия', call.from_user.id, call.message.id,
                                    reply_markup=menu.choose_reason())
    elif prefix == 'classAbsents':
        show_class_absents_for_current_teacher(call=call, date=str(date))


def choose_reason_other(message: telebot.types.Message):
    temp_absents[str(message.chat.id)].reason = message.text
    response = send_absent(temp_absents[str(message.chat.id)])
    if response == 201:
        msg = bot.send_message(message.chat.id, 'Запись успешно добавлена!', reply_markup=menu.main_teacher_menu())
    elif response == 400:
        msg = bot.send_message(message.chat.id, 'В эту дату данный ученик уже имеет запись об отсутствии',
                               reply_markup=menu.main_teacher_menu())


def choose_student(message: telebot.types.Message, prefix):
    data_find_students = {
        "tg_user_id": message.chat.id,
        "name": message.text
    }
    response_find_students = requests.get(url=base_url + 'teacher/students_by_name', params=data_find_students)

    if response_find_students.status_code == 200:
        founded_students = response_find_students.json()['students']
        msg = bot.send_message(message.chat.id, f'Выберите из списка:',
                               reply_markup=menu.choose_student(founded_students, prefix))


def choose_student_call(call):
    code = call.data.split('choose_student_')[1]
    code, prefix = code.split('_')
    if prefix == 'addAbsent':
        temp_absents[str(call.from_user.id)].student_code = code

        data_find_student = {
            "code": code
        }
        response_find_student = requests.get(url=base_url + 'student', params=data_find_student)
        student = response_find_student.json()

        full_name = f"{student['surname']} {student['name']}"

        msg = bot.edit_message_text(f'Выбран ученик: {full_name}\nВыберите дату',
                                    call.from_user.id,
                                    call.message.id, reply_markup=menu.choose_day('addAbsent'))

    elif prefix == 'studentAbsents':
        data_find_student = {
            "code": code
        }
        response_find_student = requests.get(url=base_url + 'student', params=data_find_student)
        student = response_find_student.json()

        full_name = f"{student['surname']} {student['name']}"
        show_student_absents(call=call, name=full_name, code=data_find_student['code'])


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.infinity_polling()
