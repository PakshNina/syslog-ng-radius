# -*- coding: utf-8 -*-

"""Script routering Syslog-ng events to Radius."""

import re
import sys
import logging
import configparser
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import time
from multiprocessing import Pool

class Rador(object):
    """Класс для пересылки сообщений из Syslog-ng в Radius."""

    packet_send = 0

    def __init__(self, config, logging):
        """Инициализация объекта из файла ibitial.conf."""
        self.logging = logging
        self.radius_ip = config['RADIUS']['IP']
        self.radius_secret = config['RADIUS']['SECRET']
        self.radius_dict_path = config['RADIUS']['DICT_PATH']
        self.srv = Client(
            server=self.radius_ip,
            secret=self.radius_secret.encode(),
            dict=Dictionary(self.radius_dict_path),
        )

    def send_message(self, attributes_dict):
        self.attributes_dict = attributes_dict
        self.req = self.srv.CreateAcctPacket()
        # Создаем запрос по всем атрибутам и их значениям
        for key in self.attributes_dict:
            self.req[key] = self.attributes_dict[key]
        # Отправляем запрос
        reply = self.srv.SendPacket(self.req)
        # В случае успеха (ответный код 5), отправляем в лог
        if reply.code == pyrad.packet.AccountingResponse:
            self.packet_send += 1
            self.logging.error('Successfully sent Acct packet to server.')
        else:
            # Иначе пишем в лог ошибку
            self.logging.error('Error with sending packet. Wrong server reply. Rador< send_message')
