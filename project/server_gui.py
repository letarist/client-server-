import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton, \
    QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from server_database import ServerDataBase


def gui_create_model(database):
    list_users = database.all_active_users()
    list_window = QStandardItemModel()
    list_window.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    for row in list_users:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        # Уберём миллисекунды из строки времени, т.к. такая точность не требуется.
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        list_window.appendRow([user, ip, port, time])
    return list_window


def create_stat_model(database):
    history_list = database.message_history()
    list_table = QStandardItemModel()
    list_table.setHorizontalHeaderLabels(['Имя клиента', 'Последний вход', 'Отправлено', 'Получено'])
    for row in history_list:
        user, last_seen, send, rec = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        send = QStandardItem(str(send))
        send.setEditable(False)
        rec = QStandardItem(str(rec))
        rec.setEditable(False)
        list_table.appendRow([user, last_seen, send, rec])

    return list_table


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.exitAction = QAction('Выход', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Обновить список', self)
        self.show_history_button = QAction('История клиентов', self)
        self.config_button = QAction('Настройки сервера', self)

        self.statusBar()

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_button)
        self.setFixedSize(800, 600)
        self.setWindowTitle('Server')
        self.label = QLabel('Список подключенных: ')
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        self.active_clients = QTableView(self)
        self.active_clients.move(10, 45)
        self.active_clients.setFixedSize(780, 400)

        self.show()


class HistoryWidget(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)
        self.history = QTableView(self)
        self.history.move(10, 15)
        self.history.setFixedSize(580, 620)
        self.show()


class ConfWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(365, 260)
        self.setWindowTitle('SETTINGS')
        self.db_path_label = QLabel('Путь до базы данных : ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton('Найти...', self)
        self.db_path_select.move(275, 28)

        def open_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_dialog)

        self.db_file_line = QLabel('Имя файла базы данных: ', self)
        self.db_file_line.move(10, 68)
        self.db_file_line.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel('Номер порта соединений: ', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel(' оставьте это поле пустым, чтобы\n принимать соединения с любых адресов.', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.move(190, 220)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 228)
        self.close_button.clicked.connect(self.close)
        self.show()

# if __name__ == '__main__':
# app = QApplication(sys.argv)
# main_window = MainWindow()
# main_window.statusBar().showMessage('Test Statusbar Message')
# test_list = QStandardItemModel(main_window)
# test_list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
# test_list.appendRow(
#     [QStandardItem('test1'), QStandardItem('192.198.0.5'), QStandardItem('23544'), QStandardItem('16:20:34')])
# test_list.appendRow(
#     [QStandardItem('test2'), QStandardItem('192.198.0.8'), QStandardItem('33245'), QStandardItem('16:22:11')])
# main_window.active_clients.setModel(test_list)
# main_window.active_clients.resizeColumnsToContents()
# app.exec_()

# app = QApplication(sys.argv)
# dial = ConfWindow()
#
# app.exec_()

# app = QApplication(sys.argv)
# window = HistoryWidget()
# test_list = QStandardItemModel(window)
# test_list.setHorizontalHeaderLabels(
#     ['Имя Клиента', 'Последний раз входил', 'Отправлено', 'Получено'])
# test_list.appendRow(
#     [QStandardItem('test1'), QStandardItem('Fri Dec 12 16:20:34 2020'), QStandardItem('2'), QStandardItem('3')])
# test_list.appendRow(
#     [QStandardItem('test2'), QStandardItem('Fri Dec 12 16:23:12 2020'), QStandardItem('8'), QStandardItem('5')])
# window.history.setModel(test_list)
# window.history.resizeColumnsToContents()
#
# app.exec_()
