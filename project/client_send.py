import json
from socket import socket, AF_INET, SOCK_STREAM
import sys
import time
import logging
import argparse

sys.path.append('common\\')
from tests.err import ReqFieldMissingError
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT
from common.utils import send_message, get_message
from decorators import logg

CLIENT_LOGGER = logging.getLogger('client')


@logg
def message_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от: {message[SENDER]} {message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера! {message}')


@logg
def create_message(sock, account_name='Guest'):
    message = input('введите сообщение для отправки.  \n Для выхода нажмите "Q":  ')
    if message == '!!!':
        sock.close()
        CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    messages = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформировано сообщение {messages}')
    return messages


@logg
def create_presence(account_name='Guest'):
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
    parser.add_argument('-m', '--mode', default='send', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(f'попытка запуска клиента с неподходящим номером порта {server_port}')
        sys.exit(1)
    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Указан недопустимы режим работы {client_mode}')
        sys.exit(1)

    return server_address, server_port, client_mode


@logg
def main():
    server_address, server_port, client_mode = parser_arg()
    CLIENT_LOGGER.info(f'Запуск клиента с параметрами: {server_address}:{server_port}, Режим работы {client_mode}')
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_responce(get_message(transport))
        CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
        print(answer)
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOGGER.error('не получилось декодировать')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}')
        sys.exit(1)
    except ReqFieldMissingError as missing_field:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_field.missing_field}')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Клиент работает в режиме отправки')
        else:
            print('Клиент работает в режиме приема')
        while True:
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_server(get_message(transport))
                except(ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно')
                    sys.exit(1)


if __name__ == '__main__':
    main()
