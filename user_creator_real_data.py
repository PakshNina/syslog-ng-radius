# -*- coding: utf-8 -*-

"""Generate real user data."""

import ipaddress
import os

# List examples
name_list = ['surfservice',
r'fortidomain.local\\r.carlos',
r'fortidomain\\d.beckham',
'fgservice',
'l.figo@fortidomain.local', r'fortidomain\\z.zidan',
'cpservice@fortidomain.local',
'tmservice@fortidomain.local',
'f.smolov@fortidomain.local',
'i.akinfeev@fortidomain.local',
'j.klopp@fortidomain.local',
'f5_auditor@fortidomain.local']


def make_string(x, name_list):
    user_name = name_list[x]
    user_ip = ipaddress.ip_address('10.0.0.1') + x
    return 'logger -n 127.0.0.1 Passed-Authentication: Authentication succeeded, User-Name={0}, Calling-Station-ID={1}'.format(user_name, user_ip)


def create_log(name_list):
    commands = []
    for x in range(len(name_list)):
        os.system(make_string(x, name_list))


if __name__ == '__main__':
    if not  os.path.isfile('/var/log/test.log'):
        file = open('/var/log/test.log', 'w')
        file.close()
    create_log(name_list)


