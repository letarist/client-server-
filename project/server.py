import argparse
import configparser
import os
import threading
import time
import socket
import sys
from select import select
import logging
from decorators import logg
from metaclasses import ServerMeta
from server_database import ServerDataBase
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import HistoryWidget, ConfWindow, MainWindow, gui_create_model, create_stat_model

sys.path.append('common\\')
from tests.err import IncorrectDataRecivedError
from common.variables import ACTION, DEFAULT_PORT, MAX_CONNECTIONS, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    MESSAGE, MESSAGE_TEXT, SENDER, EXIT, DESTINATION, RESPONSE_200, RESPONSE_400, RESPONSE_202, LIST_INFO, ADD_CONTACT, \
    CONTACT_DEL, USERS_LIST, GET_CONTACTS
from common.utils import get_message, send_message
from descriptors import Port

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOGGER = logging.getLogger('server')
connection = False
conflag_lock = threading.Lock()


@logg
def parse_arg(default_port, default_address):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


class Server(threading.Thread, metaclass=ServerMeta):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.address = listen_address
        self.port = listen_port
        self.clients = []
        self.names = dict()
        self.messages = []
        self.database = database
        super().__init__()

    def init_socket(self):
        LOGGER.info(f'Сервер запущен с потром {self.port}'
                    f'и адресом {self.address}')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    def run(self):
        self.init_socket()
        while True:
            try:
                client, client_address = self.sock.accept()
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
                LOGGER.error(f'Ошибка работы с сокетами ')

            if recv_data_list:
                for client_with_message in recv_data_list:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
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
        global new_connection
        LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(
                    message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message and self.names[message[SENDER]] == client:
            self.messages.append(message)
            self.database.process_message(
                message[SENDER], message[DESTINATION])
            return

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.database.user_logout(message[ACCOUNT_NAME])
            LOGGER.info(
                f'Клиент {message[ACCOUNT_NAME]} корректно отключился от сервера.')
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with conflag_lock:
                new_connection = True
            return
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
                self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            send_message(client, response)
        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)
        elif ACTION in message and message[ACTION] == CONTACT_DEL and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)
        elif ACTION in message and message[ACTION] == USERS_LIST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0]
                                   for user in self.database.users_list()]
            send_message(client, response)

        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return


def main():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")

    listen_address, listen_port = parse_arg(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    database = ServerDataBase(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage('Progress')
    main_window.active_clients.setModel(gui_create_model(database))
    main_window.active_clients.resizeColumnsToContents()
    main_window.active_clients.resizeRowsToContents()

    def list_update():
        global connection
        if connection:
            main_window.active_clients.setModel(gui_create_model(database))
            main_window.active_clients.resizeColumnsToContents()
            main_window.active_clients.resizeRowsToContents()
            with conflag_lock:
                connection = False

    def show_statistic():
        global stat_window
        stat_window = HistoryWidget()
        stat_window.history.setModel(create_stat_model(database))
        stat_window.history.resizeColumnsToContents()
        stat_window.history.resizeRowsToContents()
        stat_window.show()

    def server_conf():
        global config_window
        config_window = ConfWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_address'])
        config_window.save_button.clicked.connect(save_settings_server)

    def save_settings_server():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['Settings']['default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as file_config:
                    config.write(file_config)
                    message.information(config_window, 'OK', 'Настройки сохранены')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен тыть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistic)
    main_window.config_button.triggered.connect(server_conf)
    server_app.exec_()

    # while True:
    #     command = input('Введите команду: ')
    #     if command == 'help':
    #         print_help()
    #     elif command == 'exit':
    #         break
    #     elif command == 'users':
    #         for user in sorted(database.all_users_list()):
    #             print(f'Пользователь {user[0]}: последний вход: {user[1]}')
    #     elif command == 'loghist':
    #         name = input('Введите имя пользователя: ')
    #         for user in sorted(database.all_history_login(name)):
    #             print(f'{user[0]} время входа: {user[1]}, Входа с {user[2]}: {user[3]}')
    #     elif command == 'connected':
    #         for user in sorted(database.all_active_users()):
    #             print(f'{user[0]}:{user[1]}, время установки соединения: {user[2]}')
    #     else:
    #         print('Команда не распознана')


if __name__ == '__main__':
    main()
