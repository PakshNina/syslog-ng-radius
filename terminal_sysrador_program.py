from fortigator.sysrador import SysRador


if __name__ =='__main__':
    sysrad = SysRador('/home/python-radius/initial.conf')
    source_file = open('/var/log/test.log', 'r')
    syslog_lines = source_file.read().split('\n')
    source_file.close()
    for line in syslog_lines:
        sysrad.send(line)

