import sys
sys.path.append(r'/usr/local/lib/python3.7/site-packages')
sys.path.append('/root/guangxi_test/1/con_log')
from qqwry import QQwry
from IPy import IP
import socket
import threading
import csv
import time
from con_log import logger_rule
import eventlet
eventlet.monkey_patch()
q = QQwry()
q.load_file('qqwry.dat')

def shanghai(batch_list):
    """
    输入：ip list
    输出：ip 归属地写入的csv文件
    :param batch_list:
    :return:
    """
    with open("上海_ip.csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        #writer.writerow(["country", "serve",  "ip"])
        #ip_list = f.read().splitlines()
        for ip in batch_list:
            address =[]
            try:
                with eventlet.Timeout(1, False):
                    #ip = socket.gethostbyname(url)
                    address = list(q.lookup(ip))
                address.append(ip)
                writer.writerow(address)
                print('{} success'.format(ip))
                logger_rule.info('{} success'.format(ip))
            except Exception as e:
                print('{}  ip fail,{}'.format(ip, e))
                logger_rule.error('{}  ip fail,{}'.format(ip, e))
                pass

# def shanghai():
#     """
#     单线程
#     输入：ip list
#     输出：ip 归属地写入的csv文件
#     :param batch_list:
#     :return:
#     """
#     with open("上海_ip.csv", "a") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["country", "serve",  "ip"])
#         with open('ip_test.txt', "r", encoding='ISO-8859-1') as f:
#             batch_list = f.read().splitlines()
#             #ip_list = f.read().splitlines()
#             for ip in batch_list:
#                 address =[]
#                 try:
#                     with eventlet.Timeout(1, False):
#                         #ip = socket.gethostbyname(url)
#                         address = list(q.lookup(ip))
#                     address.append(ip)
#                     writer.writerow(address)
#                     print('{} success'.format(ip))
#                     logger_rule.info('{} success'.format(ip))
#                 except Exception as e:
#                     print('{}  ip fail,{}'.format(ip, e))
#                     logger_rule.error('{}  ip fail,{}'.format(ip, e))
#                     pass

def threads_clm(thread_num):
    with open('NEW_OVERSEA_IP_RESULT.txt', "r", encoding='ISO-8859-1') as f:
        urls = f.read().split()
    per_num = int(len(urls) / thread_num)
    threads = []
    for i in range(thread_num):
        t = threading.Thread(target=shanghai, args=(urls[i*per_num:i*per_num+per_num],))
        threads.append(t)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    threads_clm(32)
