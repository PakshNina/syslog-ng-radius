[Ссылка на русскую документацию](README_RUS.md)

# Python script to route login events from Syslog-ng server to Fortinet Single Sign On Agent
The script is used for routing login events from syslog-ng server to FSSO radius server for user accounting purposes.

## Files and directories description
- /dicts - standart radius dictionaries
- /fortigator - python modules
- /schemes - script work schemes
- initial.conf - configurator file, that sets up python script (ldap, radius, logging)
- syslog_sysrador_program.py - python script for syslog-ng login events handling (runs from syslog-ng destination settings)
- terminal_sysrador_program.py - script for linux console execution
- user_creator_multiproc.py - script for user login events generating (starting from User00001 and 10.0.0.1 to setted value)
- user_creator_real_data.py - script, that generates real users (from written inside list of users)

## System preconfiguration
### Make sure that you have python v3 installed (from 3.6)
```
python3 –V
```

### Install pip util for python3:
```
apt install python3-pip
```

#### If you have problems with pip installation ‘Unable to locate package python-pip’, add tag `universe` at the end of the each `sources.list` entry:
```
deb http://archive.ubuntu.com/ubuntu bionic-security main universe 
deb http://archive.ubuntu.com/ubuntu bionic-updates main universe
deb http://archive.ubuntu.com/ubuntu bionic main universe
```

#### Update OS packets:
```
apt update
```

#### Install pip:
```
apt install python3-pip
```

### Install ldap library packages:
```
apt install build-essential python3-dev libldap2-dev libsasl2-dev slapd ldap-utils valgrind
```

## Python modules installatiion and script configuration

### Install python3 modules
```
pip install python-ldap pyrad configparser
```

### Clone with git or download script:
https://github.com/PakshNina/syslog-ng-radius

### Go to the downloaded dir.
Open script's configguration file `initial.conf`:
```
nano initial.conf
```
#### Leave these options without changes
```
[ALIES]
User-Name=User-Name
Calling-Station-ID=Framed-IP-Address
[ADDITIONAL FIELDS]
Acct-Status-Type=Start
```

#### Add radius server informationL IP, secret key, absolute path to Radius dictionaries:
```
[RADIUS]
IP = 10.0.0.1
SECRET = P@ssw0rd
DICT_PATH = /home/python-radius/dicts/dictionary
```

#### Set up abolute path to result log file
```
[RESULT_LOG]
LOG_PATH = /var/log/syslog-python.log
```

#### Do not change that part
```
[TARGET_ATTR]
ATTR = User-Name
```
#### Set up ldap server settings: IP-address, login, password. Keep out without changes LDAP_ATTR.
Change LDAP_OU Organizational Unit and domain name LDAP_DOMAIN:
```
[LDAP]
LDAP_URL = ldap://10.0.0.2:389
LDAP_USERNAME = administrator@testdomain.local
LDAP_PSWD = P@ssw0rd
LDAP_ATTR = userPrincipalName
LDAP_OU = HQ
LDAP_DOMAIN = testdomain.local
```

## Running script from syslog-ng

### Change syslog-ng configuration:
```
nano /etc/syslog-ng/syslog-ng.conf
```
Full config:
```
source s_net { udp(ip(0.0.0.0) port(514)); };
filter f_ise_host     {    (
                                host("10.0.0.10") or
                                host("127.0.0.1")
                                );
                        };
filter f_ise_auth { message("Authentication succeeded"); };
destination d_NS_ISE { file("/var/log/test.log"); };
destination d_python { program("python3 -u /home/python-radius/syslog_sysrador_program.py"
        flags(no_multi_line)
        flush_timeout(1000)
); };

log {   source(s_net);
        filter(f_ise_host);
        filter(f_ise_auth);
        destination(d_NS_ISE);
        destination(d_python);
};
```
Instead of path /var/log/test.log – use path to your syslog-ng events destination. Instead of /home/python-radius/syslog_sysrador_program.py – use absolute path to python syslog_sysrador_program.py script.

### Open syslog_sysrador_program.py in redactor:
```
nano syslog_sysrador_program.py
```
On line `sysrad = SysRador('/home/python-radius/initial.conf')` change `/home/python-radius/initial.conf` to absolute file to initial.conf file:

```
from fortigator.sysrador import SysRador
import sys

if __name__ =='__main__':
    sysrad = SysRador('/home/python-radius/initial.conf')
    try:
        line = sys.stdin.readline()
        sysrad.send(line)
    except Exception as err:
        raise Exception('Problem occured: {0}'.format(err))
```

### Generating login events from console

#### For users without domain name:
```
logger -n 127.0.0.1 Passed-Authentication: Authentication succeeded, User-Name=surfservice, Calling-Station-ID=10.0.0.1
```
#### For users with userPrincipalName (UDN):
```
logger -n 127.0.0.1 Passed-Authentication: Authentication succeeded, User-Name=cpservice@fortidomain.local, Calling-Station-ID=10.0.0.2
```
#### For users with mail instead of UDN:
```
logger -n 127.0.0.1 Passed-Authentication: Authentication succeeded, User-Name=figoluis@fortidomain.local, Calling-Station-ID=10.0.0.3
```
#### For users with alternativy domain notation:
```
logger -n 127.0.0.1 Passed-Authentication: Authentication succeeded, User-Name=fortidomain.local\\r.carlos, Calling-Station-ID=10.0.0.4
```
### Check result

## Running script from console

### Clear syslog-ng destination log:
```
rm /var/log/test.log
```

### Comment python destination line in syslog-ng configuration:
```
#        destination(d_python);
```
### Go to dir with scripts (syslog-ng-radius) and run user login events regerator. After –n type in numbers of generated users:
```
python3 user_creator_multiproc.py -n 400
```
### Run terminal script:
```
python3 terminal_sysrador_program.py
```

### Check out the results:
```
tail -f /var/log/syslog-python.log
```


# Project structure
## Fortigator package has following modules:
- attributor.py - module that forms attributes based on initial.conf settings and text line
- domainator.py - using regular expressions cheack out if the user name is in particular format. If user name is "domain.com\user", then attributes sends to radius without modification. If user has simple "user" format, then к domain is added "@domain.com". If login is "user@doman.com" alike, then it is send to ldap server, to check if it is an mail. And if so, ldap client requests proper userPrincipalName.
- ldaper.py - ldap client to connect with AD (ldap) server
- rador.py - Radius client
- sysrador.py - module with final logic

## Principal simple work scheme
![scheme small](http://ninucium.ru/random_files/algorythm_scheme_small.png)

## principal sysrador module scheme
![scheme big](http://ninucium.ru/random_files/algorythm_scheme_big.png)