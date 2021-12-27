"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое и
выполнить обратное преобразование (используя методы encode и decode).
"""


def encode_decode(lst):
    for arg in lst:
        e = arg.encode('utf-8')
        print(e)
        d = e.decode('utf-8')
        print(d)
        print("*" * 30)


if __name__ == '__main__':
    lst = ['разработка', 'администрирование', 'protocol', 'standard']
    encode_decode(lst)
