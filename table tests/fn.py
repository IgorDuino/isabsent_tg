import gspread
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime

# gc = gspread.service_account(filename='credentials.json')
#
# table = gc.open_by_key("1QTbU7fX_VrcqEuI_9LoD-zpazTgyJydxHrFiUlTSjPk")
#
# worksheet = table.get_worksheet(-1)


def find_student(table, key):
    student_list = table.worksheet("Учащиеся")
    data = student_list.get_all_values()[1:]
    find = process.extract(key, [' '.join(x) for x in data], limit=3)
    find_res = []

    for e in find:
        if e[1] != 0:
            find_res.append(e)
    return find_res

#
# find_res = find_student(table, input())
# print(find_res)
