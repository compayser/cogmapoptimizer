import socket
import string
import random


def get_ip_string():
    """
    Генерирует строку с текущим IP-адресом
    :return: строка с текущим IP-адресом или "0.0.0.0" при невозможности его определения
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("11.22.33.44", 80))
        result = s.getsockname()[0]
    except socket.error:
        result = "0.0.0.0"
    s.close()
    ip1 = int(result.split(".")[0])
    ip2 = int(result.split(".")[1])
    ip3 = int(result.split(".")[2])
    ip4 = int(result.split(".")[3])
    result = f"{ip1:03d}-{ip2:03d}-{ip3:03d}-{ip4:03d}"
    return result.replace(".", "-")


def get_random_string(length):
    """
    Генерирует случайную строку из заглавных латинских букв и десятичных цифр
    :param length: число символов в генерируемой строке
    :return: сгенерированная строка
    """
    abc = string.ascii_uppercase
    abc = abc.join("0123456789")
    return ''.join(random.choice(abc) for _ in range(length))


def get_uid():
    """
    Генерирует уникальный идентификатор на базе IP и случайно сгенерированных строк
    :return: сгенерированный UID, состоящий из 8 групп по 3 символа, разделенных дефисом
    """
    result = get_ip_string()
    result = result + "-" + get_random_string(3)
    result = result + "-" + get_random_string(3)
    result = result + "-" + get_random_string(3)
    result = result + "-" + get_random_string(3)
    return result
