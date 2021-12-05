def validate_date(date: str):
    return True


def translate_reason(reason: str):
    replace_dict = {
        'family': 'Семейные обстоятельства',
        'event': 'Мероприятие',
        'ill': 'Заболевание'
    }
    return replace_dict.get(reason, reason)
