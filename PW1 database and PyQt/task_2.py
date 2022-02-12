from task_1 import check_ip, host_ping


def host_range_ping():
    while True:
        start = input('первоначальный адрес - ')
        try:
            ip = check_ip(start)
            oct_last = int(start.split('.')[3])
            break
        except Exception:
            print(Exception)
    while True:
        ip_last_oct = int(input('Сколько адресов проверить: '))
        if (oct_last + ip_last_oct) > 256:
            print('Меняем толкьо последний октет, число должно быть не больше 255')
        break
    hosting = [str(ip + i) for i in range(int(ip_last_oct))]
    return host_ping(hosting)


if __name__ == '__main__':
    host_range_ping()
