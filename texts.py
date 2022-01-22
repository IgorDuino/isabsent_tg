from main import User

step_handler_command_error = 'Судя по всему это команда, пожалуйста отправьте её повторно'
first_text = 'Здравствуйте, я бот IsAbsent 👋\nЧтобы начать работу напишите мне ваш код авторизации\n\n' \
             '<a href="https://telegra.ph/CHto-takoe-kod-avtorizacii-i-kak-ego-poluchit-01-22">Что это и как его ' \
             'получить?</a>'

main_admin_menu = 'Главное меню админа'

all_schools_text = 'Всего {count} школ:'
admin_school_menu = 'Меню школы {school_name}'


def welcome_text(user: User):
    texts = {
        'teacher': f'Вы успешно авторизовались как учитель {user.full_name}',
        'student': f'Привет, {user.name}!'
    }

    return texts[user.role]


error = 'Error'


def help_text(user):
    return '@igorduino'
