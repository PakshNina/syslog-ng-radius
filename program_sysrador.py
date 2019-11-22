from fortigator.sysrador import SysRador


if __name__ == '__main__':
    sysrad = SysRador('initial.conf')
    sysrad.send()

