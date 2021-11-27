import telebot
from telebot import types
from fn import *
import menu
import gspread
import requests

API_TOKEN = '2138511910:AAGYBjjEsZyMQwAMDd5mdhoTX_osuAnqeDM'

gc = gspread.service_account(filename='credentials.json')

table = gc.open_by_key("1QTbU7fX_VrcqEuI_9LoD-zpazTgyJydxHrFiUlTSjPk")

bot = telebot.TeleBot(API_TOKEN)

base_url = 'http://localhost:5050/v1'


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message: types.Message):
    msg = bot.send_message(message.chat.id, """\
Здравствуйте, я бот для отметки отсутствия в школе
Пожалуйста введите свой код доступа:
""")

    bot.register_next_step_handler(msg, process_code_step)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = call.data


def process_code_step(message):
    chat_id = message.chat.id
    text = message.text
    if not validate_code(text):
        msg = bot.send_message(chat_id, 'ты лох')
        bot.register_next_step_handler(msg, process_code_step)
        return
    data = {
        'code': text,
        'tg_user_id': chat_id
    }

    response_teacher = requests.post(url=base_url + '/teacher/tg_auth', json=data)
    role = 'teacher'
    if response_teacher.status_code != 200:
        response_student = requests.post(url=base_url + '/student/tg_auth', json=data)
        if response_student.status_code != 200:
            msg = bot.send_message(chat_id, 'ты лох')
            bot.register_next_step_handler(msg, process_code_step)
            return
        role = 'student'

    data = {
        'tg_user_id': chat_id
    }
    response_get_user = requests.get(f'{base_url}/{role}', json=data)
    if response_get_user.status_code != 200:
        return

    response_get_user = response_get_user.json()

    msg = bot.send_message(chat_id,
                           f'Вы успешно авторизовались как учитель {response_get_user["class_name"]} класса - '
                           f'{response_get_user["name"]} {response_get_user["patronymic"]}',
                           reply_markup=menu.main_teacher_menu)


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.infinity_polling()
