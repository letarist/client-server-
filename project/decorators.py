import sys
import logging

import log.client_log_config
import log.server_log_config
import traceback

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def logg(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        LOGGER.debug(f'Была вызвана функция {func.__name__} с параметрами {args} , {kwargs}'
                     f'Вызов из модуля {func.__module__}'
                     f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}')
        return res

    return wrapper
