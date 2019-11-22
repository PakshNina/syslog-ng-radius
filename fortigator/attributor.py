# -*- coding: utf-8 -*-

"""Module that creates attributes from radius from input text line."""

import re
import sys
import configparser

# Turning off Traceback information.
sys.tracebacklimit = 0
# Error template.
ERROR_TEMPLATE = 'Error has been occured in {0} with error {1} on line {2}'


class AttributorException(Exception):
    """Exception class for Atruibutor class."""

    def __init__(self, name, err, line):
        """Reinit AttributorException class message."""
        super().__init__(self, ERROR_TEMPLATE.format(name, err, line))


class Attributor(object):
    """Creates attributes from text line."""

    def __init__(self, config, logger):
        """Init Attributor key in dictionaries."""
        self.logging = logger
        try:
            self.alies_input_dict = config['ALIES']
            self.additional_input_dict = config['ADDITIONAL FIELDS']
        except Exception as err:
            _, _, exc_tb = sys.exc_info()
            raise AttributorException(self, err, exc_tb.tb_lineno)

        self.alies_dict = {}
        self.additional_dict = {}

        for indx in self.alies_input_dict:
            # Creating dict for radius attribute
            self.alies_dict[indx] = self.alies_input_dict[indx]

        for field in self.additional_input_dict:
            # Creating dict for additional attributes.
            # Somehow, attributes are gotten in lower case,
            # so making it with capital letters again.
            field = field.split('-')
            field = [word.capitalize() for word in field]
            field = '-'.join(field)
            self.additional_dict[field] = self.additional_input_dict[field]

    def __repr__(self):
        """Object representaion."""
        return 'Attributor class'

    def create_attributes(self, text_line):
        """Create result dict with attributes and values to send."""
        self.result_dict = {}
        self._search(text_line)
        if self.result_dict:
            if 'User-Name' in self.result_dict:
                return self.result_dict
        self.logging.error(ERROR_TEMPLATE.format(self.result_dict, text_line, 'User-Name'))

    def _search(self, text_line):
        """Adding elements to."""
        text_array = ((text_line.lower()).strip(' ')).split(',')
        self._add_alies(text_array)
        self._add_field()

    def _add_alies(self, text_array):
        """Добавления в общий словарь атрибутов."""
        for key in self.alies_dict:
            for line in text_array:
                if re.search(key, line):
                    line = line.split('=')
                    self.result_dict[self.alies_dict[key]] = line[1]
                    break

    def _add_field(self):
        """Добавление в общий словарь дополнительных параметров."""
        for key in self.additional_dict:
            self.result_dict[key] = self.additional_dict[key]


if __name__ == '__main__':

    conf = configparser.ConfigParser()
    conf.read('../initial.conf')
    text_line = """Oct 25 18:20:46 10.31.34.101 CISE_Passed_Authentications
0000000008 1 0 2019-10-25 18:20:46.236 +03:00 0000108067 5200 NOTICE
Passed-Authentication: Authentication succeeded, ConfigVersionId=174,
Device IP Address=10.31.34.225, DestinationIPAddress=10.31.34.101,
DestinationPort=1812, UserName=f5_auditor, Protocol=Radius,
RequestLatency=114, NetworkDeviceName=F5_14.1, User-Name=f5_auditor,
NAS-IP-Address=10.31.33.223,
NAS-Port=8470, Service-Type=Authenticate Only,
Calling-Station-ID=10.31.253.42,
NAS-Identifier=httpd, NAS-Port-Type=Virtual, OriginalUserName=f5_auditor,
NetworkDeviceProfileName=Cisco,
NetworkDeviceProfileId=b0699505-3150-4215-a80e-6753d45bf56c,
IsThirdPartyDeviceFlow=false, AcsSessionID=ise/358616094/16,
AuthenticationIdentityStore=Internal Users,
AuthenticationMethod=PAP_ASCII, SelectedAccessService=F5 Auth Proto,
SelectedAuthorizationProfiles=F5 RO, IdentityGroup=User
Identity Groups:Employee, Step=11001, Step=11017, Step=11117,
Step=15049, Step=15008, Step=15048, Step=15041, Step=15013,
Step=24210, Step=24212, Step=22037, Step=24715, Step=15036,
Step=15016, Step=22081, Step=22080, Step=11002,
SelectedAuthenticationIdentityStores=Internal Users,
AuthenticationStatus=AuthenticationPassed, NetworkDeviceGroups=IPSEC#Is
IPSEC Device#No, NetworkDeviceGroups=Location#All
Locations, NetworkDeviceGroups=Device Type#All
Device Types, IdentityPolicyMatchedRule=Default,
AuthorizationPolicyMatchedRule=Authorization Rule 1,
UserType=User, CPMSessionID=0a1f2265OTErVOEMx
7g1H4zTivXBrUeDcFn191e4o5xkg30FzSw,
PostureAssessmentStatus=NotApplicable, ISEPolicySetName=F5 Auth,
IdentitySelectionMatchedRule=Default, StepData=5= Network
Access.NetworkDeviceName, StepData=7=Internal Users,
DTLSSupport=Unknown, Network Device Profile=Cisco,
Location=Location#All Locations, Device Type=Device
Type#All Device Types, IPSEC=IPSEC#Is IPSEC Device#No,
Name=User Identity Groups:Employee, EnableFlag=Enabled,
Response={Class=CACS:0a1f2265OTErVOEMx7g1H4zTi
vXBrUeDcFn191e4o5xkg30FzSw:ise/358616094/16;
F5-LTM-User-Info-1=RO; F5-LTM-User-Role=80; }"""
    text_line = text_line.strip('\n')
    attr = Attributor(conf)
    attr_dict = attr.create_attributes(text_line)
    print(attr_dict)
