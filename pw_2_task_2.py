"""Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах. Написать
скрипт, автоматизирующий его заполнение данными. Для этого:
Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity), цена
(price), покупатель (buyer), дата (date). В это словаре параметров обязательно должны присутствовать юникод-символы,
отсутствующие в кодировке ASCII.
Функция должна предусматривать запись данных в виде словаря в файл orders.json. При записи данных указать величину
отступа в 4 пробельных символа;
Необходимо также установить возможность отображения символов юникода: ensure_ascii=False;
Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра."""

import json


def write_or_json(item, quantity, price, buyer, date):
    with open('orders.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    with open('orders_parse.json', 'a', encoding='utf-8') as file_parse:
        orders_list = data['orders']
        info = {
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date
        }
        orders_list.append(info)
        json.dump(data, file_parse, indent=4,ensure_ascii=False)


if __name__ == '__main__':
    write_or_json('Диск', '20', '2500', 'Олег', '23.10.2021')
    write_or_json('Книга', '2', '250', 'Алексей', '23.11.2011')
