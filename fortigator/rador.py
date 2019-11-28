# -*- coding: utf-8 -*-

"""Script routering Syslog-ng events to Radius."""

import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary


class Rador(object):
    """Класс для пересылки сообщений из Syslog-ng в Radius."""

    def __init__(self, radius_settings_tuple, logging):
        """Инициализация объекта из файла ibitial.conf."""
        self.packet_send = 0
        self.logging = logging
        radius_ip = radius_settings_tuple[0]
        radius_secret = radius_settings_tuple[1]
        radius_dict_path = radius_settings_tuple[2]
        self.srv = Client(
            server=radius_ip,
            secret=radius_secret.encode(),
            dict=Dictionary(radius_dict_path),
        )

    def send_message(self, attributes_dict):
        """Send radius packet."""
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
            self.logging.error('Error with sending packet.')
