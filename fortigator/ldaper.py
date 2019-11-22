# -*- coding: utf-8 -*-

"""Ldap client."""

import ldap
import configparser
import logging
import sys


# Turning off Traceback information.
sys.tracebacklimit = 0
# Error template.
ERROR_TEMPLATE = 'Error has been occured in {0} with error {1} on line {2}'


class LdaperException(Exception):
    """Exception class for Ldaper class."""

    def __init__(self, name, err, line):
        """Reinit LdaperException class message."""
        super().__init__(self, ERROR_TEMPLATE.format(name, err, line))


class Ldaper(object):
    """Ldaper client."""

    user_tag = 'userPrincipalName'
    mail_tag = 'mail'

    def __init__(self, url, user, psw, domain, ou, logger):
        """Init ldap client."""
        self.logging = logger
        self.ldap = ldap.initialize(url)
        self.ldap.simple_bind_s(user, psw)
        splited_domain = domain.split('.')
        self.basedn = 'ou={0}, dc={1}, dc={2}'.format(
            ou,
            splited_domain[0],
            splited_domain[1],
        )

    def get_user_principal(self, target_user, attr=user_tag):
        """Get userPrincipalName."""
        self.target_user = target_user
        self.attribute = attr.split(',')
        principal_user = self._check_if_principal()
        if principal_user:
            return principal_user

    def _check_if_principal(self):
        filtering = '(&(objectCategory=user)({0}={1}))'.format(
            Ldaper.user_tag,
            self.target_user,
            )
        final_user = self._make_request(filtering)
        if final_user:
            return self.target_user
        checked_user = self._check_if_email()
        if checked_user:
            return checked_user

    def _check_if_email(self):

        filtering = '(&(objectCategory=user)({0}={1}))'.format(
            Ldaper.mail_tag,
            self.target_user,
            )

        final_user = self._make_request(filtering)
        if final_user:
            try:
                for line in final_user:
                    for element in list(line):
                        if isinstance(element, dict):
                            return element[Ldaper.user_tag][0].decode()
            except Exception as err:
                _, _, exc_tb = sys.exc_info()
                self.logging.error(
                    ERROR_TEMPLATE.format(
                        self,
                        err,
                        exc_tb.tb_lineno,
                    ),
                )

    def _make_request(self, filtering):
        try:
            final_users = self.ldap.search_s(
                self.basedn,
                ldap.SCOPE_SUBTREE,
                filtering,
                self.attribute,
            )
        except Exception as err:
            _, _, exc_tb = sys.exc_info()
            self.logging.error(
                ERROR_TEMPLATE.format(
                    self,
                    err,
                    exc_tb.tb_lineno,
                ),
            )
            raise LdaperException(
                ERROR_TEMPLATE.format(
                    self,
                    err,
                    exc_tb.tb_lineno,
                ),
            )
        return final_users


if __name__ == '__main__':
    LDAP = 'LDAP'
    conf = configparser.ConfigParser()
    conf.read('../initial.conf')
    logging.basicConfig(
        filename='/var/log/syslog-python.log',
        format='%(asctime)s %(message)s',
    )
    conn = Ldaper(
        conf[LDAP]['LDAP_URL'],
        conf[LDAP]['LDAP_USERNAME'],
        conf[LDAP]['LDAP_PSWD'],
        conf[LDAP]['LDAP_DOMAIN'],
        conf[LDAP]['LDAP_OU'],
        logging,
    )
    principal_user = conn.get_user_principal('r.carlos@fortidomain.local')
    print(principal_user)
