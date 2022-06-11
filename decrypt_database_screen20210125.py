import os,sys
import time
from os.path import exists

import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
import codecs
import base64
from urllib.parse import urlparse
import  getopt,shutil

sys.path.append(os.path.abspath('/wfd_batch_cloud'))
from core.encryption.encryption_aes1 import HandleAES
from core.storage.tableManage import tableEngine, urlContent, contentJudgeResult, htmlContent,htmlScreenshot


def copyfile(infile,outfile):
    ''' 实现复制文件的功能

    Args:
        infile: 待复制的文件
        outfile: 复制的目标路径

    Returns:

    '''
    try:
        shutil.copy(infile,outfile)
    except Exception as e:
        print('''Can't copy this file :{}'''.format(e))
        return


def decypt_urlcontent():
    '''提取数据库中的url、文本内容、判读结果，写入到excel中，
       并且保存高清截图到当前路径的short_screen路径
       Args:
           无
       Returns:
    '''

    #数据库连接
    engine = tableEngine
    dbSession = sessionmaker(bind=engine)
    session = dbSession()
    ##判断结果关联内容表

    instances1 = (session.query(contentJudgeResult.label.label('typ'), contentJudgeResult.judge_time.label('Tim'),
                                contentJudgeResult.html_content_id, htmlContent.url_id,htmlContent.html_content).
                  join(htmlContent, htmlContent.html_content_id == contentJudgeResult.html_content_id).
                  filter(and_(contentJudgeResult.label != '10105', contentJudgeResult.operater == 'classify'\
                              ,contentJudgeResult.bak1 !='true')).
                  subquery())


    ##判断结果关联url表，获得url值
    instances1_1 = session.query(urlContent.url_id,urlContent.url_value,instances1.c.typ,  instances1.c.Tim,instances1.c.html_content ,instances1.c.html_content_id). \
        join(urlContent, instances1.c.url_id == urlContent.url_id).subquery()
    ###拿截图
    instances2=session.query(instances1_1.c.url_id,instances1_1.c.url_value,instances1_1.c.typ,  instances1_1.c.Tim,instances1_1.c.html_content,htmlScreenshot.short_screenshot_base64 ,\
                         htmlScreenshot.screenshot_id). outerjoin(htmlScreenshot, instances1_1.c.html_content_id == htmlScreenshot.html_content_id).all()
    session.close()
    if instances2:
        i=0
        df1 = pd.DataFrame(columns=['url_id','url', 'lable', 'time', 'content','screenshot_id'])
        for row in instances2:
            i=i+1
            url_id=row.url_id
            url=HandleAES.aes_decrypt(row.url_value)
            lable=row.typ
            tim=row.Tim
            #转为时间
            timeArray = time.localtime(int(tim))
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

            # 保存截图
            path = './short_screenshot'
            if not exists(path):
                os.mkdir(path)
            if row.screenshot_id:
                screenshot_id=row.screenshot_id
                try:
                    #copyfile('/wfd_batch_cloud/pics/{}.png'.format("".join(screenshot_id.split('-'))),path)
                    pass
                except Exception as e :
                    pass
            else:
                screenshot_id='none'
            # 解密内容
            content = HandleAES.aes_decrypt(row.html_content)
            df = pd.DataFrame({"url_id":[url_id],"url": [url], "lable": [lable], "time": [otherStyleTime], 'content': [content],'screenshot_id':[screenshot_id]},
                              index=[i])
            df1 = df1.append(df)
        with pd.ExcelWriter('./Decryptcontent_all.xlsx') as writer:
            df1.to_excel(writer, sheet_name="Decryptcontent",index=False)
        writer.close()

    else:
        print('result is none！')


def decypt_know_urlcontent():
    """
       提取路径下urls.txt中的url、文本内容、判读结果，写入到excel中，
       并且保存高清截图到当前路径的short_screen路径

       Args:
           无
       Returns:
    """

    # 数据库连接
    engine = tableEngine
    dbSession = sessionmaker(bind=engine)
    session = dbSession()

    with codecs.open('./urls.txt', 'r', 'utf-8') as infile:
        df1 = pd.DataFrame(columns=['url_id','url', 'lable', 'time', 'content','html_content_id','screenshot_id'])
        for line in infile.readlines():
            url=line.strip()
            print(url)
            #关联url_id
            row=session.query(urlContent.url_value,urlContent.url_id).filter(urlContent.url_value==HandleAES.aes_encrypt(url))\
                        .subquery()
            #关联content
            row1=session.query(row.c.url_id,row.c.url_value,htmlContent.html_content_id,htmlContent.html_content,htmlContent.capture_time)\
                         .join(htmlContent,row.c.url_id==htmlContent.url_id).subquery()
            #关联判断结果
            row11 = session.query(row1.c.url_id, row1.c.url_value, row1.c.html_content_id, row1.c.html_content,
                                 row1.c.capture_time, \
                                 contentJudgeResult.label,contentJudgeResult.judge_time).join(contentJudgeResult,
                                                                and_(contentJudgeResult.html_content_id == \
                                                                     row1.c.html_content_id,contentJudgeResult.bak1=='false' )).subquery()
            #关联截图
            row2 = session.query(row11.c.url_id, row11.c.url_value, row11.c.html_content_id, row11.c.html_content,
                row11.c.capture_time,row11.c.judge_time,row11.c.label, htmlScreenshot.short_screenshot_base64,htmlScreenshot.screenshot_id).\
                outerjoin(htmlScreenshot, htmlScreenshot.html_content_id == row11.c.html_content_id).\
                order_by(row11.c.judge_time.desc()).first()


            if row2:
                i = 0
                row=row2
                i = i + 1
                url_id=row.url_id
                url = HandleAES.aes_decrypt(row.url_value)
                lable = row.label
                html_content_id=row.html_content_id
                tim = row.judge_time
                # 转为时间
                timeArray = time.localtime(int(tim))
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                # 解密内容
                content = HandleAES.aes_decrypt(row.html_content)

                # 保存截图
                path = './short_screenshot'
                if not exists(path):
                    os.mkdir(path)
                if row.screenshot_id:
                    screenshot_id = row.screenshot_id
                    try:
                        pass
                        #copyfile('/wfd_batch_cloud/pics/{}.png'.format("".join(screenshot_id.split('-'))), path)
                    except Exception as e:
                        pass
                else:
                    screenshot_id = 'screen error'
                df = pd.DataFrame(
                    {"url_id": [url_id], "url": [url], "lable": [lable], "time": [otherStyleTime], 'content': [content],
                     'html_content_id': [html_content_id],'screenshot_id':[screenshot_id]},
                    index=[i])
                df1 = df1.append(df)
                # print(df1)
            else:
                df1=df1
                print('{}未查询到'.format(url))
                pass
    print(df1)
    with pd.ExcelWriter('./Decryptcontent_know.xlsx') as writer:
        df1.to_excel(writer, sheet_name="knowurl", index=False)
    writer.close()



if __name__ == '__main__':
    if sys.argv[1] == 'all':
        decypt_urlcontent()
        decypt_know_urlcontent()
    elif sys.argv[1] == '2':
        decypt_know_urlcontent()
    elif sys.argv[1] == '1':
        decypt_urlcontent()

