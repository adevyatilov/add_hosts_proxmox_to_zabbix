#!/usr/bin/python3
"""
   Добавляет хосты из Proxmox в Zabbix
"""

import re
# import getpass

import requests
from bs4 import BeautifulSoup
from pyzabbix import ZabbixAPI, ZabbixAPIException
from progressbar import ProgressBar, Percentage, Timer, Bar


# Переменные авторизации в Proxmox VE
PROXMOX_USERNAME = "user"
PROXMOX_PASSWORD = "password"
PROXMOX_URL = "https://proxmox.ru"

# Переменные Zabbix
ZABBIX_USER = 'Admin'
ZABBIX_PASSWORD = 'zabbix'
ZABBIX_URL = "http://127.0.0.1:7431"
ZABBIX_BASE_GROUP_NAME = "Linux servers"
ZABBIX_BASE_TEMPLATE_NAME = 'Linux by Zabbix agent'


def proxmox_get_hosts(url: str) -> list:
    """
        Парсит список хостов с Proxmox
        return: список хостов
    """
    session = requests.Session()

    # Получаем csrfmiddlewaretoken
    html = session.get(url).text
    csrfmiddlewaretoken = re.search(r"\w{64}", html).group(0)

    # password = getpass.getpass("Введите пароль: ")
    data = { # Данные для авторизации
        'username': PROXMOX_USERNAME,
        'password': PROXMOX_PASSWORD,
        'csrfmiddlewaretoken': csrfmiddlewaretoken
    }
    session.headers = { "Referer": url + "/admin/login/?next=/admin/" }
    response = session.post(url + "/admin/login/?next=/admin/", data=data)
    print('[{}]'.format(response.status_code), url + "/admin/login/?next=/admin/")

    # Получаем список виртуальных машин
    session.headers = { "Referer": url + "/admin/" }
    response = session.get(url + "/admin/servers/server/")
    print('[{}]'.format(response.status_code), url + "/admin/servers/server/")

    fied_hostname_html = BeautifulSoup(response.text, 'lxml') \
                            .find_all('th', class_="field-hostname")

    return [item.get_text() for item in fied_hostname_html]


def zabbix_add_hosts(hosts: list):
    zapi = ZabbixAPI(ZABBIX_URL)
    zapi.login(user=ZABBIX_USER, password=ZABBIX_PASSWORD)

    bar = ProgressBar(maxval=len(hosts), widgets=[Percentage(), Bar(), Timer()]).start()
    groupid = zabbix_get_groupid_by_name(zapi, ZABBIX_BASE_GROUP_NAME)
    templateid = zabbix_get_templateid_by_name(zapi, ZABBIX_BASE_TEMPLATE_NAME)
    for i, host in enumerate(hosts, start=1):
        try:
            zapi.host.create(
                host=host,
                status=1,
                interfaces=[{
                    "type": 1,
                    "main": "1",
                    "useip": 0,
                    "ip": "",
                    "dns": host,
                    "port": 10050
                }],
                groups=[{
                    "groupid": groupid
                }],
                templates=[{
                    "templateid": templateid
                }]
            )
        except ZabbixAPIException as err:
            # print(err)
            pass
        bar.update(i)


def zabbix_get_groupid_by_name(zapi: ZabbixAPI, name: str) -> int:
    """
        Возвращает groupid по наименованию группы
    """
    for group in zapi.hostgroup.get():
        if group['name'] == name:
            return group['groupid']
    # TODO Добавить исключение если группа по имени не найдется raise


def zabbix_get_templateid_by_name(zapi: ZabbixAPI, name: str) -> int:
    """
        Возвращает templateid по наименованию шаблона
    """
    for template in zapi.template.get():
        if template['name'] == name: # 'Linux by Zabbix agent'
            return template['templateid']
    # TODO Добавить исключение если шаблон по имени не найдется raise


def main():
    print("Авторизация в Proxmox {}".format(PROXMOX_URL.split('//')[1]))
    hosts = proxmox_get_hosts(PROXMOX_URL)
    zabbix_add_hosts(hosts)


if __name__ == "__main__":
    main()
