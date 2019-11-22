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

    def send(self, line):
        """Works with single line."""
        if line:
            raw_attributes = self.attributor.create_attributes(self.needed_attribute, line)
            if raw_attributes:
                attributes = self.domanaitor.get_attributes(raw_attributes)
                if attributes:
                    self.rador.send_message(attributes)


if __name__ =='__main__':
    sysrad = SysRador('../initial.conf')
    source_file = open('/var/log/test.log', 'r')
    syslog_lines = source_file.read().split('\n')
    source_file.close()
    for line in syslog_lines:
        sysrad.send(line)
    sysrad.send()
