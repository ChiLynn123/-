import sys
sys.path.append(r'/home/clm/.local/lib/python3.6/site-packages')
sys.path.append(r'/usr/local/lib/python3.6/dist-packages')
import jieba
import re
from bs4 import BeautifulSoup
import threading
import pandas as pd
from datasketch import MinHash, MinHashLSH
from nltk import ngrams
import time
import os
import csv
csv.field_size_limit(sys.maxsize)

lsh = MinHashLSH(threshold=0.5, num_perm=128, storage_config={'type': 'redis', 'basename': b'0.5_pro',

                                                              'redis': {'host':'10.1.203.15', 'port':6379, 'db':13}})

# 分片
def task_split(deal_list, parts):
    pieces = len(deal_list) // parts
    if pieces == 0:
        return [[i] for i in deal_list]
    piece_list = list()
    for i in range(0, pieces * parts, pieces):
        piece_list.append(deal_list[i: i + pieces])
    for i in range(pieces * parts, len(deal_list)):
        piece_list[i % parts].append(deal_list[i])
    return piece_list


# 去标点符号
def fuhao(sentence):
    remove_chars = '[·’!"\#$%&\'()＃！（）*+,-./:;<=>?\@，：?￥★、…．＞【】［］《》？“”‘’\[\\]^_`{|}~]+'
    sentenceClean = re.sub(remove_chars, "", sentence)
    return sentenceClean


# 从原始文本提取特征
def Extract_fea(html_origin):
    soup = BeautifulSoup(html_origin, 'lxml')
    mate_tag = ['keywords', 'Keywords', 'description', 'Description']
    mate_word = []
    try:
        title = [soup.title.text]
    except Exception as e:
        title = list()
    for i in mate_tag:
        try:
            sen = soup.find(attrs={"name": i})['content']
        except Exception as e:
            sen = ''
        mate_word.append(sen)
    title.extend(mate_word)
    result = ''.join(title)
    return fuhao(result)


# 原始文本预处理
def feature_csv(batch_list):
    """
    输入：list的字典 【{'id'：, 'origin': }，.....】
    输出：写入的csv文件
    :param batch_list:
    :return:
    """
    save_path = '/home/clm/clm_minhash/id_feature.csv'
    with open(save_path, "a") as csvfile:
        writer = csv.writer(csvfile)
        #writer.writerow(["country", "server",  "ip"])
        #ip_list = f.read().splitlines()
        for url in batch_list:
            id = url['html_content_id']
            feature = Extract_fea(url['html_origin_content'])
            if feature:
                res = [id, feature]
                #print('******{}******处理完成'.format(id))
                writer.writerow(res)
            else:
                pass



def threads_clm(thread_num, txt_path):
    """
    多线程
    :param thread_num:
    :return:
    """
    # 处理csv文件
    with open(txt_path, "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    #per_num = int(len(rows)/thread_num)
    piece = task_split(rows, thread_num)
    threads = []
    for i in piece:
        t = threading.Thread(target=feature_csv, args=(i, txt_path))
        threads.append(t)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()

# 查询
def da2mh(data):
    """
    输入要查询的字符串文本
    输出
    """
    minhash = MinHash(num_perm=128)
    for d in ngrams(data['sent'], 3):
        minhash.update("".join(d).encode('utf-8'))
    lsh.insert(data['key'], minhash)

def minhash_query(sent):
    minhash = MinHash(num_perm=128)
    for d in ngrams(sent, 3):
        minhash.update("".join(d).encode('utf-8'))
    res = lsh.query(minhash)
    print('minhash查询redis完成')
    return res

# 批量插入
def insert(mlist):
    """
    mlist:[(key, minhash),(),]
    """
    with lsh.insertion_session() as session:
        for i in mlist:
            try:
                session.insert(i['key'], i['mh'])
            except:
                print('已存在')
                pass
# 处理每一片的原始文本生成feature, 并写入另一个csv文件中

# 分片处理csv文件
def read_csv(file1, chunk_size=500):
    chunk = []
    time_start = time.time()
    with open(file1, "r", newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        cnt = 0
        fieldnames = ["html_content_id", "html_origin_content"]
        for row in csvreader:
            if row[0] == "html_content_id":
                continue
            try:
                # {’html_content_id‘: , 'html_origin_content': }
                tmpdict = {fieldnames[idx]: row[idx] for idx in range(len(fieldnames))}
                # id_ = row[0]
            except:
                continue
            chunk.append(tmpdict)
            cnt += 1
            if cnt == chunk_size:   # 满足一片的数量之后，开始处理
                cnt = 0
                # 处理获取feature
                a = time.time()
                feature_csv(chunk)
                b = time.time()
                print('500处理完成，耗时{}'.format(b-a))
                # response = smoke_test(chunk, port, debug)
                chunk = []
        # 剩下的最后一片，如果不能均分的话
        if chunk:
            feature_csv(chunk)
        end_time = time.time()
        print('********************')
        print('{}文件处理完成共耗时：{}'.format(file1, end_time-time_start))


# data = pd.read_csv('/home/clm/clm_minhash/100w.csv')
# print('读取成功，大小{}'.format(data.shape))
# data1 = data[data['url_title'].notna()]
# print('去空之后 {}'.format(data1.shape))
# data2 = data1.drop_duplicates(['url_title'])
# print('title 去重之后 {}'.format(data2.shape))
# data2.to_csv('/home/clm/clm_minhash/100w_drop.csv',index =None)


if __name__ == "__main__":
    # threads_clm(int(sys.argv[1]), sys.argv[2])

    file1 = '/home/cyh/需求汇总分析/hhc_crawler/result/'
    file_path = ['1.csv', '1-2.csv', '2-3.csv', '4-5.csv', '5-6.csv', '6-7.csv']
    for i in file_path:
        file = f'{file1}{i}'
        read_csv(file, chunk_size=500)

