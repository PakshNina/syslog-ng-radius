# -*- coding: utf-8 -*-

"""Module that aggregates all information and """

from fortigator.attributor import Attributor
from fortigator.domainator import Domainator
from fortigator.rador import Rador
import configparser
import logging

class SysRador(object):
    """Sends username to Radius with some checking."""

    def __init__(self, path_to_config_file):
        """Init Sysrador object."""
        config = configparser.ConfigParser()
        config.read(path_to_config_file)
        self.text_line = self._get_sourse(config)
        logging.basicConfig(filename=config['RESULT_LOG']['LOG_PATH'], format='%(asctime)s %(message)s')
        self.attributor = Attributor(config, logging)
        self.domanaitor = Domainator(logging, config)
        self.rador = Rador(config, logging)

    def send(self):
        for line in self.text_line:
            if line:
                self._do_line(line)

    def _get_sourse(self, config):
        with open(config['SOURCE_MESSAGE']['LOG_PATH'], 'r') as file:
            return file.read().split('\n')

    def _do_line(self, line):
        raw_attributes = self.attributor.create_attributes(line)
        if raw_attributes:
            attributes = self.domanaitor.get_attributes(raw_attributes)
            if attributes:
                self.rador.send_message(attributes)


if __name__ =='__main__':
    sysrad = SysRador('../initial.conf')
    sysrad.send()
