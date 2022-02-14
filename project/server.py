import argparse
import os
import time
import socket
import sys
from select import select
import logging
from decorators import logg
from metaclasses import ServerMeta

sys.path.append('common\\')
from tests.err import IncorrectDataRecivedError
from common.variables import ACTION, DEFAULT_PORT, MAX_CONNECTIONS, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    MESSAGE, MESSAGE_TEXT, SENDER, EXIT, DESTINATION, RESPONSE_200, RESPONSE_400
from common.utils import get_message, send_message
from descriptors import Port

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOGGER = logging.getLogger('server')


@logg
def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


class Server(metaclass=ServerMeta):
    port = Port()

    def __init__(self, listen_address, listen_port):
        self.address = listen_address
        self.port = listen_port
        self.clients = []
        self.names = dict()
        self.messages = []

    def init_socket(self):
        LOGGER.info(f'Сервер запущен с потром {self.port}'
                    f'и адресом {self.address}')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)
        self.socket = transport
        self.socket.listen()

    def main_loop(self):
        self.init_socket()
        while True:
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Установлено соединение с {client_address}')
                self.clients.append(client)

            recv_data_list = []
            send_data_list = []
            err_list = []
            try:
                if self.clients:
                    recv_data_list, send_data_list, err_list = select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_list:
                for client_with_message in recv_data_list:
                    try:
                        self.process_client_message(get_message(client_with_message),client_with_message)
                    except:
                        LOGGER.info((f'Клиент {client_with_message.getpeername()} отключен'))
                        self.clients.remove(client_with_message)
            for message in self.messages:
                try:
                    self.process_message(message, send_data_list)
                except:
                    LOGGER.info(f'Связь с {message[DESTINATION]} потеряна')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    def process_message(self, message, listen_sock):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_sock:
            send_message(self.names[message[DESTINATION]], message)
            LOGGER.info(f'Сообщение отправлено {message[DESTINATION]} от {message[SENDER]}')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_sock:
            raise ConnectionError
        else:
            LOGGER.error(f'Пользователь {message[DESTINATION]} не был зарегистрирован')

    def process_client_message(self, message, client):
        LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return


def main():
    listen_address, listen_port = parse_arg()
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
