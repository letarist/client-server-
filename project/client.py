import datetime
import json
import socket
import sys
import time
import logging
import argparse
import threading
import dis
from err import ServerError

sys.path.append('common\\')
from tests.err import ReqFieldMissingError
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
    TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT, GET_CONTACTS, LIST_INFO, ADD_CONTACT, CONTACT_DEL, USERS_LIST
from common.utils import send_message, get_message
from decorators import logg
from metaclasses import ClientMeta
from client_database import ClientDataBase

CLIENT_LOGGER = logging.getLogger('client')
sock_lock = threading.Lock()
database_lock = threading.Lock()


class Client(threading.Thread, metaclass=ClientMeta):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
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
        with database_lock:
            if not self.database.check_user(to):
                CLIENT_LOGGER.error(f'Попытка отправить сообщение незарегистрированому получателю: {to}')
                return
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сфлормирован словарь сообщения: {message_dict}')
        with database_lock:
            self.database.save_message(self.account_name, to, message)

        with sock_lock:
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
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_exit_message())
                    except:
                        pass
                print('Завершение соединения...')
                CLIENT_LOGGER.info(f'Завершение работы пользователя')
                time.sleep(0.5)
                break
            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contact()
                for contact in contacts_list:
                    print(contact)
            elif command == 'edit':
                self.edit_contacts()
            elif command == 'history':
                self.message_history()
            elif command == 'help':
                self.print_help()
            else:
                print('Команда не распознана')

    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def message_history(self):
        answer = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if answer == 'in':
                history_list = self.database.get_history(to_user=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif answer == 'out':
                histry_list = self.database.get_history(from_user=self.account_name)
                for message in histry_list:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} '
                          f'от {message[3]}\n{message[2]}')

    def edit_contacts(self):
        answer = input('Для удаления введите del, для добавления add: ')
        if answer == 'del':
            edit = input('Введите имя удаляемого контакта: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    CLIENT_LOGGER.error('Невозможно удалить не существующий контакт')
        elif answer == 'edit':
            edit = input('Введите имя добавляемого контакта: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit)
                    except ServerError:
                        CLIENT_LOGGER.error('Не удалось отправить информацию на сервер.')


class ClientReader(threading.Thread, metaclass=ClientMeta):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    def run(self):
        while True:
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)
                except OSError as err:
                    if err.errno:
                        CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                        break
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                    break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                            and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                        print(f'\n Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')

                        with database_lock:
                            try:
                                self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                            except Exception as e:
                                print(e)
                                CLIENT_LOGGER.error('Ошибка взаимодействия с базой данных')

                        CLIENT_LOGGER.info(
                            f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    else:
                        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


@logg
def create_presence(account_name):
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
def process_responce(message):
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            CLIENT_LOGGER.critical(f'400: {message[ERROR]}')
            raise ServerError(f'400 : {message[ERROR]}')
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


def req_contact_list(sock, name):
    CLIENT_LOGGER.debug(f'Запрос списка контактов для пользователя {name}')
    answer = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    CLIENT_LOGGER.debug(f'Сформирован запрос {answer}')
    send_message(sock, answer)
    ans = get_message(sock)
    CLIENT_LOGGER.debug(f'Получен ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def add_contact(sock, username, contact):
    CLIENT_LOGGER.debug(f'Создание контакта {contact}')
    answer = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, answer)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Ошибка создания контакта')
    print('Удалось создать контакт')


def user_list_request(sock, username):
    CLIENT_LOGGER.debug(f'Запрос списка известных пользователей {username}')
    req = {
        ACTION: USERS_LIST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def remove_contact(sock, name, contact):
    CLIENT_LOGGER.debug(f'Запрос на удаление {contact}')
    req = {
        ACTION: CONTACT_DEL,
        TIME: time.time(),
        USER: name,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    answer = get_message(sock)
    if RESPONSE in answer and answer[RESPONSE] == 200:
        print(f'Контакт {contact} удален!')
    else:
        raise ServerError('Ошибка удаления контакта')


def database_load(sock, database, username):
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        CLIENT_LOGGER.error('Ошибка запроса списка известных пользователей.')
    else:
        database.add_users(users_list)
    try:
        contacts_list = req_contact_list(sock, username)
    except ServerError:
        CLIENT_LOGGER.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    server_address, server_port, client_name = parser_arg()
    print('Добро пожаловать в консольный мессенджер ')
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиент запущен с именем {client_name}')
    CLIENT_LOGGER.info(f'Запуск клиента с параметрами  {server_address}: порт {server_port}, имя {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.settimeout(1)

        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_responce(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(f'Не получилось подключиться к серверу {server_address}:{server_port}')
        exit(1)
    else:
        database = ClientDataBase(client_name)
        database_load(transport, database, client_name)
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
