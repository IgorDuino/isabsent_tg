import gspread
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

gc = gspread.service_account(filename='credentials.json')

table = gc.open_by_key("1QTbU7fX_VrcqEuI_9LoD-zpazTgyJydxHrFiUlTSjPk")

worksheet = table.get_worksheet(-1)


def find_student(table, worksheet_name, key):
    student_list = table.worksheet(worksheet_name)
    data = student_list.get_all_values()[1:]
    find = process.extract(key, [' '.join(x[:-1]) for x in data])
    print(find)


find_res = find_student(table, "Учащиеся", input())
print(find_res)
