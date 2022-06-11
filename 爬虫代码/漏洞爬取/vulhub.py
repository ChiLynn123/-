import requests
from bs4 import BeautifulSoup
import pymysql
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import time

# 建数据库
def create_db():
    db = pymysql.connect(host='113.31.114.239', user='root', password='123456', port=53377)
    cursor = db.cursor()
    cursor.execute("Create Database If Not Exists test_db2 Character Set UTF8")
    db.close()
# 建表
def create_table():
    db = pymysql.connect(host='113.31.114.239', user='root', password='123456', port=53377, db='test_db2', autocommit=True)
    cursor = db.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS test_table2(resource VARCHAR(255), id VARCHAR(255) NOT NULL,submit_time VARCHAR(255),vul_level VARCHAR(255),vul_title VARCHAR(255),chinese_data VARCHAR(255),explit_data VARCHAR(255),detail_data VARCHAR(255),software_data VARCHAR(255),analyzer_data VARCHAR(255),populator VARCHAR(255),PRIMARY KEY (id))'
    cursor.execute(sql)
    db.close()
# 统计行数
def count_line():
    db = pymysql.connect(host='113.31.114.239', user='root', password='123456', port=53377, db='test_db2',autocommit=True)
    sq = 'select count(*) from test_table2'
    ss = pd.read_sql(sq, db)
    line = int((str(ss.values).replace('[','')).replace(']',''))
    return line

# 数据插入
def data_insert(value, count):
    db = pymysql.connect(host='113.31.114.239', user='root', password='123456', port=53377, db='test_db2')
    cursor = db.cursor()
    sql = "INSERT ignore INTO test_table2(resource, id,submit_time,vul_level,vul_title,chinese_data,explit_data,detail_data,software_data,analyzer_data,populator) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql, value)
        db.commit()
        print('第{}条数据插入完成'.format(count))
    except:
        db.rollback()
        print("第{}条数据插入数据失败".format(count))
    db.close()

# get 网站文本信息
def get_html(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            #'Cookie': 'Cookie: __cdnuid_s=a38e6b496158001bc9e0729f75625c45; Hm_lvt_6b15558d6e6f640af728f65c4a5bf687=1645603517; __jsluid_s=ef0eb0b0bbf9107b287038f1e9908e1d; __cdn_clearance_s=1645851820.096|0|UkLjBz7LmFg4lN6ocMYHVPFKBxc%3D; __cdnuid_h=5c4461173a5389c1638e8553a4947721; __cdn_clearance=1645851852.689|0|ckpyaRiMLnLi8V%2Fz2PF%2Fuu8G7yw%3D; sessionid=04nya3m1m5zut5ugecrjkeva894rvszw; messages="889badfec532ed8825f6567f807a12b48c33f881$[[\"__json_message\"\0540\05425\054\"Login succeeded. Welcome\054 04ff6220153e.\"]]"; Hm_lpvt_6b15558d6e6f640af728f65c4a5bf687=1645851874'
            # 'Cookie': '__jsluid_s=ae810abd928efaf677c4890289307cf9; Hm_lvt_6b15558d6e6f640af728f65c4a5bf687=1645605185; __jsluid_h=394240af4b88872c57d4598cd33b9e61; sessionid=ff5moa2eycc9oqf5off2pbz44l9rzlmq; messages="9903a3a9a1c3dae059e57b0c5d99fe1daf67edb3$[[\"__json_message\"\0540\05425\054\"Login succeeded. Welcome\054 212720bef878.\"]]"; Hm_lpvt_6b15558d6e6f640af728f65c4a5bf687=1645670262; __jsl_clearance_s=1645673873.626|0|66uxA2XUgeGxK9guvlnAw6j3QvI%3D',
        }
        r = requests.get(url, headers=headers, timeout=60)
        return r.text
    except:
        return " ERROR "


def get_content(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    liTags = soup.find_all('tr')
    count = 0
    for li in liTags:
        try:
            resource = 'http://vulhub.org.cn/'  # 获取来源
            id = 'http://vulhub.org.cn/' + li.find('a')['href']  # 标识
            submit_time = li.find('td', attrs={'class': 'hidden-xs'}).text.strip()  # 提交时间
            vul_level = li.find('span', attrs={'class': 'grade'})['title'] # 漏洞等级
            vul_title = li.find_all('td')[3].text.strip() # 漏洞名称
            chinese_data = li.find('span', attrs={'class': 'chinese_True'})['title']  # 有无中文数据
            explit_data = li.find('span', attrs={'class': 'exploit_False'})['title']  # 漏洞利用代码
            detail_data = li.find('span', attrs={'class': 'details_True'})['title']  # 漏洞细节
            software_data = li.find('span', attrs={'class': 'software_False'})['title']  # 漏洞载体
            analyzer_data = li.find('span', attrs={'class': 'analyzer_False'})['title']  # 漏洞检测脚本
            populator = li.find_all('td')[5].text.strip() #人气

            count += 1
            value = (resource, id,submit_time,vul_level,vul_title,chinese_data,explit_data,detail_data,software_data,analyzer_data,populator)
            print(value)
            data_insert(value, count)
        except:
            continue
# 发送邮件
def email(data_end,data_begin):
    number = '1115016718@qq.com'
    smtp = 'xolzrxgwjaoigdig'
    to = '1115016718@qq.com'  # 可以是非QQ的邮箱
    mer = MIMEMultipart()

    head = '''
       <p>日期：{}</p>
       <p>新增漏洞个数:{}</p>
   '''.format( time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , data_end-data_begin)

    mer.attach(MIMEText(head, 'html', 'utf-8'))


    mer['Subject'] = '新增【vulhub】漏洞信息'  # 邮件主题
    mer['From'] = number  # 发送人
    mer['To'] = to  # 接收人

    s = smtplib.SMTP_SSL('smtp.qq.com', 465)
    s.login(number, smtp)
    s.send_message(mer)  # 发送邮件
    s.quit()
    print('成功发送')


def main(deep):
    url_list = []
    count = 0
    for i in range(0, deep):
        url_list.append('http://vulhub.org.cn/vulns/{}?view=global'.format(i+1))

    for url in url_list:
        count += 1
        print("正在爬取第{}|{}页:{}".format(count+1, len(url_list), url))
        print(get_content(url))
        time.sleep(10)


if __name__ == '__main__':
    create_db()
    create_table()

    data_begin = count_line()
    print("运行之前---》数据库表目前存储条数:{}".format(data_begin))

    deep = 5
    main(deep)

    data_end = count_line()
    print("运行之后---》数据库表目前存储条数:{}".format(data_end))

    email(data_end, data_begin)

