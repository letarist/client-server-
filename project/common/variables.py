"""Порт"""
DEFAULT_PORT = 7777
"""IP"""
DEFAULT_IP_ADDRESS = '127.0.0.1'
"""Очередь подключений"""
MAX_CONNECTIONS = 5
"""Максимальная длинна сообщения в байтах"""
MAX_PACKAGE_LENGTH = 1024
"""Кодировка"""
ENCODING = 'utf-8'
"""Ключи для JIM"""
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account-name'
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
SENDER = 'from'
DESTINATION = 'to'
EXIT = 'exit'
RESPONSE_400 = {
    ERROR: None,
    RESPONSE: 400
}
RESPONSE_200 = {
    RESPONSE: 200
}

