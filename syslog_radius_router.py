# -*- coding: utf-8 -*-

"""Script routering Syslog-ng events to Radius."""

import re
import sys
import logging
import configparser
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary

###### укажите абсолютный путь к данному файлу ######
INITIAL_CONF_FILE = '/home/python-radius/initial.conf'
#####################################################

config = configparser.ConfigParser()
config.read(INITIAL_CONF_FILE)

RADIUS_IP = config['PYTHON SCRIPT']['RADIUS_IP']
RADIUS_SECRET = config['PYTHON SCRIPT']['RADIUS_SECRET']
RADIUS_DICT_PATH = config['PYTHON SCRIPT']['RADIUS_DICT_PATH']
LOG_PATH = config['PYTHON SCRIPT']['LOG_PATH'] 

class Send2Radius(object):
    """Класс для пересылки сообщений из Syslog-ng в Radius."""

    def __init__(self, conf_path, logger):
        """Инициализация объекта.

        :conf_path: - абсолютный путь к файлу конфигурации.
        В файле конфигурации задаются искомые в запросе параметры,
        а также соотвествующие им атрибуты словаря Radius.
        :logging: - модуль для записи событий в лог.
	"""
        conf = configparser.ConfigParser()
        conf.read(conf_path)
        self.alies_dict = {}
        self.additional_dict = {}
        self.logging = logger
        for indx in conf['ALIES']:
            # Создаем словарь с искомыми параметрами и атрибутами Radius.
            self.alies_dict[indx] = conf['ALIES'][indx]

        for field in conf['ADDITIONAL FIELDS']:
            # Создаем словарь для дополнительных полей, указанных в conf_path.
	    # Почему-то при чтении confiparser меняет все заглавные буквы на строчные.
            field = field.split('-')
            field = [word.capitalize() for word in field]
            field = '-'.join(field)
            self.additional_dict[field] = conf['ADDITIONAL FIELDS'][field]

    def send_message(self, text, radius_ip, secret, dict_path):
        """
        Публичный метод, отправляющий сообщение на сервер Radius.

        :text: - строка, передаваемая от syslog-ng
        (через стандартный входной поток stdin).
        :IP: - адресс сервера Radius.
        :secret: - секретный ключ.
        :ict_path: - абсолютный путь к словарю атрибутов Radius.
        """
        self._search(text)
        # Создаем клиент Радиус. Указывать порты отдельным
        # способом не надо, так как они по умолчанию уже заданы
        srv = Client(
            server=radius_ip,
            secret=secret.encode(),
            dict=Dictionary(dict_path),
        )
        # Создаем пакет аккаунтинга
        req = srv.CreateAcctPacket()
        # Создаем запрос по всем атрибутам и их значениям
        for key in self.result_dict:
            req[key] = self.result_dict[key]
        # Отправляем запрос
        reply = srv.SendPacket(req)
        # В случае успеха (ответный код 5), отправляем в лог
        if reply.code == pyrad.packet.AccountingResponse:
            logging.error('Successfully sent Acct packet to server.')
        else:
            # Иначе пишем в лог ошибку
            logging.error('Error with sending packet. Wrong server reply.')

    def _search(self, text):
        """Составление словаря атрибутов Radius и их значений."""
        self.result_dict = {}
        self.text_arr = ((text.lower()).strip(' ')).split(',')
        self._add_alies()
        self._add_field()

    def _add_alies(self):
        """Добавления в общий словарь атрибутов."""
        for key in self.alies_dict:
            for line in self.text_arr:
                if re.search(key, line):
                    line = line.split('=')
                    self.result_dict[self.alies_dict[key]] = line[1]
                    break

    def _add_field(self):
        """Добавление в общий словарь дополнительных параметров."""
        for key in self.additional_dict:
            self.result_dict[key] = self.additional_dict[key]

# Создаем лог для хранения событий скрипта
logging.basicConfig(filename=LOG_PATH, format='%(asctime)s %(message)s')

# Считываем значения из syslog-ng через стандартный ввод stdin
try:
    line_from_syslog = sys.stdin.readline()
except Exception as error:
    logging.error('Error with receiving line from syslog: {0}'.format(error))

# Отправляем сообщения в Radius
sending_router = Send2Radius(INITIAL_CONF_FILE, logging)

try:
    sending_router.send_message(
        line_from_syslog,
        RADIUS_IP,
        RADIUS_SECRET,
        RADIUS_DICT_PATH,
    )

except Exception as error:
    logging.error('Error with sending message to RADIUS: {0}'.format(error))
