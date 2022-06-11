#-*- coding : utf-8 -*-
import pandas as pd
import os
import sys
# sys.path.append(r'/root/csv')
# sys.path.append(r'/root/guangxi_test/con_log')

def path_list(filepath):
    """
    输入文件路径
    输出此路径下的所有的子文件的完整路径名称list
    """
    all_path = os.listdir(filepath)
    com_path=list()
    for i in all_path:
        j = f'{filepath}/{i}'  # ('F:/csv_he/'+i)
        com_path.append()
    return com_path
    

def Data_pro(path):
    """
    读取此路径的所有文件内容 并拼接为一个完成csv文件保存到指定路径
    """
    data = pd.DataFrame(columns=['country', 'serve', 'url', 'ip'])
    for i in path:
        df = pd.read_csv(i, encoding='utf8')
        df = df.dropna()   # 去除空值
        print('{} count is {}'.format(i, df.shape))
        data = data.append(df)   #合并
    print('data count is {}'.format(data.shape))
    #去重
    data = data.drop_duplicates(['url'])
    print('data drop_duplicates count is {}'.format(data.shape))
    #保存
    data.to_csv('F:/data_sum.csv', encoding='utf-8')
    




