"""Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
 Проверить кодировку созданного файла (исходить из того, что вам априори неизвестна кодировка этого файла!). Затем
 открыть этот файл и вывести его содержимое на печать. ВАЖНО: файл должен быть открыт без ошибок вне зависимости от
 того, в какой кодировке он был создан!"""

import chardet

with open('text_files.txt', 'w', encoding='utf-8') as file:
    file.write('Системное программирование\nсокет\nдекоратор')


def text_encoding():
    with open('text_files.txt', 'rb') as file:
        content = file.readline()
    encoding = chardet.detect(content)
    print(f'Кодировка файла: {encoding["encoding"]}')
    return encoding


def write_unknown_encode_file(name_file):
    with open(name_file, 'r', encoding=text_encoding()['encoding']) as file:
        for line in file:
            print(line, end='')


write_unknown_encode_file('text_files.txt')  # можно заставить пользователя в аргументы названия файлов вводить руками
