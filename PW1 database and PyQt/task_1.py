import ipaddress
import platform
import subprocess
import threading

result_dct = {'Доступные': '', 'Не доступные': ''}


def check_ip(value):
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        raise Exception('Некорректный ip адрес')
    return ip


def ping_proc(ip):
    process = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', process, '1', str(ip)]
    res = subprocess.Popen(args, stdout=subprocess.PIPE)
    if res.wait() == 0:
        result_dct['Доступные'] += f"{str(ip)}\n"
    else:
        result_dct['Не доступные'] += f"{str(ip)}\n"
    print(f'Доступные узлы - {str(ip)}\n' if res.wait() == 0 else f'Недоступные узлы {str(ip)}\n')
    return result_dct


def host_ping(addr):
    for address in addr:
        try:
            ip = check_ip(address)
        except Exception:
            print(f'Это доменное имя - {address}')
            ip = address
        thread = threading.Thread(target=ping_proc, args=(ip,))
        thread.start()
    return ping_proc(ip)


if __name__ == '__main__':
    addr = ['vk.com', 'aboba.ru', 'google.ru', 'jkj', '8.8.8.8']
    host_ping(addr)
