# -*- coding: utf-8 -*-

r"""Module that checks username and domain structure.

If username is styled like 'domain\user' of 'domain/user'
then it is legitimate.
If domain like 'user@domain.local' then ldap checks if i's userPrincipalName.
Otherwise it checks if it is e-mail and if so returns userPrincipalName.
If username doesn't have domain, then moduls adds it.
And if none is applied - it wouldn't be send.
"""

import re
import sys
from fortigator.ldaper import Ldaper
import configparser

LDAP = 'LDAP'
USER_NAME = 'User-Name'

# Turning off Traceback information.
sys.tracebacklimit = 0
# Error template.
ERROR_TEMPLATE = 'Error has been occured in {0} with error {1} on line {2}'


class Domainator(object):
    """Checks User-Name: if it's legimate UserPrincipalName."""

    def __init__(self, needed_attribute, ldap_settings_tuple, logging):
        """Init object with target attribute (User-Name) and ldap settings."""
        self.needed_attribute = needed_attribute
        self.logging = logging
        self.domain = ldap_settings_tuple[3]
        self.ldap = Ldaper(
            ldap_settings_tuple[0],
            ldap_settings_tuple[1],
            ldap_settings_tuple[2],
            ldap_settings_tuple[3],
            ldap_settings_tuple[4],
            self.logging,
        )

    def get_attributes(self, attributes_input_dict):
        """Form final attribute dict.

        _check_name() checks domain style.
        """
        self.attributes_input_dict = attributes_input_dict
        return self._check_name()

    def _check_name(self):
        # Check if the name-attribute is right
        good_domain = r'[a-zA-Z0-9._-]+\[a-zA-Z0-9._-]+'
        suspect_domain = '[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+[.]?[a-zA-Z0-9_.-]+'
        no_domain = '[a-zA-Z0-9._-]+'
        try:
            self.target_user = self.attributes_input_dict[
                self.needed_attribute
            ]
        except Exception as err:
            _, _, exc_tb = sys.exc_info()
            self.logging.error(
                ERROR_TEMPLATE.format(
                    self.attributes_input_dict,
                    self.target_user,
                    err,
                ),
            )

        if re.match(good_domain, self.target_user):
            return self.attributes_input_dict

        if re.match(suspect_domain, self.target_user):
            principal_user = self._check_ldap()
            if principal_user:
                self.attributes_input_dict[
                    self.needed_attribute
                ] = principal_user
                return self.attributes_input_dict

        if re.match(no_domain, self.target_user):
            self.attributes_input_dict[
                self.needed_attribute
            ] = '{0}@{1}'.format(
                self.target_user,
                self.domain,
            )
            return self.attributes_input_dict
        else:
            self.logging.error('Error in domainator in _check_name')

    def _check_ldap(self):
        return self.ldap.get_user_principal(self.target_user)


if __name__ == '__main__':
    dom = Domainator(USER_NAME)
    conf = configparser.ConfigParser()
    conf.read('../initial.conf')
    attr = dom.get_attributes({USER_NAME: 'r.carlos@fortidomain.local'}, conf)
    print(attr)
    attr = dom.get_attributes({USER_NAME: r'fortidomain\r.carlos'}, conf)
    print(attr)
    attr = dom.get_attributes({USER_NAME: 'fortidomain/r.carlos'}, conf)
    print(attr)
