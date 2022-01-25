import json
from socket import socket, AF_INET, SOCK_STREAM
import sys
import time
import logging

sys.path.append('common\\')
from tests.err import ReqFieldMissingError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT
from common.utils import send_message, get_message
from decorators import logg

CLIENT_LOGGER = logging.getLogger('client')


@logg
def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@logg
def process_ans(message):
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера:  {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


@logg
def main():
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            CLIENT_LOGGER.critical(f'Попытка запуска клиента с неподходящим портом {server_port}')
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('В качестве порта может быть указано только число')
        sys.exit(1)
    CLIENT_LOGGER.info(f'Запущен клиент с параметрами: адрес {server_address}, порт {server_port}')

    transport = socket(AF_INET, SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence()
    send_message(transport, message_to_server)
    try:
        answer = process_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
        print(answer)
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOGGER.error('не получилось декодировать')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}')
    except ReqFieldMissingError as missing_field:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_field.missing_field}')


if __name__ == '__main__':
    main()
