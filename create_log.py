import ipaddress
import argparse
import os
import time
from multiprocessing import Pool

def create_log(num):
    USER = 'User000000'
    IP = ipaddress.ip_address('10.0.0.0')
    num_len = len(str(num))
    user_name = USER[0:len(USER) - num_len] + str(num)
    user_IP = IP + num
    command = 'logger -n 127.0.0.1 Passed-Authentication: Authentication succeeded, User-Name={0}, Calling-Station-ID={1}'.format(user_name, user_IP)
    try:
        os.system(command)
        if not num % 10:
            return 'Send {} messages to logger'.format(num)
    except Exception as err:
        return err


if __name__ == '__main__':
    time1 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', dest='number', type=int, help='number of users to generate')
    args = parser.parse_args()

    if args.number:
        user_number = args.number
    else:
        user_number = 101
    pool = Pool(processes=4)
    result = pool.map(create_log, range(1, user_number + 1))
    time2 = time.time()
    delta = time2 - time1
    print('Execution time = {}'.format(delta))

