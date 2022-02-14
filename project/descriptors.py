import logging

SERVER_LOGGING = logging.getLogger('server')


class Port:
    def __set__(self, instance, port):
        if not 1023 < port < 65536:
            SERVER_LOGGING.critical(f'У сервера не подходящий порт {port}')
            exit(1)
        instance.__dict__[self.name] = port

    def __set_name__(self, owner, name):
        self.name = name
