import logging
import sys

log = logging.getLogger('client')
formatter = logging.Formatter('%(levelname)-8s - %(asctime)s %(message)s')
file_handler = logging.FileHandler('client_log.log', encoding='utf_8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    log.setLevel(logging.WARNING)
    log.debug('Отладочная информация')
