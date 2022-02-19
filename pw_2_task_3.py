"""Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле
YAML-формата. Для этого:
Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом, отсутствующим в кодировке
ASCII (например, €);
Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml. При этом обеспечить стилизацию файла с
помощью параметра default_flow_style, а также установить возможность работы с юникодом: allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными."""

import yaml

data = {'items': ['disk', 'book', 'lamp', 'notepad'],
        'quantity': 4,
        'item_price': {
            'disk': '200€',
            'book': '500€',
            'lamp': '1000€',
            'notepad': '20€'
        }
        }
with open('file_1.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open('file_1.yaml', 'r', encoding='utf-8') as file:
    data_out = yaml.load(file, Loader=yaml.SafeLoader)

print(data_out == data)
