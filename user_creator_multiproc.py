# -*- coding: utf-8 -*-

"""Create multiple users."""

import ipaddress
import argparse
import os
import time
from multiprocessing import Pool


def create_log(num):
    """Create and run command."""
    user = 'User000000'
    ip = ipaddress.ip_address('10.0.0.0')
    num_len = len(str(num))
    user_name = user[0:len(user) - num_len] + str(num)
    user_ip = ip + num
    command = 'logger -n 127.0.0.1 Passed-Authentication: \
        Authentication succeeded, User-Name={0}, \
        Calling-Station-ID={1}'.format(user_name, user_ip)

    try:
        os.system(command)  # Not secure!
    except Exception as err:
        raise Exception('Problem with running command: {0}'.format(err))

    if not num % 10:
        return 'Send {0} messages to logger'.format(num)


if __name__ == '__main__':
    time1 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n',
        dest='number',
        type=int,
        help='number of users to generate',
    )
    args = parser.parse_args()

    if args.number:
        user_number = args.number
    else:
        user_number = 101
    pool = Pool(processes=4)
    pool.map(create_log, range(1, user_number + 1))
    time2 = time.time()
    delta = time2 - time1
    print('Execution time = {0}'.format(delta))
