# -*- coding: utf-8 -*-
# 安装 pip install qqwry-py3
import sys
from qqwry import QQwry
from IPy import IP
import socket
import threading
import csv
import re
import time
#from con_log import logger_rule
#import eventlet
from urllib.parse import urlparse
#eventlet.monkey_patch()
q = QQwry()
q.load_file('D:/work_data/四期/ip境内外区分/qqwry.dat')

china_1 = ["中国","北京","天津","上海","重庆","河北","山西","内蒙古","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","广西","海南","四川","贵州","云南","陕西","甘肃","青海","西藏","宁夏","新疆"]
china_2 = ["香港","澳门","台湾",]
combined1 = "(" + ")|(".join(china_1) + ")"
combined2 = "(" + ")|(".join(china_2) + ")"

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
                        print('{} success'.format(ip))
                except Exception as e:
                    print('{}  ip fail,{}'.format(ip, e))
                address.append(ip)
                address.append(url)
                writer.writerow(address)

def ipip():
    file = 'C:/Users/FH/Desktop/无标题2hao.csv'  # 输入文件加密的
    save_file = 'C:/Users/FH/Desktop/2号_jiemi111.csv'  # 输出结果文件，解密的
    with open(file, encoding='utf-8') as f:
        with open(save_file, 'w', encoding='utf-8') as save_f:
            csv_read = csv.reader(f)
            writer = csv.writer(save_f)
            for line in csv_read:
                label = line[0]
                cur_ulr = line[1]
                title = line[2]
                lines = [label, cur_ulr, title]
                print(cur_url)
                if url.startswith("http"):
                    url = urlparse(url).netloc
                try:
                    ip = socket.gethostbyname(url)
                    address = list(q.lookup(ip))
                    print('{} success'.format(ip))
                except Exception as e:
                    print('{}  ip fail,{}'.format(ip, e))
                lines.append(ip)
                lines.append(url)
                writer.writerow(lines)


def test_add(txt_path):
    with open(f"{txt_path}_{time.strftime('%Y%m%d_%H%M%S')}.csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["country", "serve", "China", "ip", "url"])
        with open(txt_path, "r", encoding='ISO-8859-1') as f:
            batch_list = f.read().splitlines()
            for url in batch_list:
                address = []
                ip = ''
                if url.startswith("http"):
                    url = urlparse(url).netloc
                try:
                    ip = socket.gethostbyname(url)
                    address = list(q.lookup(ip))
                except Exception as e:
                    print('{}  ip fail,{}'.format(url, e))
                else:
                    flag='境外'
                    if re.match(combined2, address[0]):
                        flag = f"境内-{address[0]}"
                    elif re.match(combined1, address[0]):
                        flag = "境内"
                    address.append(flag)
                    address.append(ip)
                    address.append(url)
                    writer.writerow(address)
                    print('{} ip success:{}'.format(url, address))


china_1 = ["中国", "北京", "天津", "上海", "重庆", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", "江苏", "浙江", "安徽", "福建", "江西", "山东",
               "河南", "湖北", "湖南", "广东", "广西", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "西藏", "宁夏", "新疆"]
china_2 = ["香港", "澳门", "台湾", ]
combined1 = "(" + ")|(".join(china_1) + ")"
combined2 = "(" + ")|(".join(china_2) + ")"

# 根据ip归属地判断是否属于境内外，香港澳门台湾单独标记
def ip_area(ip_address):
    """
    Args:
        ip_address: list类型的address:['address','server']
    Returns:
        '境内'/'境外'，其中'香港澳门台湾'标记
    """
    area = '未知'
    if ip_address[0]:
        area = '境外'
        if re.match(combined2, ip_address[0]):
            area = f"境内-{ip_address[0]}"
        elif re.match(combined1, ip_address[0]):
            area = "境内"
    return area


# 输入字段的合法性检查（ip、带不带http头的url，有端口号的会先提取域名再判断是否合法）
def valid_2(word):
    """
    判断输入是否合法,若合法返回 域名 或者 IP(不带端口的)
    :param word:
    :return:若合法，输出url的域名或者ip  [netloc,ip]
    """
    if word.startswith("http"):
        netloc = urlparse(word).netloc
    else:
        url = f"http://{word}"
        netloc = urlparse(url).netloc
    netl = netloc if len(netloc.split(':')) < 2 else netloc.split(':')[0]
    pattern = re.compile(r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
                         r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
                         r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
                         r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$')
    if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", netl):
        return [None, netl]
    elif re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', netl):
        return [urlparse(netl).netloc, None]
    elif pattern.match(netl):
        return [netl, None]
    return [None, None]

def valid_2(word):
    """
    判断输入是否合法,若合法返回 域名 或者 IP(不带端口的)
    :param word:
    :return:若合法，输出true, 否则输出false
    """
    if word.startswith("http"):
        netloc = urlparse(word).netloc
    else:
        url = f"http://{word}"
        netloc = urlparse(url).netloc
    netl = netloc if len(netloc.split(':')) < 2 else netloc.split(':')[0]  #不加端口
    pattern = re.compile(r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
                         r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
                         r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
                         r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$')
    if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", netl):
        return True
    elif pattern.match(netl):
        return True
    return False


def dahu():
    xxxx='Gene_id=XLOC_003495;Gene_name=linc-DTHD1-11;Transcript_id=TCONS_00008774;Transcript_name=linc-DTHD1-11;'
    xxx = 'gene_id ENSG00000266904.1; transcript_id ENST00000589910.1; gene_type lincRNA; gene_status NOVEL; gene_name LINC00663; transcript_type lincRNA; transcript_status KNOWN; transcript_name LINC00663-004; level 2; havana_gene OTTHUMG00000182363.1; havana_transcript OTTHUMT00000460779.1;'
    pattern = re.compile('gene_name.+?;', re.I)   #匹配从ab开始，到ef结束的内容
    result = pattern.findall(xxx)
    reee = re.search(r'[g|G]ene_name.+?;', xxxx, flags=0, )
    reee2 = re.search(r'[g|G]ene_name.+?;', xxx, flags=0, )
    print(reee.group()[:-1])
    print(reee2.group()[:-1])




if __name__ == "__main__":
    #test_add('D:/work_data/四期/ip境内外区分/url.txt')
    #threads_clm(int(sys.argv[1]), sys.argv[2])
    # add=[['江苏省淮安市', '联通'],['美国', ' CZ88.NET'],['', ' CZ88.NET']]
    # for i in add:
    #     print(ip_area(i))
    # url_list = ["218.15.146.73:8081", "218.15.146.139:8000",
    #             "117.21.93.112:8081", "www.ycyun.vip:80", "120.238.91.169:8081", "218.15.144.184:8001",
    #             "root.mzdfwl.cn:8888", "123.129.217.41:8888", "103.237.103.240:8888", "121.37.212.171:8080",
    #             "101.35.133.75:8888", "8.134.119.26:8888", "211.99.98.79:8888", "mzv.uoscn.com:8088",
    #             "222.187.223.177:8888", "120.48.20.70:8080", "118.195.182.88:8888",'hfksjfh^^*&^(%~@','87r932798#@%$#%%^$^*%&.gcn']
    # for url in url_list:
    #     val = valid_2(url)
    #     print('{} 的合法性检查：{}'.format(url, val))
    dahu()


