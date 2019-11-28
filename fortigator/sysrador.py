# -*- coding: utf-8 -*-

"""Module that aggregates all information."""

import os
import configparser
import logging
from fortigator.attributor import Attributor
from fortigator.domainator import Domainator
from fortigator.rador import Rador


class SysRador(object):
    """Sends username to Radius with some checking."""

    def __init__(self, path_to_config_file):
        """Init Sysrador object."""
        # Config file
        config = configparser.ConfigParser()
        config.read(path_to_config_file)

        # Get line from source
        logging.basicConfig(
            filename=config['RESULT_LOG']['LOG_PATH'],
            format='%(asctime)s %(message)s',
        )

        # Attributor settings
        dict_attributes_tuple = (
            config['ALIES'],
            config['ADDITIONAL FIELDS'],
        )
        self.attributor = Attributor(dict_attributes_tuple, logging)

        # Domanaitor and Ldap settings
        self.needed_attribute = config['TARGET_ATTR']['ATTR']
        ldap_conf = config['LDAP']
        ldap_settings_tuple = (
            ldap_conf['LDAP_URL'],
            ldap_conf['LDAP_USERNAME'],
            ldap_conf['LDAP_PSWD'],
            ldap_conf['LDAP_DOMAIN'],
            ldap_conf['LDAP_OU'],
        )
        self.domanaitor = Domainator(
            self.needed_attribute,
            ldap_settings_tuple,
            logging,
        )

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
            raw_attributes = self.attributor.create_attributes(
                self.needed_attribute,
                line,
            )
            if raw_attributes:
                attributes = self.domanaitor.get_attributes(raw_attributes)
                if attributes:
                    self.rador.send_message(attributes)


def get_source_file(conf):
    """Get path to message source."""
    conf = configparser.ConfigParser()
    conf.read(conf)
    return conf['SOURCE_MESSAGE']['LOG_PATH']


if __name__ == '__main__':
    path_to_dir = os.getcwd()
    path_to_conf = os.path.join(path_to_dir, 'initial.conf')
    source_message = get_source_file(path_to_conf)
    sysrad = SysRador(path_to_conf)
    with open(source_message, 'r') as source_file:
        syslog_lines = source_file.read().split('\n')
    for line in syslog_lines:
        sysrad.send(line)
    sysrad.send()
