import dis


class ServerMeta(type):
    def __init__(cls, cname, bases, clsdict):
        methods = []
        attrs = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо на сервере')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета')
        super().__init__(cname, bases, clsdict)


class ClientMeta(type):
    def __init__(cls, cname, bases, cargs):
        method = []
        for func in cargs:
            try:
                res = dis.get_instructions(cargs[func])
            except TypeError:
                pass
            else:
                for i in res:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in method:
                            method.append(i.argval)
        for command in ('acccept', 'listen', 'socket'):
            if command in method:
                raise TypeError('В классе обнаружено использование запрещенного метода')
        if 'get_message' in method or 'send_message' in method:
            pass
        else:
            raise TypeError('Функции для работы с сокетами не вызываются ')
        super().__init__(cname, bases, cargs)
