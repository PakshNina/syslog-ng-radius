[Русская документация](README_RUS.md)

# Python script syslog-ng-radius
The script routes login events from syslog-ng server to FSSO Radius server for accounting.

## Script details
1. Syslog-ng Server gets login events from different sources.
Server filters logs with "Authentication succeeded" message, and then routes it either to the python script or to the test.log file.
Whole Message Line looks like:
```
Nov 26 15:54:41 127.0.0.1 1 2019-11-26T15:54:41.272535+00:00 ubu-srv-nfs root - - [timeQuality tzKnown="1" isSynced="1" syncAccuracy="213000"] Passed-Authentication: Authentication succeeded, User-Name=d.beckham@fortidomain.local, Calling-Station-ID=10.0.0.2
```
2. Python script gets log (from test.log or from stdin line) and parses it.
It uses attributes from initial.conf file:
'User-Name' from Message Line replaced with 'User-Name' (Radius attribute, just in case it could be changes to the other attribute).
'Calling-Station-ID' replaced with 'Framed-IP-Address'
Also to the Radius packet added constant attribute 'Acct-Status-Type' with value 'Start'.
3. Script parses 'User-Name' value.
If 'User-Name' without domain name - domain name added.
If 'User-Name' looks like 'testdomain.local\user1', script sends it without adjustment.
If 'User-Name' looks like e-mail "user@testdomain.local", script sends to LDAP server.
LDAP server checks if it is an UPN (userPrincipalName), if not, LDAP looks for such email and returns userPrincipalName (if not None).
4. At the end with all verified attributes script creates Radius packet and sends it to Radius server.
If server replies with 'pyrad.packet.AccountingResponse' - success!


## Files and directories description
- /dicts - standard radius dictionaries
- /fortigator - python package
- /schemes - script work schemes
- initial.conf - configurator file, that sets script settings (ldap, radius, logging)
- syslog_sysrador_program.py - python script for Syslog-ng login events handling (runs from syslog-ng destination settings)
- terminal_sysrador_program.py - script for linux console execution
- user_creator_multiproc.py - script for user login events generating (starting from User00001 and 10.0.0.1 to setted value)
- user_creator_real_data.py - script that generates real users (from written inside list of users)


# Project structure
## Fortigator package has following modules:
- attributor.py - module that forms attributes based on initial.conf settings and text line
- domainator.py - using regular expressions checks out if the user name is in particular format. If user name is "domain.com\user", then attributes sends to radius without modification. If user has simple "user" format, then к domain is added "@domain.com". If login is "user@doman.com" alike, then it is send to ldap server, to check if it is an mail. If so, ldap client requests proper userPrincipalName.
- ldaper.py - ldap client to connect with AD (ldap) server
- rador.py - Radius client
- sysrador.py - module with final logic

## Principal simple work scheme
![scheme small](http://ninucium.ru/random_files/algorythm_scheme_small.png)

## principal sysrador module scheme
![scheme big](http://ninucium.ru/random_files/algorythm_scheme_big.png)

# Used libraries
For linux:

```build-essential python3-dev libldap2-dev libsasl2-dev ldap-utils valgrind
```
for python:
```
python3 -m pip install python-ldap pyrad configparser
```

## System preparation
### Make sure that you have python v3 installed (from 3.6)
```
python3 –V
```

### Install pip utils for python3:
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
apt install build-essential python3-dev libldap2-dev libsasl2-dev ldap-utils valgrind
```

## Python modules installation and script configuration

### Install python3 modules
```
python3 -m pip install python-ldap pyrad configparser
```

### Clone with git or download script:
https://github.com/PakshNina/syslog-ng-radius

### Go to the downloaded dir.
Open script's configuration file `initial.conf`:
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

#### Set up absolute path to result log file
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

### Open syslog_sysrador_program.py in editor:
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
#### For users with alternative domain notation:
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
# destination(d_python);
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
