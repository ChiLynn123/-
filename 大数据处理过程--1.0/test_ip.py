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

def batch_query_and_print(path):
    with open(path+".csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["country", "serve", "url", "ip"])
        with open(path+".txt") as f:
            url_list = f.read().splitlines()
            for url in url_list:
                ip =''
                address =[]
                try:
                    with eventlet.Timeout(1, False):
                        ip = socket.gethostbyname(url)
                        address = list(q.lookup(ip))
                    address.append(url)
                    address.append(ip)
                    writer.writerow(address)
                    logger_rule.info('{}  ip success'.format(url))
                except Exception as e:
                    #logger_rule.error()
                    #print('{}  ip fail,{}'.format(url, e))
                    pass

                #logger_rule.info()

def batch_query(batch_list):
    """
    参数为一个list，32个线程
    输出为32线程的结果
    :param batch_list:
    :return:
    """
    threads = []
    for batch in batch_list:
        logger_rule.info('********************')
        logger_rule.info('{} pian '.format(batch))
        t = threading.Thread(target=batch_query_and_print, args=(batch,))
        threads.append(t)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()

def threads_clm(thread_num):
    per_num = int(128/thread_num)
    for i in range(per_num):
        batch_list = []
        for j in range(thread_num):
            batch_list.append(str(32*i+(j+1)))
        a = time.time()
        batch_query(batch_list)
        #第几片成功
        logger_rule.info('{}  batch is  success'.format(i))
        b = time.time()
        print('shijain:***********{}**********'.format((b - a)))
    list1=['129','130','1154', '1155', '1156', '1157', '1158', '1159', '1160', '1161', '1162', '1163', '1164', '1165', '1166', '1167', '1168', '1169', '1170', '1171', '1172', '1173', '1174', '1175', '1176', '1177', '1178']
    list2=['1179', '1180', '1181', '1182', '1183', '1184', '1185', '1186', '1187', '1188', '1189', '1190', '1191', '1192', '1193', '1194', '1195', '1196', '1197', '1198','1199']
    logger_rule.info('&&&&&&&&&&&&&&&&&&&&')
    batch_query(list1)
    logger_rule.info('#########################')
    batch_query(list2)

if __name__ == "__main__":
    threads_clm(32)
