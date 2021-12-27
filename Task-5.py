""" Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтового в строковый
(предварительно определив кодировку выводимых сообщений)."""
import chardet
import platform
import subprocess


def ping_resource(arg):
    param_os = '-n' if platform.system().capitalize() == 'Windows' else '-c'
    lst = ['ping', param_os, '5', arg]

    process = subprocess.Popen(lst, stdout=subprocess.PIPE)
    for i in process.stdout:
        result_code = chardet.detect(i)
        print_line = i.decode(result_code['encoding']).encode(encoding='utf-8')
        print(print_line.decode(encoding='utf-8'))


ping_resource('youtube.com')
ping_resource('yandex.ru')
