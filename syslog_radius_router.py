import re
import sys
import logging
import configparser
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary


class Send2Radius():
    '''Класс для пересылки сообщений из Syslog-ng в Radius.'''

    def __init__(self, conf_path, logging):
        '''
	Инициализация объекта.
        :conf_file: - полный путь к файлу конфигурации.
        В файле конфигурации задаются искомые в запросе параметры,
        а также соотвествующие им атрибуты словаря Radius.
        :logging: - модуль для записи событий в лог.
	'''
        conf = configparser.ConfigParser()
        conf.read(conf_path)
        self.alies_dict = {}
        self.additional_dict = {}
        self.logging = logging
        for i in conf['ALIES']:
            '''Создаем словарь с искомыми параметрами и атрибутами Radius.'''
            self.alies_dict[i] = conf['ALIES'][i]

        for field in conf['ADDITIONAL FIELDS']:
            '''Создаем словарь для дополнительных полей, указанных в conf_path.
	    Почему-то при чтении confiparser меняет все заглавные буквы на строчные.'''
            field = field.split('-')
            field = list(map(lambda x: x.capitalize(), field))
            field = '-'.join(field)
            self.additional_dict[field] = conf['ADDITIONAL FIELDS'][field]

    def _search(self, text):
        '''Внутренний метод, составляющий словарь атрибутов Radius и их значений.'''
        self.result_dict = {}
        self.text_arr = ((text.lower()).strip(' ')).split(',')
        self._add_alies()
        self._add_field()

    def _add_alies(self):
        '''Внутренний метод для добавления в общий словарь атрибутов
        и их значений'''
        for key in self.alies_dict:
            for line in self.text_arr:
                if re.search(key, line):
                    line = line.split('=')
                    self.result_dict[self.alies_dict[key]] = line[1]
                    continue

    def _add_field(self):
        '''Внутренний метод для добавления в общий словарь
        дополнительных параметров. '''
        for key in self.additional_dict:
            self.result_dict[key] = self.additional_dict[key]

    def send_message(self, text, IP, port, secret, dict_path):
        '''Публичный метод, отправляющий сообщение на сервер Radius.'''
        self._search(text)
        # Создаем клиент Радиус. Указывать порты отдельным способом не надо,
        # Так как они по умолчанию уже заданы
        srv = Client(server=IP, secret=secret.encode(), dict=Dictionary(dict_path))
        # Создаем пакет аккаунтинга
        req = srv.CreateAcctPacket()
        # Создаем запрос по всем атрибутам и их значениям
        for key in self.result_dict:
            req[key] = self.result_dict[key]
        # Отправляем запрос
        reply = srv.SendPacket(req)
        # В случае успеха (ответный код 5), отправляем в лог
        if reply.code == pyrad.packet.AccountingResponse:
            logging.error('Successfull')
        else:
            # Иначе пишем в лог ошибку
            logging.error('Error')

# Пытаемся выполнять нашу программу, в случае ошибки записываем ее в лог 
try:
    logging.basicConfig(filename='/var/log/syslog-python.log', format='%(asctime)s %(message)s')
    text = sys.stdin.readline()
    send = Send2Radius('/home/python-radius/initial.conf', logging)
    send.send_message(text, '10.31.46.196', 1813, 'q1q1q1Q!Q!Q!', '/home/python-radius/dictionary')
except Exception as e:
    logging.error('####fatal error#####')
    logging.error(e)
    logging.error('####fatal error######')
