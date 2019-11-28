# -*- coding: utf-8 -*-

"""Script run from console."""

import os
import configparser
from fortigator.sysrador import SysRador


def get_source_file(path_to_conf):
    """Get path to message source."""
    conf = configparser.ConfigParser()
    conf.read(path_to_conf)
    return conf['SOURCE_MESSAGE']['LOG_PATH']


if __name__ == '__main__':
    path_to_dir = os.getcwd()
    path_to_conf = os.path.join(path_to_dir, 'initial.conf')

    source_message = get_source_file(path_to_conf)
    with open(source_message, 'r') as source_file:
        syslog_lines = source_file.read().split('\n')

    sysrad = SysRador(path_to_conf)
    for line in syslog_lines:
        sysrad.send(line)
