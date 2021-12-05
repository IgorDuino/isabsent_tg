def validate_date(date: str):
    try:
        data = data.split('-')
        if len(data) == 3:
            if len(data[0]) == 4 and data[0].isdigit():
                if len(data[1]) < 3 and data[1].isdigit():
                    if len(data[2]) < 3 and data[2].isdigit():
                        return True
    except:
        pass
    return False


def translate_reason(reason: str):
    replace_dict = {
        'family': 'Семейные обстоятельства',
        'event': 'Мероприятие',
        'ill': 'Заболевание'
    }
    return replace_dict.get(reason, reason)
