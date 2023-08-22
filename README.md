# add_hosts_proxmox_to_zabbix.py
Скрипт добаления Linux хостов из Proxmox в Zabbix для мониторинга

## Описание переменных
Переменные для авторизации в Proxmox VE:
 - `PROXMOX_USERNAME` - Пользователь
 - `PROXMOX_PASSWORD` - Пароль
 - `PROXMOX_URL` - URL

Переменные Zabbix
 - `ZABBIX_USER` - Пользователь
 - `ZABBIX_PASSWORD` = Пароль
 - `ZABBIX_URL` - URL
 - `ZABBIX_BASE_GROUP_NAME` - наименование группы, куда будут добавлены хосты
 - `ZABBIX_BASE_TEMPLATE_NAME` - наименование шаблона, который будет пременен к хостам

## Запуск
```bash
# Устанавливаем пакетный менеджер pip3
sudo apt install -y python3-pip

# Устанавливаем пакеты python3  из requirements.txt
pip3 install -r requirements.txt

# Изменяем значение переменных из раздела выше
vim add_hosts_proxmox_to_zabbix.py

# Запускаем скрипт
python3 add_hosts_proxmox_to_zabbix.py
```