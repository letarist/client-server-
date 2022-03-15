import tabulate
from task_2 import host_range_ping


def host_range_ping_tab():
    dct = host_range_ping()
    print(tabulate.tabulate([dct], headers='keys', tablefmt='pipe', stralign='left'))


if __name__ == '__main__':
    host_range_ping_tab()
