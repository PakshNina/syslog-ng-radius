# -*- coding: utf-8 -*-

"""Module that aggregates all information and """

from fortigator.attributor import Attributor
from fortigator.domainator import Domainator
from fortigator.rador import Rador
import configparser
import logging

class SysRador(object):
    """Sends username to Radius with some checking."""

    LDAP = 'LDAP'

    def __init__(self, path_to_config_file):
        """Init Sysrador object."""
        # Config file
        config = configparser.ConfigParser()
        config.read(path_to_config_file)

        # Get line from source
        self.text_line = self._get_sourse(config)
        logging.basicConfig(filename=config['RESULT_LOG']['LOG_PATH'], format='%(asctime)s %(message)s')

        # Attributor settings
        dict_attributes_tuple = (
            config['ALIES'],
            config['ADDITIONAL FIELDS'],
        )
        self.attributor = Attributor(dict_attributes_tuple, logging)

        # Domanaitor and Ldap settings
        self.needed_attribute = config['TARGET_ATTR']['ATTR']
        ldap_settings_tuple = (
            config[self.LDAP]['LDAP_URL'],
            config[self.LDAP]['LDAP_USERNAME'],
            config[self.LDAP]['LDAP_PSWD'],
            config[self.LDAP]['LDAP_DOMAIN'],
            config[self.LDAP]['LDAP_OU'],
        )
        self.domanaitor = Domainator(self.needed_attribute, ldap_settings_tuple, logging)

        # Radius settings
        radius_settings_tuple = (
            config['RADIUS']['IP'],
            config['RADIUS']['SECRET'],
            config['RADIUS']['DICT_PATH'],
        )
        self.rador = Rador(radius_settings_tuple, logging)

    def send(self):
        for line in self.text_line:
            if line:
                self._do_line(line)

    def _get_sourse(self, config):
        with open(config['SOURCE_MESSAGE']['LOG_PATH'], 'r') as file:
            return file.read().split('\n')

    def _do_line(self, line):
        raw_attributes = self.attributor.create_attributes(self.needed_attribute, line)
        if raw_attributes:
            attributes = self.domanaitor.get_attributes(raw_attributes)
            if attributes:
                self.rador.send_message(attributes)


if __name__ =='__main__':
    sysrad = SysRador('../initial.conf')
    sysrad.send()
