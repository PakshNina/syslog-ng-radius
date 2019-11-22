from fortigator.sysrador import SysRador
import sys

if __name__ =='__main__':
    sysrad = SysRador('/home/python-radius/initial.conf')
    try:
        line = sys.stdin.readline()
        sysrad.send(line)
    except Exception as err:
        raise Exception('Problem occured: {0}'.format(err))

