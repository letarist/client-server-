"""Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание
данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и поместить в
него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных
через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv()."""
import chardet
import csv
import re


def get_data():
    os_prod = []
    os_name = []
    os_code = []
    os_type = []
    main_data = []

    get_file_data = ['info_1.txt', 'info_2.txt', 'info_3.txt']
    for i in get_file_data:
        with open(f'{i}', 'rb') as file_name:
            data_read = file_name.read()
            encode_data = chardet.detect(data_read)
            data = data_read.decode(encode_data['encoding'])

        prod = re.compile(r'Изготовитель системы:\s*\S*')
        os_prod.append(prod.findall(data)[0].split()[2])

        name = re.compile(r'Windows\s*\S*')
        os_name.append(name.findall(data)[0])

        code = re.compile(r'Код продукта:\s*\S*')
        os_code.append(code.findall(data)[0].split()[2])

        type = re.compile(r'Тип системы:\s*\S*')
        os_type.append(type.findall(data)[0].split()[2])

    head = ['Изготовитель системы', 'Название операционной системы', 'Код ОС', 'Тип системы']
    main_data.append(head)

    rows = [os_prod, os_name, os_code, os_type]
    for i in range(len(rows[0])):
        main_data.append([os_prod[i], os_name[i], os_code[i], os_type[i]])
    return main_data


def write_main_data(result):
    main_data = get_data()
    with open(result, 'w', encoding='utf-8') as res:
        write = csv.writer(res)
        for row in main_data:
            write.writerow(row)


if __name__ == '__main__':
    write_main_data('result_for_file.csv')
