import requests
import pymysql
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
# chrome_driver = "C:\Program Files\Google\Chrome\Application\chromedriver.exe"
# todo 自己的path
chrome_driver="E:\Anaconda\chromedriver.exe"
driver = webdriver.Chrome(chrome_driver, chrome_options=options)


def create_db():
    db = pymysql.connect(host='113.31.114.239', user='root', password='123456', port=53377)
    cursor = db.cursor()
    cursor.execute("Create Database If Not Exists test_db Character Set UTF8")
    db.close()


def create_table():
    db = pymysql.connect(host='113.31.114.239', user='root', password='123456', port=53377, db='test_db', autocommit=True)
    cursor = db.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS test_table(resource VARCHAR(255), cve_id VARCHAR(255) NOT NULL, ssv_id VARCHAR(255), submit_time VARCHAR(255),vul_level VARCHAR(255),vul_title VARCHAR(255),wea_poc VARCHAR(255),wea_range VARCHAR(255),wea_detail VARCHAR(255),wea_icon VARCHAR(255),wea_exp VARCHAR(255),PRIMARY KEY (ssv_id))'
    cursor.execute(sql)
    db.close()


def count_line():
    db = pymysql.connect(host='113.31.114.239', user='root', password='123456', port=53377, db='test_db', autocommit=True)
    sq = 'select count(*) from test_table'
    ss = pd.read_sql(sq, db)
    line = int((str(ss.values).replace('[', '')).replace(']', ''))
    return line


def data_insert(value, count):
    db = pymysql.connect(host='113.31.114.239', user='root', password='123456', port=53377, db='test_db')
    cursor = db.cursor()
    sql = "INSERT ignore INTO test_table(resource, cve_id, ssv_id, submit_time, vul_level, vul_title, wea_poc, wea_range, wea_detail, wea_icon,wea_exp) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql, value)
        db.commit()
        print('第{}条数据插入完成'.format(count))
    except:
        db.rollback()
        print("第{}条数据插入数据失败".format(count))
    db.close()


def get_content():
    """
    获取当前浏览器页面的内容
    :return:
    """
    table_loc = (By.XPATH, '/html/body/div[2]/div/div/div/div/table')
    liTags = driver.find_element(*table_loc).find_elements(By.TAG_NAME, 'tr')
    count = 0
    for li in liTags:
        try:
            resource = 'https://www.seebug.org/'  # 获取来源
            cve_id = li.find_element_by_class_name('fa-id-card').get_attribute('data-original-title')
            ssv_id = li.find_element_by_tag_name('a').text
            submit_time = li.find_element_by_class_name('datetime').text
            vul_level = li.find_element_by_class_name('vul-level').get_attribute('data-original-title')  # 漏洞等级
            vul_title = li.find_element_by_class_name('vul-title').text  # 漏洞名称
            wea_poc = li.find_element_by_class_name('fa-rocket').get_attribute('data-original-title')  # 有无poc
            wea_range = li.find_element_by_class_name('fa-bullseye').get_attribute('data-original-title')  # 有无靶场
            wea_detail = li.find_element_by_class_name('fa-file-text-o').get_attribute(
                'data-original-title')  # 有无详情
            wea_icon = li.find_element_by_class_name('fa-signal').get_attribute('data-original-title')  # 有无图表
            wea_exp = '无exp'

            count += 1
            value = (resource, cve_id, ssv_id,submit_time, vul_level, vul_title, wea_poc, wea_range, wea_detail, wea_icon,wea_exp)
            print(value)
            data_insert(value, count)
        except:
            continue


def email(data_end, data_begin):
    number = '1115016718@qq.com'
    smtp = 'xolzrxgwjaoigdig'
    to = '1115016718@qq.com'  # 可以是非QQ的邮箱
    mer = MIMEMultipart()

    head = '''
       <p>日期：{}</p>
       <p>新增漏洞个数:{}</p>
   '''.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), data_end - data_begin)

    mer.attach(MIMEText(head, 'html', 'utf-8'))

    mer['Subject'] = '新增【知道创宇】漏洞信息'  # 邮件主题
    mer['From'] = number  # 发送人
    mer['To'] = to  # 接收人

    s = smtplib.SMTP_SSL('smtp.qq.com', 465)
    s.login(number, smtp)
    s.send_message(mer)  # 发送邮件
    s.quit()
    print('成功发送')


def main():
    count = 0
    while True:
        if driver.find_element_by_class_name('fa-chevron-right'):  # > 箭头存在的
            time.sleep(1)
            count += 1
            print("正在爬取第{}页:{}".format(count, driver.current_url))
            driver.find_element_by_class_name('fa-chevron-right').click()
            get_content()
            time.sleep(1)


if __name__ == '__main__':
    create_db()
    create_table()

    data_begin = count_line()
    print("运行之前---》数据库表目前存储条数:{}".format(data_begin))

    main()

    data_end = count_line()
    print("运行之后---》数据库表目前存储条数:{}".format(data_end))

    email(data_end, data_begin)
