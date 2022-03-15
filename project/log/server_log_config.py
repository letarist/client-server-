import logging
from logging import handlers
import sys

log = logging.getLogger('server')
formatter = logging.Formatter('%(levelname)-8s - %(asctime)s - %(message)s')
file_handler = handlers.TimedRotatingFileHandler('server_log.log', when='D', interval=1, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    log.setLevel(logging.DEBUG)
    log.debug('Отладочная информация')
