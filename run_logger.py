import os
import ipaddress
import argparse
import time


time1 = time.time()
USER = 'User000000'
IP = ipaddress.ip_address('10.0.0.0')

parser = argparse.ArgumentParser()
parser.add_argument('-n', dest='number', type=int, help='number of users to generate')
args = parser.parse_args()

if args.number:
    user_number = args.number
else:
    user_number = 400000

user_name = ''
user_ip = ''
for num in range(1, user_number+1):
    num_len = len(str(num))
    user_name = USER[0: len(USER) - num_len] + str(num)
    user_ip = IP + num
    command = 'logger -n 127.0.0.1 Passed-Authentication: Authentication succeeded, User-Name={0}, Calling-Station-ID={1}'.format(user_name, user_ip)
    try:
        os.system(command)
    except Exception as err:
        print(err)

time2 = time.time()
delta = time2-time1
print('Execution time = {}'.format(delta))

