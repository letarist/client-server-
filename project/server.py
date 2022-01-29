import argparse
import os
import time
from socket import socket, AF_INET, SOCK_STREAM
import sys
from select import select
import logging
from decorators import logg

sys.path.append('common\\')
from tests.err import IncorrectDataRecivedError
from common.variables import ACTION, DEFAULT_PORT, MAX_CONNECTIONS, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SERVER_LOGGER = logging.getLogger('server')


@logg
def process_client_message(message, messages_list, client):
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента - {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message and message[USER][
        ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad request'
        })
        return


@logg
def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    if not 1023 < namespace.p < 65536:
        SERVER_LOGGER.critical(f'{namespace.p} недопустимый порт')
        sys.exit(1)
    return listen_address, listen_port


@logg
def main():
    listen_address, listen_port = parse_arg()
    SERVER_LOGGER.info(f'Запущен сервер с адресом {listen_address}, портом {listen_port}')
    transtport = socket(AF_INET, SOCK_STREAM)
    transtport.bind((listen_address, listen_port))
    transtport.settimeout(0.5)

    clients = []
    messages = []
    transtport.listen(MAX_CONNECTIONS)
    while True:
        try:
            client, client_adress = transtport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с клиентом {client_adress}')
            clients.append(client)

        recv_data_list = []
        send_data_list = []
        err_list = []
        try:
            if clients:
                recv_data_list, send_data_list, err_list = select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_list:
            for client_with_message in recv_data_list:
                try:
                    process_client_message(get_message(client_with_message), messages, client_with_message)
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился')
                    clients.remove(client_with_message)

        if messages and send_data_list:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_list:
                try:
                    send_message(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился')
                    clients.remove(waiting_client)
    # try:
    #     if '-p' in sys.argv:
    #         listen_port = int(sys.argv[sys.argv.index('-p') + 1])
    #     else:
    #         listen_port = DEFAULT_PORT
    #     if listen_port < 1024 or listen_port > 65535:
    #         SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта'
    #                                f'{listen_port},Допустимы адреса с 1024 до 65535')
    #         sys.exit(1)
    #     SERVER_LOGGER.info(f'Запущен сервер с портом {listen_port} ')
    # except IndexError:
    #     print('После параметра \'-p\' необходимо указать номер порта')
    #     sys.exit(1)
    # except ValueError:
    #     print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535')
    #     sys.exit(1)
    # try:
    #     if '-a' in sys.argv:
    #         listen_address = sys.argv[sys.argv.index('-a') + 1]
    #     else:
    #         listen_address = ''
    # except IndexError:
    #     print('После параметра \'-a\' необходимо указать номер адреса')
    #
    # transport = socket(AF_INET, SOCK_STREAM)
    # transport.bind((listen_address, listen_port))
    #
    # transport.listen(MAX_CONNECTIONS)
    #
    # while True:
    #     client, client_address = transport.accept()
    #     SERVER_LOGGER.info(f'Установленно соединение с ПК {client_address}')
    #     try:
    #         message_from_client = get_message(client)
    #         SERVER_LOGGER.debug(f'Получено сообщение {message_from_client}')
    #         response = process_client_message(message_from_client)
    #         send_message(client, response)
    #         SERVER_LOGGER.debug(f'Соединение с клиентом {client_address} закрывается ')
    #         client.close()
    #     except IncorrectDataRecivedError:
    #         SERVER_LOGGER.error(f'От клиента {client_address} пришли некорректные данные ')


if __name__ == '__main__':
    main()
