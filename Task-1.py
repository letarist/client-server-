"""
Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание
соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление в формат Unicode и
также проверить тип и содержимое переменных.
"""


# 1 variant

def dec_enc(lst):
    for item in lst:
        print(item)
        print(type(item))


if __name__ == '__main__':
    first_p = 'разработка'
    second_p = 'сокет'
    third_p = 'декоратор'
    lst = [first_p, second_p, third_p]
    dec_enc(lst)

    first_u = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
    second_u = '\u0441\u043e\u043a\u0435\u0442'
    third_u = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
    lst_unicode = [first_u, second_u, third_u]
    dec_enc(lst_unicode)


# 2 VARIANT
# result = []
# result_dec = []
# result_dec_str = []
# answ = input('Input word for decoding(do not enter anything to stop): ')
# result.append(answ)
# for i in range(len(answ)):
#     print(f'{result[i]}: type {type(result[i])}')
#     result_dec.append(result[i].encode('unicode_escape'))
#     print(type(result_dec[i]))
#     result_dec_str.append(
#         str(result[i].encode('unicode_escape')))  # для показа unicode символов, пришлось переводить в str
#     if r'\\' in result_dec_str[i]:
#         print(str(result_dec_str[i].replace(r'\\', '\\')))
#     else:
#         print(str(result_dec_str[i]))
#     answ = input('Input word for decoding(do not enter anything to stop): ')
#     if answ == '':
#         break
#     result.append(answ)
