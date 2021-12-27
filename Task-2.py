"""Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это необходимо в автоматическом, а не
 ручном режиме с помощью добавления литеры b к текстовому значению, (т.е. ни в коем случае не используя методы encode и
  decode) и определить тип, содержимое и длину соответствующих переменных."""


def bite_view(lst):
    for i in lst:
        inst = eval(f"b'{i}'")
        print(type(inst))
        print(inst)
        print(len(i))
        print('*' * 30)


if __name__ == '__main__':
    lst = ['class', 'function', 'method']
    bite_view(lst)
