"""
pip install eml_parser
pip install langdetect
"""
import re
import csv
import os
from bs4 import BeautifulSoup
import eml_parser
from langdetect import detect
from langdetect import DetectorFactory
from translate import Translator   # 英汉翻译
DetectorFactory.seed = 0
keywords = ['@gjsyjfsg.com', '@hfisu.eu']

save_file = ''
file_dir =  ''


# 英语翻译中文
translator = Translator(to_lang="chinese")
translation = translator.translate("Do you believe")
print(translation)

# 中文翻译成英文
translator = Translator(from_lang="chinese",to_lang="english")
translation = translator.translate("开心快乐每一天！")
print (translation)

with open(save_file,'w',encoding='utf-8') as save_f:
    writer = csv.writer(save_f)
    writer.writerow(['name', 'sender', 'reciver', 'cc', 'title', 'body', 'keyword', 'lang'])
    # 当前目录路径  当前路径下所有子目录  当前路径下所有非目录子文件list 格式
    for root, dirs, files in os.walk(file_dir):
        for eml_data_path in files:
            filepath = os.path.join(file_dir, eml_data_path)
            # 读取每个eml文件
            name = eml_data_path.split('.')[0]
            with open(filepath,'rb') as f:
                a=f.read()
            eml = eml_parser.eml_parser.decode_email_b(a,True,True)
            # 提取数据
            for i in eml["body"]:
                try:
                    if i['content_type'] == 'text/plain':
                        body = i['content']
                        break
                    elif i['content_type'] == 'text/html':
                        soup = BeautifulSoup(i['content'], 'lxml')
                        p_data =soup.find_all('p')
                        ree = []
                        for i in p_data:
                            res = i.get_text()
                            ree.append(res)
                        body = ''.join(ree)
                except Exception as e:
                    body = i["content"].replace('\r\n','')   # 正文
            title = eml["header"]["subject"]    # 标题
            reciver = ','.join(eml["header"]["to"])   # 收
            sender = eml["header"]["from"]   # 发
            # 加抄送
            try:
                cc = eml["header"]["cc"]
            except Exception as e:
                cc=''
            # 拼接查看已知关键词命中情况
            key = ['key1','key2','key3','key4']
            aa = f'{reciver},{sender},{cc}'
            for i in keywords:
                if re.match(aa, i):
                    key.append(i)
            # 识别语言类型
            lang = detect(body)    # detect函数是中英文类型识别函数
            # 写入csv
            line = [name, sender, reciver, cc, title, body, key, lang]
            writer.writerow(line)

