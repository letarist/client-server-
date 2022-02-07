import argparse
import os
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
from select import select
import logging
from decorators import logg

sys.path.append('common\\')
from tests.err import IncorrectDataRecivedError
from common.variables import ACTION, DEFAULT_PORT, MAX_CONNECTIONS, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    MESSAGE, MESSAGE_TEXT, SENDER, EXIT, DESTINATION, RESPONSE_200, RESPONSE_400
from common.utils import get_message, send_message

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOGGER = logging.getLogger('server')


@logg
def process_client_message(message, messages_list, client, clients, names):
    LOGGER.debug(f'Разбор сообщения от клиента - {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            responce = RESPONSE_400
            responce[ERROR] = 'Такое имя уже есть'
            send_message(client, responce)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    elif ACTION in message and message[
        ACTION] == MESSAGE and TIME in message and MESSAGE_TEXT in message and DESTINATION in message and SENDER in message:
        messages_list.append(message)
        return
    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос не корректен'
        send_message(client, response)
        return


def process_message(message, names, listen_socks):

    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


@logg
def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    if not 1023 < namespace.p < 65536:
        LOGGER.critical(f'{namespace.p} недопустимый порт')
        sys.exit(1)
    return listen_address, listen_port


@logg
def main():

    listen_address, listen_port = parse_arg()

    LOGGER.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')
    transport = socket(AF_INET, SOCK_STREAM)
    transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)
    clients = []
    messages = []
    names = dict()  # {client_name: client_socket}
    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Установлено соедение с ПК {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select(clients, clients, [], 0)
        except OSError:
            pass
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except Exception:
                    LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_with_message)
        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
