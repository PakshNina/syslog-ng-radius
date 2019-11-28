# -*- coding: utf-8 -*-

"""Script run syslog-ng."""

import os
import sys
from fortigator.sysrador import SysRador


if __name__ == '__main__':
    path_to_file = os.path.join('/home/python-radius/initial.conf')  # Absolute path!
    sysrad = SysRador(path_to_file)
    try:
        line = sys.stdin.readline()
        sysrad.send(line)
    except Exception as err:
        raise Exception('Could not read line: {0}'.format(err))
    
