import telebot
from telebot import types
from fn import find_student
import menu
import gspread

API_TOKEN = '2138511910:AAGYBjjEsZyMQwAMDd5mdhoTX_osuAnqeDM'

user_dict = {}

gc = gspread.service_account(filename='credentials.json')

table = gc.open_by_key("1QTbU7fX_VrcqEuI_9LoD-zpazTgyJydxHrFiUlTSjPk")


class User:
    def __init__(self, role):
        self.role = role
        self.name = None
        self.age = None
        self.sex = None


bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message: types.Message):
    msg = bot.send_message(message.chat.id, """\
Здравствуйте, я бот для отметки отсутствия в школе
Пожалуйста выберите роль:
""", reply_markup=menu.start)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = call.data
    if data == 'student':
        user = User(data)
        user_dict[user_id] = user

        msg = bot.edit_message_text('Отлично, теперь напиши своё Имя и Фамилию', user_id, call.message.id)
        bot.register_next_step_handler(msg, process_name_step)
    elif data == 'teacher':
        pass
    elif data == 'меня тут нет':
        msg = bot.send_message(user_id, 'Попробуй написать немного подругому или более подробно своё ФИО. '
                                        'Если это не поможет Обратись к @igorduino или к @SvinoBuddist')
        bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    chat_id = message.chat.id
    text = message.text

    user_dict[chat_id].name = text
    find_res = find_student(table, text)

    if len(find_res) == 0:
        msg = bot.send_message(chat_id, 'К сожалению я не нашёл тебя  своём списке... Попробуй написать по-другому')
        bot.register_next_step_handler(msg, process_name_step)
    else:
        keyboard = types.InlineKeyboardMarkup()
        for student in find_res:
            keyboard.add(types.InlineKeyboardButton(text=student[0], callback_data=student[0]))

        keyboard.add(types.InlineKeyboardButton(text='❌ Меня тут нет', callback_data='меня тут нет'))

        msg = bot.send_message(chat_id, f'Я нашёл {len(find_res)} похожих вариантов. Если ты тут есть нажми '
                                        f'на себя', reply_markup=keyboard)

        # bot.register_next_step_handler(msg, process_age_step)


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        if not age.isdigit():
            msg = bot.reply_to(message, 'Age should be a number. How old are you?')
            bot.register_next_step_handler(msg, process_age_step)
            return
        user = user_dict[chat_id]
        user.age = age
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Male', 'Female')
        msg = bot.reply_to(message, 'What is your gender', reply_markup=markup)
        bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_sex_step(message):
    try:
        chat_id = message.chat.id
        sex = message.text
        user = user_dict[chat_id]
        if (sex == u'Male') or (sex == u'Female'):
            user.sex = sex
        else:
            raise Exception("Unknown sex")
        bot.send_message(chat_id,
                         'Nice to meet you ' + user.name + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
    except Exception as e:
        bot.reply_to(message, 'oooops')


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.infinity_polling()
