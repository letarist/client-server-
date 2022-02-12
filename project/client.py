import json
from socket import socket, AF_INET, SOCK_STREAM
import sys
import time
import logging
import argparse
import threading

sys.path.append('common\\')
from tests.err import ReqFieldMissingError
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
    TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import send_message, get_message
from decorators import logg

CLIENT_LOGGER = logging.getLogger('client')


@logg
def message_server(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message and DESTINATION in message and \
                    message[DESTINATION] == my_username:
                print(f'Получено сообщение от: {message[SENDER]} \n {message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от: {message[SENDER]} \n {message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера! {message}')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером')
            break


@logg
def create_exit_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@logg
def create_message(sock, account_name='Guest'):
    to_user = input('Введите кому отправить сообщение: ')
    message = input('Введите текст сообщения: ')
    messages = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформировано сообщение {messages}')
    try:
        send_message(sock, messages)
        CLIENT_LOGGER.info(f'Отправлено сообщение для {to_user}')
    except Exception as e:
        print(e)
        CLIENT_LOGGER.critical('Потеряно соединение с сервером ')
        sys.exit(1)


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
def print_help():
    print('Поддерживаемые комманды: \n message - Отправить сообщение,кому и текст сообщения вводятся отдельно'
          '\n help - вывести подсказки по коммандам'
          '\n exit - выход')


@logg
def user_interactive(sock, client_name):
    print_help()

    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, client_name)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(client_name))
            CLIENT_LOGGER.info('Завершение работы. Пользователь вышел! ')
            time.sleep(1)
            break
        else:
            print('Команда не распознана, попробуйте снова')


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


@logg
def main():
    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = parser_arg()

    """Сообщаем о запуске"""
    print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {client_name}')

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_responce(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # Если соединение с сервером установлено корректно,
        # запускаем клиентский процесс приёма сообщений
        receiver = threading.Thread(target=message_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
