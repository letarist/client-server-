"""
Определить, какие из слов, поданных на вход программы, невозможно записать в байтовом типе. Для проверки правильности
работы кода используйте значения: «attribute», «класс», «функция», «type»
"""


def exception(lst):
    for i in lst:
        try:
            i.encode('ascii')
        except UnicodeEncodeError:
            print(f'Слово {i} невозможно перевести в bytes')


if __name__ == '__main__':
    lst = ["attribute", 'класс', 'функция', 'type']
    exception(lst)
