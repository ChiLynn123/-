#-*- coding : utf-8 -*-
import pandas as pd
import os
import sys
# sys.path.append(r'/root/csv')
# sys.path.append(r'/root/guangxi_test/con_log')
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


def read_path(filePath):
    """
    读取改路径下的所有子文件 list
    """
    # filePath = 'F:/csv_he'
    allxls=os.listdir(filePath)
    allxlss = []
    for i in allxls:
        j = f'{filePath}/{i}'  #('F:/csv_he/'+i)
        allxlss.append(j)
    return allxlss


def batch_query_and_print(path):
    """
    打开txt文件夹，get ip 并将结果写入CSV
    """
    with open(path+".csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["country", "serve", "url", "ip"])
        with open(path+".txt") as f:
            url_list = f.read().splitlines()
            for url in url_list:
                try:
                    with eventlet.Timeout(1, False):
                        ip = socket.gethostbyname(url)
                except Exception as e:
                    pass
                else:
                    address = list(q.lookup(ip))
                    address.append(url)
                    address.append(ip)
                    writer.writerow(address)
                    logger_rule.info('{}  ip success'.format(url))


def batch_query(batch_list):
    """
    参数为一个list，32个线程
    输出为32线程的结果
    :param batch_list:
    :return:
    """
    threads = []
    for batch in batch_list:
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
    batch_query(list1)
    batch_query(list2)


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


def shanghai():
    """
    单线程
    输入：ip list
    输出：ip 归属地写入的csv文件
    :param batch_list:
    :return:
    """
    with open("上海_ip.csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["country", "serve",  "ip"])
        with open('ip_test.txt', "r", encoding='ISO-8859-1') as f:
            batch_list = f.read().splitlines()
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


def threads_clm11(thread_num):
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


data = pd.DataFrame(columns=['country', 'serve', 'url', 'ip'])
for i in allxlss:
    df = pd.read_csv(i, encoding='utf8')
    df = df.dropna()
    print('{} count is {}'.format(i, df.shape))
    data = data.append(df)   #合并
print('data count is {}'.format(data.shape))
#去重
data = data.drop_duplicates(['url'])
print('data drop_duplicates count is {}'.format(data.shape))
#保存
data.to_csv('F:/data_sum.csv', encoding='utf-8')