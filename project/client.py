import json
from socket import socket, AF_INET, SOCK_STREAM
import sys
import time
import logging
import argparse
import threading
import dis

sys.path.append('common\\')
from tests.err import ReqFieldMissingError
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
    TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import send_message, get_message
from decorators import logg
from metaclasses import ClientMeta

CLIENT_LOGGER = logging.getLogger('client')


class Client(threading.Thread, metaclass=ClientMeta):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        to = input('Введите имя получателя сообщения: ')
        message = input('Введите текст сообщения: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сфлормирован словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            CLIENT_LOGGER.info(f'Отправлено для {to}')
        except:
            CLIENT_LOGGER.critical('Потеряно соединение с сервером')
            exit(1)

    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение соединения...')
                CLIENT_LOGGER.info(f'Завершение работы пользователя')
                time.sleep(0.5)
                break
            elif command == 'help':
                self.print_help()
            else:
                print('Команда не распознана')

    def print_help(self):
        print('Введите одну из функций программы:')
        print('message - отправить сообщение \n'
              'help - запросить подсказки\n'
              'exit - выйти из программы')


class ClientReader(threading.Thread, metaclass=ClientMeta):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение от сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError):
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером ')
                break


@logg
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@logg
def process_responce(message):
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            CLIENT_LOGGER.critical(f'400: {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@logg
def parser_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, nargs='?')
    parser.add_argument('-m', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(f'попытка запуска клиента с неподходящим номером порта {server_port}')
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    server_address, server_port, client_name = parser_arg()
    print('Добро пожаловать в консольный мессенджер ')
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиент запущен с именем {client_name}')
    CLIENT_LOGGER.info(f'Запуск клиента с параметрами  {server_address}: порт {server_port}, имя {client_name}')
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_responce(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ {answer}')
        print('Установлено соединение с сервером ')
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(f'Не получилось подключиться к серверу {server_address}:{server_port}')
        exit(1)
    else:
        module_reciever = ClientReader(client_name, transport)
        module_reciever.daemon = True
        module_reciever.start()
        module_send = Client(client_name, transport)
        module_send.daemon = True
        module_send.start()
        CLIENT_LOGGER.info('Процессы запущены')
        while True:
            time.sleep(1)
            if module_reciever.is_alive() and module_send.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
