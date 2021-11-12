import json
import gspread

gc = gspread.service_account(filename='credentials.json')

table = gc.open_by_key("1QTbU7fX_VrcqEuI_9LoD-zpazTgyJydxHrFiUlTSjPk")

worksheet = table.get_worksheet(0)

with open('список.txt', encoding="utf-8") as f:
    text = f.read()

text = text.split('\n')[::2]

a = []
class_name = ''

for string in text:
    if 'Список учащихся ' in string:
        class_name = string[16:-6]
        continue
    string = string.split('.')[1]
    string = list(map(str.strip, string.strip().split()))
    a.append([*string, class_name.strip()])

print(*a)

worksheet.update(f'A2:D{len(a)+1}', [*a])

# with open('test_students.json', 'w') as file:
#     file.write(json.dumps(a))
