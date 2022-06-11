import sys
#sys.path.append(r'/usr/local/lib/python3.7/site-packages')
sys.path.append('/home/ubuntu/ip_test/con_log')
from qqwry import QQwry
from IPy import IP
import socket
import threading
import csv
import time
from con_log import logger_rule
import eventlet
from urllib.parse import urlparse
eventlet.monkey_patch()
q = QQwry()
q.load_file('qqwry.dat')

def ip_222(batch_list, csv_path):
    """
    输入：ip list
    输出：ip 归属地写入的csv文件
    :param batch_list:
    :return:
    """
    with open(f"{csv_path}_{time.strftime('%Y%m%d_%H%M%S')}.csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        #writer.writerow(["country", "serve",  "ip"])
        #ip_list = f.read().splitlines()
        for url in batch_list:
            address =[]
            ip = ''
            if url.startswith("http"):
                url = urlparse(url).netloc
            try:
                with eventlet.Timeout(2, False):
                    ip = socket.gethostbyname(url)
                    address = list(q.lookup(ip))
            except Exception as e:
                logger_rule.error('{}  ip fail,{}'.format(ip, e))
                pass
            if ip:
                address.append(ip)
                address.append(url)
                writer.writerow(address)
                logger_rule.info('{} success'.format(ip))
            else:
                logger_rule.error('{}  ip time out'.format(ip))

def threads_clm(thread_num, txt_path):
    """
    多线程
    :param thread_num:
    :return:
    """
    with open(txt_path, "r", encoding='ISO-8859-1') as f:
        urls = f.read().split()
    per_num = int(len(urls)/thread_num)
    threads = []
    for i in range(thread_num):
        t = threading.Thread(target=shanghai, args=(urls[i*per_num:i*per_num+per_num],txt_path))
        threads.append(t)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()

def ip_111(txt_path):
    """
    单线程
    输入：ip list
    输出：ip 归属地写入的csv文件
    :param batch_list:
    :return:
    """
    with open(f"{txt_path}_{time.strftime('%Y%m%d_%H%M%S')}.csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["country", "serve",  "ip", "url"])
        with open(txt_path, "r", encoding='ISO-8859-1') as f:
            batch_list = f.read().splitlines()
            #ip_list = f.read().splitlines()
            for url in batch_list:
                address = []
                ip = ''
                if url.startswith("http"):
                    url = urlparse(url).netloc
                try:
                    with eventlet.Timeout(2, False):
                        ip = socket.gethostbyname(url)
                        address = list(q.lookup(ip))
                        logger_rule.info('{} success'.format(ip))
                except Exception as e:
                    logger_rule.error('{}  ip fail,{}'.format(ip, e))
                address.append(ip)
                address.append(url)
                writer.writerow(address)
                # if ip:
                #     address.append(ip)
                #     address.append(url)
                #     writer.writerow(address)
                #     logger_rule.info('{} success'.format(ip))
                # else:
                #     logger_rule.error('{}  ip time out'.format(ip))

if __name__ == "__main__":
    ip_111(sys.argv[1])
    #threads_clm(int(sys.argv[1]), sys.argv[2])
