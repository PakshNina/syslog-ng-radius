# -*- coding: utf-8 -*-

"""Generate real user data."""

import ipaddress
import os
import configparser

# List examples
name_list = [
    'surfservice',
    r'fortidomain.local\\r.carlos',
    r'fortidomain\\d.beckham',
    'fgservice',
    'l.figo@fortidomain.local',
    r'fortidomain\\z.zidan',
    'cpservice@fortidomain.local',
    'tmservice@fortidomain.local',
    'f.smolov@fortidomain.local',
    'i.akinfeev@fortidomain.local',
    'j.klopp@fortidomain.local',
    'f5_auditor@fortidomain.local',
]


def make_string(num, names):
    """Create command line."""
    user_name = names[num]
    user_ip = ipaddress.ip_address('10.0.0.1') + num
    return 'logger -n 127.0.0.1 Passed-Authentication: Authentication succeeded, User-Name={0}, Calling-Station-ID={1}'.format(user_name, user_ip)


def create_log(names):
    """Run command line."""
    for num in range(len(names)):
        os.system(make_string(num, names))  # Not secure!


def get_source_file(path_to_conf):
    """Get path to message source."""
    conf = configparser.ConfigParser()
    conf.read(path_to_conf)
    return conf['SOURCE_MESSAGE']['LOG_PATH']


if __name__ == '__main__':
    path_to_dir = os.getcwd()
    path_to_conf = os.path.join(path_to_dir, 'initial.conf')
    source_message = get_source_file(path_to_conf)
    if not os.path.isfile(source_message):
        with open(source_message, 'w'):
            pass
    create_log(name_list)
